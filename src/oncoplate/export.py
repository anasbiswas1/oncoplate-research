"""Tensor export and parity evaluation. Export is not a public-release permission."""
from __future__ import annotations
from pathlib import Path
import time
import numpy as np
import torch
from torch import nn
from .training import load_predictor,seed_all
from .vision import backbone
from .io import write_json,sha256


class ExportModel(nn.Module):
    def __init__(self,model,temperature=1.):super().__init__();self.model=model;self.temperature=temperature
    def forward(self,x):return torch.sigmoid(self.model(x)/self.temperature)


def image_model_for_run(run_dir):
    model,spec,schema=load_predictor(run_dir,"cpu")
    if spec.regime=="frozen":
        seed_all(spec.seed)
        encoder,_=backbone(spec.backbone,pretrained=spec.pretrained,revision=spec.revision)
        model=nn.Sequential(encoder,model)
    return model.eval(),spec,schema


def export_run(run_dir,output,temperature=1.,onnx=False):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    model,spec,schema=image_model_for_run(run_dir);wrapped=ExportModel(model,temperature).eval()
    x=torch.zeros(1,3,spec.image_size,spec.image_size)
    with torch.no_grad():
        traced=torch.jit.trace(wrapped,x,check_trace=True)
        traced.save(str(output/"predictor.torchscript.pt"))
        expected=wrapped(x);actual=traced(x)
    error=float((expected-actual).abs().max())
    if error>1e-5:raise RuntimeError("TorchScript parity failure")
    files={"torchscript":sha256(output/"predictor.torchscript.pt")}
    if onnx:
        import onnxruntime as ort
        torch.onnx.export(wrapped,x,str(output/"predictor.onnx"),input_names=["image"],output_names=["probabilities"],opset_version=18,
                          dynamic_axes={"image":{0:"batch"},"probabilities":{0:"batch"}},dynamo=False)
        session=ort.InferenceSession(str(output/"predictor.onnx"),providers=["CPUExecutionProvider"])
        y=session.run(None,{"image":x.numpy()})[0]
        onnx_error=float(np.max(np.abs(y-expected.numpy())))
        if onnx_error>1e-4:raise RuntimeError("ONNX parity failure")
        files["onnx"]=sha256(output/"predictor.onnx")
    contract={"research_only":True,"clinical_validation":False,"image_size":spec.image_size,"preprocessing":"letterbox_imagenet_v1",
       "target_schema":schema,"temperature":temperature,"files":files,"zero_input_parity_error":error,
       "limitation":"This exports the visual predictor only. Source ledger, PCSI selector and reviewed renderer must remain in the full app pipeline; retest on real locked cases."}
    write_json(output/"export_contract.json",contract)
    return contract


def benchmark_export(path,inputs,repeats=20):
    model=torch.jit.load(str(path),map_location="cpu").eval();x=torch.as_tensor(inputs,dtype=torch.float32)
    timings=[]
    with torch.inference_mode():
        for _ in range(3):model(x)
        for _ in range(repeats):
            start=time.perf_counter();y=model(x);timings.append((time.perf_counter()-start)*1000)
    return {"latency_p50_ms":float(np.median(timings)),"latency_p95_ms":float(np.quantile(timings,.95)),"batch_size":len(x),"outputs":y.numpy()}


def quantize_frozen_head(run_dir,output,features):
    model,spec,schema=load_predictor(run_dir,"cpu")
    if spec.regime!="frozen":raise ValueError("This ablation quantises a frozen-feature head only; not an entire CNN/VLM")
    q=torch.ao.quantization.quantize_dynamic(model,{nn.Linear},dtype=torch.qint8)
    x=torch.as_tensor(features,dtype=torch.float32)
    with torch.inference_mode():a=model(x).numpy();b=q(x).numpy()
    # Serialised TorchScript avoids pretending a quantised state is loadable as an FP32 head.
    traced=torch.jit.trace(q,x[:1]);Path(output).parent.mkdir(parents=True,exist_ok=True);traced.save(str(output))
    return {"scope":"head_only_dynamic_int8","max_abs_logit_difference":float(np.max(np.abs(a-b))),"mean_abs_logit_difference":float(np.mean(np.abs(a-b))),"must_recalibrate_and_retest":True}
