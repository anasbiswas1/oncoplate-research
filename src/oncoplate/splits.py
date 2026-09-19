"""Connected-component splits: groups, exact duplicates and reviewed near-duplicate edges."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from .io import write_json,write_table,digest,require_unique


class UnionFind:
    def __init__(self, keys):self.parent={k:k for k in keys}
    def find(self,x):
        p=self.parent[x]
        if p!=x:self.parent[x]=self.find(p)
        return self.parent[x]
    def union(self,a,b):
        ra,rb=self.find(a),self.find(b)
        if ra!=rb:self.parent[max(ra,rb)]=min(ra,rb)


def build_components(records, edges=None):
    df=records.copy();require_unique(df,["record_id"])
    uf=UnionFind(list(df.record_id))
    # Broad domains (retailer, country, generic food type) are deliberately NOT edges.
    for col in ("collection_group_id","participant_id","household_pseudonym","session_id","batch_id","focal_product_family_id","sha256"):
        if col not in df:continue
        for _,part in df[df[col].notna() & df[col].astype(str).ne("")].groupby(col):
            ids=part.record_id.tolist()
            for b in ids[1:]:uf.union(ids[0],b)
    if edges is not None:
        for row in edges.itertuples():
            if str(row.approved).strip().lower() not in ("true","1"):continue
            if row.record_a not in uf.parent or row.record_b not in uf.parent:raise ValueError("Unknown edge endpoint")
            uf.union(row.record_a,row.record_b)
    df["group_id"]=["g_"+digest(uf.find(x))[:16] for x in df.record_id]
    return df


def propose_near_duplicates(records, distance=3):
    rows=[]; vals=list(zip(records.record_id,records.dhash))
    for i,(a,x) in enumerate(vals):
        for b,y in vals[i+1:]:
            d=(int(str(x),16)^int(str(y),16)).bit_count()
            if d<=distance:rows.append({"record_a":a,"record_b":b,"hamming":d,"approved":False})
    return pd.DataFrame(rows,columns=["record_a","record_b","hamming","approved"])


def grouped_split(records, fractions=None, seed=0):
    fractions=fractions or {"fit":.48,"validation":.12,"calibration":.2,"test":.2}
    if not np.isclose(sum(fractions.values()),1):raise ValueError("Split fractions do not sum to one")
    if any(v<=0 for v in fractions.values()):raise ValueError("All partitions must be nonempty")
    if "group_id" not in records:records=build_components(records)
    groups=np.array(sorted(records.group_id.unique()),dtype=str)
    if len(groups)<max(8,len(fractions)*2):raise ValueError("Too few independent groups for 4-way study; do not split linked records")
    np.random.default_rng(seed).shuffle(groups)
    raw=np.array(list(fractions.values()))*len(groups)
    counts=np.floor(raw).astype(int)
    for i in np.argsort(-(raw-counts))[:len(groups)-sum(counts)]:counts[i]+=1
    if (counts==0).any():raise ValueError("Empty group partition")
    assignment={};start=0
    for key,n in zip(fractions,counts):
        for g in groups[start:start+n]:assignment[g]=key
        start+=n
    df=records.copy();df["split"]=df.group_id.map(assignment)
    validate_split(df)
    return df


def validate_split(df):
    require_unique(df,["record_id"])
    for col in ("group_id","collection_group_id","participant_id","sha256","focal_product_family_id"):
        if col not in df:continue
        valid=df[col].notna() & df[col].astype(str).ne("")
        if (df.loc[valid].groupby(col).split.nunique()>1).any():raise ValueError(f"Leakage across {col}")
    if df.split.isna().any():raise ValueError("Unassigned records")
    return True


def save_split(df,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    validate_split(df)
    manifest=df[["record_id","group_id","split"]].sort_values("record_id")
    h=digest(manifest.to_dict("records"))
    p=output/"split_manifest.csv"
    if p.exists():
        previous=pd.read_csv(p,dtype=str)
        if digest(previous.sort_values("record_id").to_dict("records"))!=h:
            raise RuntimeError("Existing split differs. Version an amendment; never silently resplit.")
    write_table(p,manifest)
    write_json(output/"split_integrity.json",{"pass":True,"split_hash":h,"records":df.groupby("split").size().to_dict(),"groups":df.groupby("split").group_id.nunique().to_dict()})
    return h
