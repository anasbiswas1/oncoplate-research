"""Explicit adapters. Public expert visual labels are not documentary/chemical truth."""
from __future__ import annotations
import ast, json, re
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
from .io import sha256,write_json,write_table,require_columns,require_unique,read_jsonl

FIELDS=("category","subcategory","cooking_style")
UNKNOWN={"", "nan", "null", "unknown", "not known", "unspecified", "n/a"}


def normalize(v):
    if v is None or (isinstance(v,float) and np.isnan(v)):return ""
    s=str(v).strip().casefold()
    return "" if s in UNKNOWN else re.sub(r"\s+"," ",s)


def values(v):
    """Recognise explicit JSON/Python lists only. Never split ordinary comma-containing names."""
    if isinstance(v,list):return v
    s=str(v).strip()
    if s.startswith("["):
        try:a=json.loads(s)
        except json.JSONDecodeError:a=ast.literal_eval(s)
        if not isinstance(a,list):raise ValueError("Expected list annotation")
        return a
    return [v]


def image_hashes(path):
    with Image.open(path) as im:
        im=ImageOps.exif_transpose(im).convert("RGB")
        w,h=im.size
        # dHash is a proposal generator, not proof of identity; near pairs require review.
        a=np.asarray(im.convert("L").resize((9,8)),dtype=np.int16)
        bits=(a[:,1:]>a[:,:-1]).reshape(-1)
        dh=sum(int(b)<<i for i,b in enumerate(bits))
    return sha256(path),f"{dh:016x}",w,h


MAX_MISSING_IMAGES=20


def audit_foodnextdb(root, output):
    root=Path(root);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    files=list(root.rglob("*_labeled_data.csv"))
    if not files:raise FileNotFoundError("No *_labeled_data.csv found. Inspect archive; do not fabricate a label table.")
    images={}
    for p in root.rglob("*"):
        if p.suffix.lower() in (".jpg",".jpeg",".png"):
            if p.name in images:raise ValueError(f"Duplicate image basename {p.name}; resolve explicitly")
            images[p.name]=p
    rows=[];missing=[]
    for file in sorted(files):
        df=pd.read_csv(file,dtype=str,keep_default_na=False,sep=None,engine="python")
        require_columns(df,["id","id_labeler",*FIELDS],str(file))
        for n,row in df.iterrows():
            iid=Path(str(row["id"])).name
            if iid not in images:
                missing.append({"image_id":iid,"annotation_file":str(file)});continue
            arrays=[values(row[f]) for f in FIELDS]
            lengths=[len(x) for x in arrays]
            if len(set(lengths))!=1:
                raise ValueError(f"{file}:{n}: unequal parallel annotation list lengths {lengths}; pairing cannot be guessed")
            for j,vs in enumerate(zip(*arrays)):
                record={"record_id":iid,"reviewer_id":str(row["id_labeler"]),
                        "item_id":f"r{row['id_labeler']}_row{n}_i{j}",
                        "source_file":str(file.relative_to(root)),"row_number":int(n),
                        "reference_kind":"expert_visual","review_complete":False}
                record.update({f:normalize(v) for f,v in zip(FIELDS,vs)})
                rows.append(record)
    excluded_missing=[]
    if missing:
        # Upstream archive gap: the published CSVs reference images absent from the
        # distributed ZIP. Excluded here and reported; never silently dropped.
        write_table(output/"missing_images.csv",pd.DataFrame(missing))
        excluded_missing=sorted({m["image_id"] for m in missing})
        if len(excluded_missing)>MAX_MISSING_IMAGES:
            raise ValueError(f"{len(excluded_missing)} distinct images missing; exceeds tolerance {MAX_MISSING_IMAGES}")
        rows=[r for r in rows if r["record_id"] not in set(excluded_missing)]
    ann=pd.DataFrame(rows)
    if ann.empty:raise ValueError("No usable annotations")
    records=[];broken=[]
    for iid in sorted(ann.record_id.unique()):
        p=images[iid]
        m=re.match(r"^(A4F_[^_]+)_",iid)
        if not m:raise ValueError(f"Cannot identify participant from {iid}")
        try:h,dh,w,hh=image_hashes(p)
        except Exception as e:broken.append({"record_id":iid,"error":str(e)});continue
        records.append({"record_id":iid,"image_path":str(p.resolve()),"participant_id":m.group(1),
                        "collection_group_id":m.group(1),"domain":"meal","sha256":h,"dhash":dh,
                        "width":w,"height":hh,"source":"foodnextdb","synthetic":False})
    if broken:
        write_table(output/"corrupt_images.csv",pd.DataFrame(broken));raise ValueError("Corrupt images: document exclusions and rerun")
    manifest=pd.DataFrame(records)
    require_unique(manifest,["record_id"])
    vocab={f:sorted(x for x in ann[f].unique() if x) for f in FIELDS}
    report={"images":len(manifest),"participants":manifest.participant_id.nunique(),"annotations":len(ann),
            "reviewers":ann.reviewer_id.nunique(),"vocabulary_sizes":{k:len(v) for k,v in vocab.items()},
            "exact_duplicate_records":int(manifest.duplicated("sha256",keep=False).sum()),
            "protocol_confirmation_required":True,
            "excluded_missing_images":excluded_missing,
            "excluded_missing_image_count":len(excluded_missing),
            "excluded_annotation_rows":len(missing),
            "note":"No cross-reviewer item alignment inferred. Complete-row tuples and reviewer-level presence are retained."}
    write_table(output/"records.csv",manifest);write_table(output/"annotations.csv",ann)
    write_json(output/"vocabulary_audit.json",vocab);write_json(output/"dataset_audit.json",report)
    return manifest,ann,report


def ingest_documented(records_path, annotations_path, output, *, allowed_root=None):
    """Canonical research JSONL: records contain ONLY permitted inference inputs;
    reference annotations remain in a separate file. Required reviews/rights are checked.
    """
    records=read_jsonl(records_path); ann=read_jsonl(annotations_path)
    if not records:raise ValueError("No real documented records supplied")
    req={"record_id","domain","collection_group_id","image_path","rights_id","reference_status","cohort"}
    for r in records:
        if req-set(r):raise ValueError(f"Record fields missing: {req-set(r)}")
        if r["domain"] not in ("meal","product"):raise ValueError("Unknown domain")
        if r["cohort"] not in ("pilot","main","external"):raise ValueError("Unknown cohort")
        if r["reference_status"]!="adjudicated":raise ValueError("Unadjudicated reference record")
        if not r["rights_id"]:raise ValueError("Missing rights reference")
        if any(k in r for k in ("ground_truth","reference_only","support_status","cancer_risk")):
            raise ValueError("Sealed reference/outcome field in inference record")
        image=Path(r["image_path"])
        if not image.is_absolute(): image=Path(allowed_root or Path(records_path).parent)/image
        image=image.resolve()
        if allowed_root and Path(allowed_root).resolve() not in image.parents:raise ValueError("Image outside approved root")
        r["image_path"]=str(image)
        r["sha256"],r["dhash"],r["width"],r["height"]=image_hashes(image)
        r["synthetic"]=False
    df=pd.DataFrame(records); require_unique(df,["record_id"])
    aa=pd.DataFrame(ann)
    require_columns(aa,["record_id","item_id","reviewer_id","review_complete"],"documented annotations")
    if not set(aa.record_id).issubset(set(df.record_id)):raise ValueError("Unknown annotation record")
    if "adjudicated" not in aa:raise ValueError("Reference adjudication status missing")
    if not aa.adjudicated.map(lambda x:str(x).lower()=="true").all():raise ValueError("Unadjudicated annotation")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    write_table(out/"records.csv",df);write_table(out/"annotations.csv",aa)
    write_json(out/"dataset_audit.json",{"records":len(df),"groups":df.collection_group_id.nunique(),
              "source":"new_documented_records","synthetic":False})
    return df,aa
