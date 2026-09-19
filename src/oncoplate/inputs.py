"""Strict input contracts and helpers used by the Colab notebooks."""
from pathlib import Path
from dataclasses import asdict
import json
import numpy as np
import pandas as pd
from PIL import Image,ImageOps
from .io import read_json,write_json,read_jsonl,write_jsonl,write_table,read_table,require_unique,digest
from .claims import Source,DOC_TYPES


def validate_states(records,states):
    unknown=set(states)-set(records.record_id)
    if unknown:raise ValueError("State IDs do not occur in the dataset")
    for r in records.to_dict("records"):
        s=states.get(r["record_id"])
        if s is None:raise ValueError(f'Missing inference state: {r["record_id"]}')
        if not {"focal_field","focal_item_id","visual_scope"}.issubset(s):raise ValueError("Missing task/scope metadata")
        if s["visual_scope"] not in ("record_presence","focal_crop","single_item"):raise ValueError("Unknown visual scope")
        if s["visual_scope"]=="record_presence" and s["focal_item_id"]!="__record__":
            raise ValueError("Whole-meal presence cannot bind an image prediction to a specific item; supply a declared focal crop")
        for k in ("ground_truth","reference_labels","support_status","y_support"):
            if k in s:raise ValueError("Hidden reference in inference input")
        for data in s.get("sources",[]):
            src=Source(**data)
            if not isinstance(src.reference_only,bool) or not isinstance(src.available_at_inference,bool):raise ValueError("JSON source flags must be booleans")
            if (src.record_id,src.item_id)!=(r["record_id"],s["focal_item_id"]):raise ValueError("Cross-item source")
            if src.reference_only or not src.available_at_inference:raise ValueError("Hidden source in inference state file")
    return {"records":len(records),"validated":True}


def draft_rules(schema):
    """Populate values from fitting taxonomy, without creating dietary evidence or approval."""
    fields={}
    for label in schema["labels"]:
        for f,v in json.loads(label).items():fields.setdefault(f,set()).add(v)
    return {f:{"claim_id":f"attribute_{f}","fields":[f],"values":sorted(vals),"qualifiers":["predicted","recorded","observed"],
               "documentary_for_recorded":True,"specificity":1,"review_status":"pending_domain_review","evidence_id":""}
            for f,vals in fields.items()}


def foundation_states(records,focal_field="subcategory"):
    return {r:{"focal_field":focal_field,"focal_item_id":"__record__","visual_scope":"record_presence","sources":[]} for r in records.record_id}


def crop_focal_image(image_path,box,out):
    """Box is a documented INFERENCE input [left,top,right,bottom] in pixels.
    Review annotations for this task refer to the same visible crop; no oracle detector.
    """
    with Image.open(image_path) as im:
        im=ImageOps.exif_transpose(im).convert("RGB")
        l,t,r,b=map(int,box)
        if not (0<=l<r<=im.width and 0<=t<b<=im.height):raise ValueError("Invalid focal crop")
        Path(out).parent.mkdir(parents=True,exist_ok=True);im.crop((l,t,r,b)).save(out)
    return str(out)


def load_context(cfg,require_review=False):
    from .config import paths
    from .pipeline import load_study
    from .governance import require_gate
    p=paths(cfg);records,targets=load_study(cfg,"joint")
    if cfg["study"]["dataset"]=="foodnextdb":
        rules=draft_rules(targets["schema"]);states=foundation_states(records)
    else:
        states=read_json(p["private"]/"inference_states.json");rules=read_json(p["private"]/"claim_rules.json")
        validate_states(records,states)
        if require_review:
            require_gate(cfg,"domain_schema")
            if any(r.get("review_status")!="approved" or not r.get("review_reference") for r in rules.values()):
                raise PermissionError("Claim rules need actual domain review references")
    return records,targets,states,rules


def make_partition_candidates(cfg,run_id,partition,*,input_mode="multimodal",asof,allow_unblind=False):
    from .pipeline import partition_predictions
    from .benchmark import candidate_rows,make_rating_jobs
    from .calibration import probabilities
    from .config import paths
    p=paths(cfg);records,targets,states,rules=load_context(cfg,require_review=cfg["study"]["dataset"]!="foodnextdb")
    pred=partition_predictions(cfg,run_id,partition,allow_unblind=allow_unblind)
    run=p["runs"]/run_id;calfile=run/"calibrators.json"
    cal={"kind":"identity"}  # Shared OOF/deployment feature contract. Support scores are calibrated separately.
    pred["probabilities"]=probabilities(pred["logits"],cal)
    rr=records.set_index("record_id").loc[pred["ids"]].reset_index()
    cc,objects=candidate_rows(rr,pred,targets["schema"],states,rules,asof=asof,input_mode=input_mode)
    out=p["private"]/"claims"/run_id/input_mode;out.mkdir(parents=True,exist_ok=True)
    write_table(out/f"{partition}_candidates.csv",cc);write_jsonl(out/f"{partition}_objects.jsonl",objects)
    make_rating_jobs(cc,out/f"{partition}_rating_jobs.csv")
    return cc,objects,out
