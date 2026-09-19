"""Notebook-facing orchestration with explicit artefacts and state transitions."""
from __future__ import annotations
import copy,itertools,json
from pathlib import Path
import numpy as np
import pandas as pd
from .config import paths,initialize
from .io import read_json,write_json,read_table,write_table,atomic_npz,sha256,digest
from .governance import require_gate,approval_report,verify_lock,record_unblinding
from .downloads import download,extract_zip
from .datasets import audit_foodnextdb,ingest_documented
from .splits import build_components,grouped_split,save_split,validate_split
from .targets import build_schema,make_targets,save_targets,load_targets
from .training import TrainSpec,train_predictor,predict_run
from .calibration import fit_temperature,fit_sigmoid,calibration_metrics,probabilities


def stage_public(cfg,download_missing=False):
    require_gate(cfg,"supervisor_execution");require_gate(cfg,"foodnextdb_research_terms")
    p=paths(cfg);archive=p["raw"]/"FoodNExtDB.zip"
    if not archive.exists():
        if not download_missing:raise FileNotFoundError(f"Download via notebook 01, or put the authorised ZIP at {archive}")
        download(cfg["data"]["foodnextdb_url"],archive,cfg["data"].get("foodnextdb_expected_sha256"))
    dest=p["local"]/"extracted"
    marker=dest/"extraction.json"
    if not marker.exists():extract_zip(archive,dest)
    else:
        # Archive hash is computed once per runtime by the caller, not for each minibatch.
        recorded=read_json(marker)
        if recorded["archive_sha256"]!=sha256(archive):raise RuntimeError("Staged data version differs from retained archive")
    return dest


def audit_public(cfg,download_missing=False):
    root=stage_public(cfg,download_missing)
    records,ann,report=audit_foodnextdb(root,paths(cfg)["prepared"])
    return report


def prepare_study(cfg,approved_edges=None):
    p=paths(cfg);records=read_table(p["prepared"]/"records.csv");ann=read_table(p["prepared"]/"annotations.csv")
    components=build_components(records,approved_edges)
    if "cohort" in components:
        cohort=components.cohort
        # Linked pilot or external material cannot silently leak into main study.
        if (components.groupby("group_id").cohort.nunique()>1).any():raise ValueError("Acquisition group shared between pilot/main/external cohorts")
        main=components[cohort.eq("main")].copy()
    else:main=components.copy()
    df=grouped_split(main,cfg["study"]["fractions"],cfg["study"]["split_seed"])
    if "cohort" in components:
        rest=components[~components.cohort.eq("main")].copy();rest["split"]=rest.cohort
        df=pd.concat([df,rest],ignore_index=True)
    save_split(df,p["prepared"]);write_table(p["prepared"]/"study_records.csv",df)
    # A documented focal-item task keeps only the predeclared item's annotations.
    if "focal_item_id" in df and df.focal_item_id.astype(str).str.len().gt(0).any():
        declared=df[["record_id","focal_item_id"]]
        ann=ann.merge(declared,on="record_id",how="left",validate="many_to_one")
        ann=ann[(ann.focal_item_id.eq("__record__"))|(ann.item_id.eq(ann.focal_item_id))].copy()
        if not set(df.record_id).issubset(set(ann.record_id)):
            raise ValueError("Some predeclared focal items have no corresponding annotation record")
    fit_ids=df.loc[df.split.eq("fit"),"record_id"]
    schemas={}
    for head,fs in (("independent",cfg["study"]["independent_fields"]),("joint",cfg["study"]["tuple_fields"])):
        schema=build_schema(ann,fit_ids,head,fs,cfg["data"]["minimum_fit_positive_support"])
        # New-benchmark joint head also predicts the additional atomic attributes needed by focal tasks.
        if head=="joint":
            supplemental=[f for f in cfg["study"]["independent_fields"] if f not in fs and f in ann and ann[f].astype(str).str.len().gt(0).any()]
            if supplemental:
                extra=build_schema(ann,fit_ids,"independent",supplemental)
                schema["labels"]+=extra["labels"];schema["group_bundles"]+=extra["group_bundles"];schema["fields"]+=supplemental
                schema["schema_hash"]=digest({k:v for k,v in schema.items() if k!="schema_hash"})
        targets=make_targets(df,ann,schema);save_targets(targets,p["prepared"]/f"targets_{head}");schemas[head]=schema
    write_json(p["prepared"]/"target_definition.json",{"schemas":schemas,"negative_semantics":"reviewer non-endorsement; unknowns masked","no_exposure_tiers":True})
    return df,schemas


def load_study(cfg,head="independent",stage_images=False):
    p=paths(cfg)
    records=read_table(p["prepared"]/"study_records.csv")
    if stage_images and len(records) and not Path(records.image_path.iloc[0]).exists():
        if cfg["study"]["dataset"]=="foodnextdb":stage_public(cfg)
        else:raise FileNotFoundError("Image paths no longer resolve. Restore the approved dataset to the same declared root.")
    validate_split(records)
    return records,load_targets(p["prepared"]/f"targets_{head}")


def spec_from_cfg(cfg,backbone="resnet50",regime="frozen",head="independent",seed=0):
    t=cfg["training"]
    return TrainSpec(backbone=backbone,regime=regime,head=head,seed=seed,epochs=t["head_epochs"] if regime=="frozen" else t["max_epochs"],
      patience=t["patience"],batch_size=t["head_batch_size"] if regime=="frozen" else t["batch_size"],effective_batch_size=t["effective_batch_size"],
      lr=t["head_lr"] if regime=="frozen" else t["finetune_lr"],weight_decay=t["weight_decay"],image_size=t["image_size"],workers=t["num_workers"],
      pretrained=t["pretrained"],hidden=256 if t["frozen_head"]=="mlp" else 0,precision=t["precision"],checkpoint_every_batches=t["checkpoint_every_batches"])


def run_training(cfg,spec,device=None):
    require_gate(cfg,"supervisor_execution")
    records,targets=load_study(cfg,spec.head,stage_images=True);p=paths(cfg)
    result=train_predictor(records,targets,spec,p["runs"]/spec.run_id,p["features"],device=device)
    return result


def grid_manifest(cfg):
    rows=[]
    for b,r,h,s in itertools.product(["resnet50","convnext_tiny","dinov2_vits14"],["frozen","finetune"],["independent","joint"],cfg["study"]["model_seeds"]):
        spec=spec_from_cfg(cfg,b,r,h,s);run=paths(cfg)["runs"]/spec.run_id
        status="complete" if (run/"complete.json").exists() else "resumable" if (run/"last.pt").exists() else "not_started"
        if status=="complete":
            from dataclasses import asdict
            old=read_json(run/"run.json");expected=asdict(spec)
            # A persisted DINO immutable snapshot replaces the initial unspecified revision.
            expected["revision"]=old["spec"].get("revision")
            current_code=digest({f.name:sha256(f) for f in Path(__file__).parent.glob("*.py")})
            if expected!=old["spec"] or old["identity"].get("software_hash")!=current_code:
                status="complete_incompatible"
        rows.append({"run_id":spec.run_id,"backbone":b,"regime":r,"head":h,"seed":s,"status":status})
    return pd.DataFrame(rows)


def run_grid(cfg,run_ids,device=None):
    manifest=grid_manifest(cfg);selected=manifest[manifest.run_id.isin(run_ids)]
    if len(selected)!=len(set(run_ids)):raise ValueError("Unknown run ID")
    for row in selected.itertuples():
        if row.status=="complete_incompatible":raise RuntimeError(f"{row.run_id}: completed under different code/config; version an amendment rather than silently mixing runs")
        if row.status=="complete":continue
        spec=spec_from_cfg(cfg,row.backbone,row.regime,row.head,int(row.seed))
        run_training(cfg,spec,device)
        write_table(paths(cfg)["reports"]/"fit_registry.csv",grid_manifest(cfg))
    return grid_manifest(cfg)


def partition_predictions(cfg,run_id,partition,*,device=None,allow_unblind=False):
    p=paths(cfg);run=p["runs"]/run_id
    spec=read_json(run/"run.json")["spec"]
    if partition not in ("fit","validation","calibration","test","external","pilot"):raise ValueError("Unknown partition")
    if partition in ("test","external"):
        if not allow_unblind:raise PermissionError("Test inference requires explicit locked evaluation")
        record_unblinding(p["private"]/"analysis_lock.json",p["private"]/f"{partition}_first_access.json",partition)
    records,targets=load_study(cfg,spec["head"],stage_images=True)
    subset=records[records.split.eq(partition)]
    if subset.empty:raise ValueError(f"No {partition} records")
    result=predict_run(run,subset,targets,p["features"],device=device)
    atomic_npz(run/f"{partition}_predictions.npz",**result)
    return result


def calibrate_predictor(cfg,run_id,device=None):
    p=paths(cfg);run=p["runs"]/run_id
    pred=partition_predictions(cfg,run_id,"calibration",device=device)
    calibrators={"identity":{"kind":"identity"},"temperature":fit_temperature(pred["logits"],pred["y"],pred["mask"]),
                 "sigmoid":fit_sigmoid(pred["logits"],pred["y"],pred["mask"])}
    # Do NOT select a calibrator by its in-sample calibration loss. Validation comparison is explicit.
    vp=partition_predictions(cfg,run_id,"validation",device=device)
    metrics={name:calibration_metrics(probabilities(vp["logits"],cal),vp["y"],vp["mask"]) for name,cal in calibrators.items()}
    write_json(run/"calibrators.json",calibrators);write_json(run/"calibration_validation_metrics.json",metrics)
    return calibrators,metrics


def prediction_arrays(path):
    with np.load(path,allow_pickle=False) as z:return {k:z[k] for k in z.files}


def frequency_baseline(cfg,head="independent",partition="validation"):
    if partition not in ("validation","calibration"):raise ValueError("Baseline development does not unblind tests")
    from .targets import align_targets
    records,targets=load_study(cfg,head);fit=records[records.split.eq("fit")];evalr=records[records.split.eq(partition)]
    y,m=align_targets(targets,fit.record_id);frequency=np.divide((y*m).sum(0),m.sum(0),out=np.zeros(y.shape[1]),where=m.sum(0)>0)
    yy,mm=align_targets(targets,evalr.record_id);p=np.broadcast_to(frequency,(len(evalr),len(frequency))).copy()
    result={"ids":evalr.record_id.to_numpy(dtype=str),"probabilities":p,"y":yy,"mask":mm}
    atomic_npz(paths(cfg)["runs"]/f"frequency_{head}_{partition}.npz",**result)
    return result
