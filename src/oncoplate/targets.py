"""Train-only vocabularies, masked reviewer-endorsement targets, and tuple identity."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .datasets import normalize
from .io import digest,write_json,atomic_npz,read_json


def label_key(fields,values):
    return json.dumps(dict(zip(fields,values)),sort_keys=True,separators=(",",":"))


def build_schema(annotations,fit_ids,head="independent",fields=None,min_support=1):
    fields=fields or (["category","subcategory","cooking_style"])
    data=annotations[annotations.record_id.isin(set(fit_ids))].copy()
    fields=[f for f in fields if f in data]
    if not fields:raise ValueError("No modelled fields in annotations")
    labels=[]
    bundles=[[f] for f in fields] if head=="independent" else [fields]
    for fs in bundles:
        seen={}
        for r in data.to_dict("records"):
            vals=[normalize(r.get(f,"")) for f in fs]
            if all(vals):
                key=label_key(fs,vals);seen.setdefault(key,set()).add(r["record_id"])
        labels.extend(sorted(k for k,v in seen.items() if len(v)>=min_support))
    if not labels:raise ValueError("No usable fitting labels; audit annotation completeness")
    schema={"head":head,"fields":fields,"labels":labels,"vocabulary_source":"fitting partition only",
            "negative_semantics":"Eligible reviewer did not record this label; not verified physical absence.",
            "group_bundles":bundles}
    schema["schema_hash"]=digest(schema)
    return schema


def make_targets(records,annotations,schema):
    ids=records.record_id.astype(str).tolist(); pos={r:i for i,r in enumerate(ids)}
    labels=schema["labels"];index={c:j for j,c in enumerate(labels)}
    y=np.zeros((len(ids),len(labels)),dtype=np.float32)
    mask=np.zeros_like(y);counts=np.zeros_like(y);unseen=[]
    parsed=[json.loads(k) for k in labels]
    for rid,part in annotations.groupby("record_id",sort=False):
        if str(rid) not in pos:continue
        i=pos[str(rid)]
        for fs in schema["group_bundles"]:
            columns=[j for j,v in enumerate(parsed) if set(v)==set(fs)]
            reviewers=[]
            for reviewer,rv in part.groupby("reviewer_id",sort=False):
                # Exclude this review for a bundle if an item has a missing bundle field.
                # Complete food records are never formed by cartesian product across items.
                rows=rv.to_dict("records")
                if any(not all(normalize(r.get(f,"")) for f in fs) for r in rows):continue
                emitted={label_key(fs,[normalize(r.get(f,"")) for f in fs]) for r in rows}
                if not emitted:continue
                reviewers.append(emitted)
                for k in emitted:
                    if k not in index:unseen.append({"record_id":str(rid),"reviewer_id":str(reviewer),"label":k})
            if not reviewers:continue
            mask[i,columns]=1;counts[i,columns]=len(reviewers)
            for j in columns:y[i,j]=sum(labels[j] in s for s in reviewers)/len(reviewers)
    return {"ids":np.array(ids,dtype=str),"y":y,"mask":mask,"n_reviewers":counts,
            "schema":schema,"unseen":pd.DataFrame(unseen,columns=["record_id","reviewer_id","label"])}


def save_targets(targets,path):
    path=Path(path);path.mkdir(parents=True,exist_ok=True)
    write_json(path/"schema.json",targets["schema"])
    atomic_npz(path/"targets.npz",ids=targets["ids"],y=targets["y"],mask=targets["mask"],n_reviewers=targets["n_reviewers"])
    targets["unseen"].to_csv(path/"unseen_labels.csv",index=False)


def load_targets(path):
    path=Path(path)
    with np.load(path/"targets.npz",allow_pickle=False) as f:out={k:f[k] for k in f.files}
    out["schema"]=read_json(path/"schema.json")
    return out


def align_targets(targets,ids):
    lookup={r:i for i,r in enumerate(targets["ids"])}
    try:ix=np.array([lookup[str(r)] for r in ids],dtype=int)
    except KeyError as e:raise ValueError(f"Missing target for {e}") from e
    return targets["y"][ix],targets["mask"][ix]


def marginal_tuple_score(independent_probs,independent_schema,joint_schema):
    # Product is only a baseline ranking score, NOT an assumed calibrated joint probability.
    ind={label:j for j,label in enumerate(independent_schema["labels"])}
    columns=[]
    for label in joint_schema["labels"]:
        item=json.loads(label);js=[]
        for field,value in item.items():
            k=label_key([field],[value])
            if k not in ind:break
            js.append(ind[k])
        columns.append(np.prod(independent_probs[:,js],axis=1) if len(js)==len(item) else np.zeros(len(independent_probs)))
    return np.column_stack(columns)
