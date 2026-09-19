"""Full-frame transforms, explicit checkpoints, resumable feature shards."""
from __future__ import annotations
from pathlib import Path
import json,os,shutil
import numpy as np
from PIL import Image,ImageOps
import torch
from torch import nn
from torch.utils.data import Dataset,DataLoader
from .io import digest,write_json,read_json,atomic_npz,sha256


class Letterbox:
    def __init__(self,size=224,normalize=True):self.size=size;self.normalize=normalize
    def __call__(self,image):
        im=ImageOps.exif_transpose(image).convert("RGB")
        im=ImageOps.pad(im,(self.size,self.size),method=Image.Resampling.BICUBIC,color=(124,116,104))
        a=np.asarray(im,dtype=np.float32)/255.0
        t=torch.from_numpy(a.transpose(2,0,1).copy())
        if self.normalize:
            t=(t-torch.tensor([.485,.456,.406])[:,None,None])/torch.tensor([.229,.224,.225])[:,None,None]
        return t


class ImageDataset(Dataset):
    def __init__(self,records,transform,y=None,mask=None):
        self.records=records.reset_index(drop=True);self.transform=transform;self.y=y;self.mask=mask
    def __len__(self):return len(self.records)
    def __getitem__(self,i):
        row=self.records.iloc[i]
        with Image.open(row.image_path) as im:x=self.transform(im)
        if self.y is None:return x,str(row.record_id)
        return x,torch.tensor(self.y[i],dtype=torch.float32),torch.tensor(self.mask[i],dtype=torch.float32)


class DinoEncoder(nn.Module):
    def __init__(self,pretrained=True,revision=None):
        super().__init__()
        from transformers import Dinov2Model,Dinov2Config
        if pretrained:
            self.model=Dinov2Model.from_pretrained("facebook/dinov2-small",revision=revision)
        else:
            self.model=Dinov2Model(Dinov2Config(hidden_size=384,num_hidden_layers=12,num_attention_heads=6,intermediate_size=1536))
    def forward(self,x):return self.model(pixel_values=x).last_hidden_state[:,0]


def backbone(name,*,pretrained=True,revision=None):
    if name=="tiny_demo":
        if pretrained:raise ValueError("Synthetic demo encoder has no pretrained checkpoint")
        return nn.Sequential(nn.Conv2d(3,8,3,padding=1),nn.ReLU(),nn.AdaptiveAvgPool2d(1),nn.Flatten()),8
    from torchvision import models
    if name=="resnet50":
        model=models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2 if pretrained else None)
        model.fc=nn.Identity();return model,2048
    if name=="convnext_tiny":
        model=models.convnext_tiny(weights=models.ConvNeXt_Tiny_Weights.IMAGENET1K_V1 if pretrained else None)
        model.classifier[-1]=nn.Identity();return model,768
    if name=="dinov2_vits14":return DinoEncoder(pretrained,revision),384
    raise ValueError(f"Unknown backbone {name}")


def resolve_dino_revision(lock_file):
    p=Path(lock_file)
    if p.exists():return read_json(p)["revision"]
    from huggingface_hub import model_info
    revision=model_info("facebook/dinov2-small").sha
    if not revision:raise RuntimeError("Cannot pin DINO snapshot")
    write_json(p,{"model_id":"facebook/dinov2-small","revision":revision})
    return revision


def feature_cache(records,encoder,cache_dir,*,model_identity,size=224,batch_size=32,workers=0,device=None,shard_size=512):
    cache_dir=Path(cache_dir);cache_dir.mkdir(parents=True,exist_ok=True)
    device=device or ("cuda" if torch.cuda.is_available() else "cpu")
    encoder=encoder.to(device).eval()
    for p in encoder.parameters():p.requires_grad_(False)
    ids=records.record_id.astype(str).tolist()
    # No source/label fields enter the feature key. Image identities and transform do.
    key=digest({"images":records[["record_id","sha256"]].to_dict("records"),"model":model_identity,"size":size,"transform":"letterbox_imagenet_v1"})
    meta=cache_dir/"manifest.json"
    if meta.exists() and read_json(meta)["cache_key"]!=key:raise RuntimeError("Feature cache identity mismatch; use a new cache directory")
    write_json(meta,{"cache_key":key,"model":model_identity,"rows":len(records),"size":size})
    chunks=[];outids=[]
    for start in range(0,len(records),shard_size):
        part=records.iloc[start:start+shard_size]
        dest=cache_dir/f"shard_{start:08d}.npz"
        if dest.exists():
            with np.load(dest,allow_pickle=False) as z:
                if z["ids"].tolist()!=part.record_id.astype(str).tolist():raise RuntimeError("Shard alignment mismatch")
                features=z["features"];gotids=z["ids"]
        else:
            loader=DataLoader(ImageDataset(part,Letterbox(size)),batch_size=batch_size,shuffle=False,num_workers=workers,pin_memory=device.startswith("cuda"))
            batches=[];gotids=[]
            with torch.inference_mode():
                for x,iids in loader:
                    try:f=encoder(x.to(device)).float().cpu().numpy()
                    except torch.cuda.OutOfMemoryError as e:
                        raise RuntimeError("Feature OOM: rerun this notebook with a smaller batch_size. Completed shards are retained.") from e
                    if not np.isfinite(f).all():raise ValueError("Nonfinite features")
                    batches.append(f);gotids.extend(iids)
            features=np.concatenate(batches);gotids=np.asarray(gotids,dtype=str)
            atomic_npz(dest,ids=gotids,features=features)
        chunks.append(features);outids.extend(list(gotids))
    if outids!=ids:raise RuntimeError("Feature order mismatch")
    return np.concatenate(chunks),np.asarray(outids,dtype=str)
