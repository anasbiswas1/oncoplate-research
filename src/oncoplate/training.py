"""Resumable masked multi-label training; no test-based checkpoint selection."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from pathlib import Path
import os,random,tempfile,time,copy
from itertools import islice
import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader,TensorDataset,Subset
from .io import digest,write_json,read_json,atomic_npz,write_table,sha256
from .vision import backbone,ImageDataset,Letterbox,feature_cache,resolve_dino_revision
from .targets import align_targets


@dataclass
class TrainSpec:
    backbone: str = "resnet50"
    regime: str = "frozen"
    head: str = "independent"
    seed: int = 0
    epochs: int = 100
    patience: int = 10
    batch_size: int = 128
    effective_batch_size: int = 128
    lr: float = .001
    weight_decay: float = .0001
    image_size: int = 224
    workers: int = 0
    pretrained: bool = True
    hidden: int = 0
    precision: str = "auto"
    checkpoint_every_batches: int = 100
    revision: str | None = None

    @property
    def run_id(self):return f"{self.backbone}_{self.regime}_{self.head}_s{self.seed}"


def seed_all(seed,deterministic=True):
    random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
    if torch.cuda.is_available():torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark=False
    if deterministic:
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG",":4096:8")
        torch.use_deterministic_algorithms(True,warn_only=False)


def masked_bce(logits,y,mask):
    element=nn.functional.binary_cross_entropy_with_logits(logits,y,reduction="none")
    n=mask.sum()
    if n<=0:raise ValueError("Batch has no observed target entries")
    return (element*mask).sum()/n


class Head(nn.Module):
    def __init__(self,n_features,n_outputs,mean=None,std=None,hidden=0):
        super().__init__()
        self.register_buffer("mean",torch.as_tensor(np.zeros(n_features) if mean is None else mean,dtype=torch.float32))
        self.register_buffer("std",torch.as_tensor(np.ones(n_features) if std is None else std,dtype=torch.float32).clamp_min(1e-6))
        self.net=(nn.Sequential(nn.Linear(n_features,hidden),nn.ReLU(),nn.Dropout(.1),nn.Linear(hidden,n_outputs)) if hidden else nn.Linear(n_features,n_outputs))
    def forward(self,x):return self.net((x-self.mean)/self.std)


class FullPredictor(nn.Module):
    def __init__(self,encoder,n_features,n_outputs,hidden=0):
        super().__init__();self.encoder=encoder;self.head=Head(n_features,n_outputs,hidden=hidden)
    def forward(self,x):return self.head(self.encoder(x))


def _atomic_torch(path,state):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=path.parent,suffix=".pt");os.close(fd)
    try:torch.save(state,tmp);os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def _rng():return {"torch":torch.get_rng_state(),"numpy":np.random.get_state(),"python":random.getstate(),"cuda":torch.cuda.get_rng_state_all() if torch.cuda.is_available() else []}


def _setrng(r):
    torch.set_rng_state(r["torch"]);np.random.set_state(r["numpy"]);random.setstate(r["python"])
    if torch.cuda.is_available() and r["cuda"]:torch.cuda.set_rng_state_all(r["cuda"])


def _load_owned(path,device):
    # Only locally produced checkpoints in the current run directory are accepted here.
    return torch.load(path,map_location=device,weights_only=False)


def fit(model,train_ds,val_ds,spec,out,identity,*,device=None):
    """Resume from optimizer boundaries, including an incomplete epoch.
    Inputs use deterministic transforms; loader RNG is isolated from model dropout RNG.
    """
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    device=device or ("cuda" if torch.cuda.is_available() else "cpu")
    config={"spec":asdict(spec),"identity":identity}
    signature=digest(config)
    if (out/"run.json").exists() and read_json(out/"run.json")["signature"]!=signature:
        raise RuntimeError("Run configuration/data differ. Choose a new run ID; do not reuse checkpoints.")
    write_json(out/"run.json",{"signature":signature,**config})
    model.to(device);optimizer=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=spec.lr,weight_decay=spec.weight_decay)
    accumulation=max(1,int(np.ceil(spec.effective_batch_size/spec.batch_size)))
    amp_enabled=device.startswith("cuda") and spec.precision!="float32"
    amp_dtype=torch.bfloat16 if amp_enabled and torch.cuda.is_bf16_supported() else torch.float16
    scaler=torch.amp.GradScaler("cuda",enabled=amp_enabled and amp_dtype==torch.float16)
    start_epoch=0;resume_batch=0;best=float("inf");bad=0;history=[]
    latest=out/"last.pt";best_path=out/"best.pt"
    if latest.exists():
        state=_load_owned(latest,device)
        if state["signature"]!=signature:raise RuntimeError("Checkpoint signature mismatch")
        model.load_state_dict(state["model"]);optimizer.load_state_dict(state["optimizer"]);scaler.load_state_dict(state["scaler"])
        start_epoch=state["epoch"];resume_batch=state["next_batch"];best=state["best"];bad=state["bad"];history=state["history"]
        _setrng(state["rng"])
    def save(epoch,next_batch):
        _atomic_torch(latest,{"signature":signature,"model":model.state_dict(),"optimizer":optimizer.state_dict(),"scaler":scaler.state_dict(),
                             "epoch":epoch,"next_batch":next_batch,"best":best,"bad":bad,"history":history,"rng":_rng()})
    for epoch in range(start_epoch,spec.epochs):
        if bad>=spec.patience:break
        order=np.random.default_rng(spec.seed+epoch*1009).permutation(len(train_ds))
        batches=[order[i:i+spec.batch_size] for i in range(0,len(order),spec.batch_size)]
        model.train();optimizer.zero_grad(set_to_none=True)
        started=time.time()
        # One loader per epoch: avoid repeatedly starting worker processes per minibatch.
        remaining = order[resume_batch * spec.batch_size:]
        loader = DataLoader(Subset(train_ds, remaining.tolist()), batch_size=spec.batch_size,
                            shuffle=False, num_workers=spec.workers,
                            generator=torch.Generator().manual_seed(spec.seed+epoch),
                            pin_memory=device.startswith("cuda"))
        iterator = iter(loader)
        step = resume_batch
        while True:
            batch_tensors = list(islice(iterator, accumulation))
            if not batch_tensors:
                break
            denom = sum(float(mask.sum()) for _,_,mask in batch_tensors)
            if denom > 0:
                for x,y,mask in batch_tensors:
                    x=x.to(device);y=y.to(device);mask=mask.to(device)
                    with torch.autocast(device_type="cuda" if device.startswith("cuda") else "cpu",enabled=amp_enabled,dtype=amp_dtype):
                        logits=model(x)
                        loss=(nn.functional.binary_cross_entropy_with_logits(logits,y,reduction="none")*mask).sum()/denom
                    scaler.scale(loss).backward()
                scaler.unscale_(optimizer);nn.utils.clip_grad_norm_(model.parameters(),1.0)
                scaler.step(optimizer);scaler.update();optimizer.zero_grad(set_to_none=True)
            step += len(batch_tensors)
            if step % max(1,spec.checkpoint_every_batches) == 0:
                save(epoch,step)
        resume_batch=0
        logits,yy,mm=predict_dataset(model,val_ds,spec.batch_size,device)
        val=float(np.sum((np.logaddexp(0,logits)-yy*logits)*mm)/max(mm.sum(),1))
        if not np.isfinite(val):raise ValueError("Nonfinite validation loss")
        improved=val<best-1e-8
        if improved:
            best=val;bad=0;_atomic_torch(best_path,{"model":model.state_dict(),"signature":signature,"epoch":epoch,"validation_loss":val})
        else:bad+=1
        history.append({"epoch":epoch,"validation_loss":val,"seconds":time.time()-started,"best":improved})
        write_table(out/"history.csv",pd.DataFrame(history));save(epoch+1,0)
        print(f"{spec.run_id} epoch={epoch+1} validation_bce={val:.5f} best={best:.5f}")
    if not best_path.exists():raise RuntimeError("No trained checkpoint")
    model.load_state_dict(_load_owned(best_path,device)["model"])
    write_json(out/"complete.json",{"signature":signature,"epochs_completed":len(history),"best_validation_loss":best,"best_sha256":sha256(best_path)})
    return model


def predict_dataset(model,ds,batch_size=64,device=None):
    device=device or next(model.parameters()).device
    model.eval();outputs=[];ys=[];masks=[]
    with torch.inference_mode():
        for x,y,m in DataLoader(ds,batch_size=batch_size,shuffle=False,num_workers=0,
                                generator=torch.Generator().manual_seed(0)):
            outputs.append(model(x.to(device)).float().cpu().numpy());ys.append(y.numpy());masks.append(m.numpy())
    if not outputs:raise ValueError("Empty prediction partition")
    return np.concatenate(outputs),np.concatenate(ys),np.concatenate(masks)


def train_predictor(records,targets,spec,run_dir,feature_root,*,fit_ids=None,val_ids=None,device=None):
    seed_all(spec.seed)
    fit_ids=set(fit_ids or records.loc[records.split=="fit","record_id"])
    val_ids=set(val_ids or records.loc[records.split=="validation","record_id"])
    if fit_ids&val_ids:raise ValueError("Fit/validation overlap")
    fr=records[records.record_id.isin(fit_ids)].copy();vr=records[records.record_id.isin(val_ids)].copy()
    if not len(fr) or not len(vr):raise ValueError("Empty fit or validation set")
    if set(fr.group_id)&set(vr.group_id):raise ValueError("Group leakage into early stopping")
    fy,fm=align_targets(targets,fr.record_id);vy,vm=align_targets(targets,vr.record_id)
    # Unlabelled rows are not trainable. They remain in later coverage denominators.
    keep=fm.sum(1)>0;fr=fr.iloc[np.where(keep)[0]];fy,fm=fy[keep],fm[keep]
    vkeep=vm.sum(1)>0;vr=vr.iloc[np.where(vkeep)[0]];vy,vm=vy[vkeep],vm[vkeep]
    if not len(fr) or not len(vr):raise ValueError("No observed fitting/validation labels")
    if spec.backbone=="dinov2_vits14" and spec.pretrained and not spec.revision:
        spec.revision=resolve_dino_revision(Path(feature_root)/"dinov2_snapshot.json")
    encoder,nf=backbone(spec.backbone,pretrained=spec.pretrained,revision=spec.revision)
    if spec.regime=="frozen":
        both=pd.concat([fr,vr],ignore_index=True)
        identity={"backbone":spec.backbone,"pretrained":spec.pretrained,"revision":spec.revision}
        # Random tiny-demo features are seed-dependent; pretrained fixed features are not.
        if not spec.pretrained:identity["random_seed"]=spec.seed
        key=digest({"identity":identity,"ids":both.record_id.tolist(),"size":spec.image_size})[:20]
        features,_=feature_cache(both,encoder,Path(feature_root)/key,model_identity=identity,size=spec.image_size,batch_size=spec.batch_size,workers=spec.workers,device=device)
        f=features[:len(fr)];v=features[len(fr):]
        model=Head(nf,fy.shape[1],f.mean(0),f.std(0),spec.hidden)
        tr=TensorDataset(torch.tensor(f),torch.tensor(fy),torch.tensor(fm));va=TensorDataset(torch.tensor(v),torch.tensor(vy),torch.tensor(vm))
    elif spec.regime=="finetune":
        model=FullPredictor(encoder,nf,fy.shape[1],spec.hidden)
        tr=ImageDataset(fr,Letterbox(spec.image_size),fy,fm);va=ImageDataset(vr,Letterbox(spec.image_size),vy,vm)
    else:raise ValueError("Unknown regime")
    identity={"fit_ids":sorted(fr.record_id),"validation_ids":sorted(vr.record_id),"schema_hash":targets["schema"]["schema_hash"],
              "fitting_target_hash":digest([fy.tolist(),fm.tolist()]),"validation_target_hash":digest([vy.tolist(),vm.tolist()]),
              "image_manifest_hash":digest(pd.concat([fr,vr])[["record_id","sha256"]].to_dict("records")),
              "software_hash":digest({f.name:sha256(f) for f in Path(__file__).parent.glob("*.py")}),
              "torch_version":torch.__version__}
    trained=fit(model,tr,va,spec,run_dir,identity,device=device)
    logits,yy,mm=predict_dataset(trained,va,spec.batch_size,device)
    atomic_npz(Path(run_dir)/"validation_predictions.npz",ids=vr.record_id.to_numpy(dtype=str),logits=logits,y=yy,mask=mm)
    write_json(Path(run_dir)/"target_schema.json",targets["schema"])
    return {"run_dir":str(run_dir),"spec":asdict(spec),"validation_rows":len(vr)}


def load_predictor(run_dir,device="cpu"):
    run_dir=Path(run_dir);cfg=read_json(run_dir/"run.json");spec=TrainSpec(**cfg["spec"])
    schema=read_json(run_dir/"target_schema.json")
    state=_load_owned(run_dir/"best.pt",device)["model"]
    if spec.regime=="frozen":
        model=Head(len(state["mean"]),len(schema["labels"]),hidden=spec.hidden)
    else:
        encoder,nf=backbone(spec.backbone,pretrained=False,revision=spec.revision)
        model=FullPredictor(encoder,nf,len(schema["labels"]),spec.hidden)
    model.load_state_dict(state);return model.to(device).eval(),spec,schema


def predict_run(run_dir,records,targets,feature_root,device=None):
    device=device or ("cuda" if torch.cuda.is_available() else "cpu")
    model,spec,schema=load_predictor(run_dir,device)
    if schema["schema_hash"]!=targets["schema"]["schema_hash"]:raise ValueError("Prediction target schema differs")
    y,mask=align_targets(targets,records.record_id)
    if spec.regime=="frozen":
        seed_all(spec.seed)
        encoder,_=backbone(spec.backbone,pretrained=spec.pretrained,revision=spec.revision)
        identity={"backbone":spec.backbone,"pretrained":spec.pretrained,"revision":spec.revision}
        if not spec.pretrained:identity["random_seed"]=spec.seed
        key=digest({"identity":identity,"ids":records.record_id.tolist(),"size":spec.image_size})[:20]
        f,_=feature_cache(records,encoder,Path(feature_root)/key,model_identity=identity,size=spec.image_size,batch_size=spec.batch_size,device=device)
        ds=TensorDataset(torch.tensor(f),torch.tensor(y),torch.tensor(mask))
    else:ds=ImageDataset(records,Letterbox(spec.image_size),y,mask)
    logits,y,mask=predict_dataset(model,ds,spec.batch_size,device)
    return {"ids":records.record_id.to_numpy(dtype=str),"logits":logits,"y":y,"mask":mask}
