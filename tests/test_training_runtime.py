import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import torch
from torch.utils.data import TensorDataset
from oncoplate.training import Head,TrainSpec,fit,seed_all,predict_dataset
from oncoplate.vision import backbone,Letterbox
from oncoplate.external import nutrition5k_metadata
from oncoplate.clarification import replay_answer
from oncoplate.multimodal import parse_vlm_json


def test_interrupted_training_resumes_exactly(tmp_path,monkeypatch):
    import oncoplate.training as tr
    torch.set_num_threads(2)
    x=torch.arange(48,dtype=torch.float32).reshape(16,3)/48;y=(x[:,:2]>.3).float();m=torch.ones_like(y)
    ds=TensorDataset(x,y,m);spec=TrainSpec(backbone='tiny_demo',epochs=3,batch_size=4,effective_batch_size=8,checkpoint_every_batches=2,hidden=4,pretrained=False,workers=0)
    seed_all(123);a=Head(3,2,hidden=4);fit(a,ds,ds,spec,tmp_path/'a',{'fixture':True},device='cpu')
    expected=predict_dataset(a,ds,4,'cpu')[0]
    save=tr._atomic_torch;calls=0
    def interrupted(path,state):
        nonlocal calls
        save(path,state)
        if Path(path).name=='last.pt':
            calls+=1
            if calls==1:raise InterruptedError('simulated runtime disconnect after checkpoint')
    seed_all(123);b=Head(3,2,hidden=4)
    monkeypatch.setattr(tr,'_atomic_torch',interrupted)
    with pytest.raises(InterruptedError):fit(b,ds,ds,spec,tmp_path/'b',{'fixture':True},device='cpu')
    monkeypatch.setattr(tr,'_atomic_torch',save)
    seed_all(123);b=Head(3,2,hidden=4);fit(b,ds,ds,spec,tmp_path/'b',{'fixture':True},device='cpu')
    assert np.array_equal(expected,predict_dataset(b,ds,4,'cpu')[0])

def test_changed_run_identity_refused(tmp_path):
    x=torch.rand(8,3);ds=TensorDataset(x,torch.ones(8,1),torch.ones(8,1));spec=TrainSpec(epochs=1,batch_size=4,pretrained=False)
    fit(Head(3,1),ds,ds,spec,tmp_path,{'data':'v1'},device='cpu')
    with pytest.raises(RuntimeError):fit(Head(3,1),ds,ds,spec,tmp_path,{'data':'v2'},device='cpu')

@pytest.mark.parametrize('name,dim',[('resnet50',2048),('convnext_tiny',768)])
def test_torchvision_random_weight_forward_no_download(name,dim):
    # Tests architecture interface ONLY; these weights are never a research pretrained model.
    torch.set_num_threads(2);m,n=backbone(name,pretrained=False);m.eval()
    with torch.inference_mode():v=m(torch.zeros(1,3,224,224))
    assert v.shape==(1,dim) and n==dim

def test_nutrition_blocks(tmp_path):
    f=tmp_path/'m.csv';f.write_text('dish_1,10,20,1,2,3,ingr_0000000001,apple,20,10,0,2,0\n')
    d,i=nutrition5k_metadata(f);assert len(d)==1 and len(i)==1

def test_nutrition_explicit_count(tmp_path):
    f=tmp_path/'m.csv';f.write_text('dish_1,10,20,1,2,3,1,ingr_0000000001,apple,20,10,0,2,0\n')
    d,i=nutrition5k_metadata(f);assert len(i)==1

def test_unknown_answer_not_invented():
    a=replay_answer([], 'r','ingredient_panel');assert a['available'] is False and a['value']=='unknown'


def test_vlm_bad_fields_rejected():
    with pytest.raises(ValueError):parse_vlm_json('{"cancer_risk":0.7}', ['category'])

def test_vlm_json_values_checked():
    with pytest.raises(ValueError):parse_vlm_json('{"items":[{"category":"unknown_word"}]}',['category'],{'category':['meat']})

def test_vlm_unknown_explicit_null():
    assert parse_vlm_json('{"items":[{"category":null}]}',['category'])['items'][0]['category'] is None


def test_colab_api_research_contract(tmp_path):
    from oncoplate.export import ExportModel
    from oncoplate.api import create_app
    from oncoplate.io import write_json,sha256
    from oncoplate.targets import label_key
    from fastapi.testclient import TestClient
    from PIL import Image
    import io
    model=torch.nn.Sequential(torch.nn.AdaptiveAvgPool2d(1),torch.nn.Flatten(),torch.nn.Linear(3,1),torch.nn.Sigmoid()).eval()
    torch.jit.trace(model,torch.zeros(1,3,32,32)).save(str(tmp_path/'predictor.torchscript.pt'))
    write_json(tmp_path/'export_contract.json',{'image_size':32,'target_schema':{'labels':[label_key(['category'],['fixture'])]},'files':{'torchscript':sha256(tmp_path/'predictor.torchscript.pt')}})
    app=create_app(tmp_path);buf=io.BytesIO();Image.new('RGB',(32,32)).save(buf,format='PNG')
    with TestClient(app) as client:
        assert client.get('/health').json()['research_only'] is True
        result=client.post('/research/predict',files={'image':('fixture.png',buf.getvalue(),'image/png')})
        assert result.status_code==200
        obj=result.json();assert obj['research_only'] and obj['retained_image'] is False
        assert 'cancer_risk' not in obj and obj['output_scope'].startswith('record_presence')
        assert client.get('/').status_code==200


def test_finetune_updates_encoder_parameters(tmp_path):
    from oncoplate.training import FullPredictor
    torch.set_num_threads(2);seed_all(18)
    encoder,n=backbone('tiny_demo',pretrained=False)
    model=FullPredictor(encoder,n,2)
    before={k:v.detach().clone() for k,v in model.encoder.state_dict().items()}
    x=torch.rand(12,3,32,32);y=torch.stack([torch.arange(12)%2,1-torch.arange(12)%2],dim=1).float()
    ds=TensorDataset(x,y,torch.ones_like(y))
    spec=TrainSpec(backbone='tiny_demo',regime='finetune',epochs=2,batch_size=4,effective_batch_size=8,pretrained=False,lr=.01,image_size=32)
    fit(model,ds,ds,spec,tmp_path,{'fixture':'finetune_cpu'},device='cpu')
    assert any(not torch.equal(v,model.encoder.state_dict()[k]) for k,v in before.items())
    assert predict_dataset(model,ds,4,'cpu')[0].shape==(12,2)
