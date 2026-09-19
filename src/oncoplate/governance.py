"""Fail-closed authorisation records and hash-locked test access.
These are procedural safeguards, NOT cryptographic access control against a data owner.
"""
from __future__ import annotations
from pathlib import Path
from .io import read_json,write_json,sha256,utcnow,digest

GATES=("supervisor_execution","foodnextdb_research_terms","new_collection", "domain_schema", "user_study", "lab_study", "product_release")


def initial_approvals():
    return {k:{"status":"pending","decision_reference":"","decided_by":"","date":""} for k in GATES}


def approval_report(root):
    p=Path(root)/"governance/approvals.json"
    if not p.exists(): write_json(p,initial_approvals())
    return read_json(p)


def require_gate(cfg, gate):
    if cfg.get("mode")=="demo": return
    entry=approval_report(cfg["root"]).get(gate,{})
    if entry.get("status") not in ("approved","not_required_by_recorded_determination") or not entry.get("decision_reference"):
        raise PermissionError(f"Gate '{gate}' pending. Record the ACTUAL decision and reference in {cfg['root']}/governance/approvals.json. Do not invent approval. Demo tests remain runnable.")


def make_lock(path, files, protocol):
    if not files: raise ValueError("An analysis lock must bind code/config/model/reference contracts.")
    items={str(Path(p).resolve()):sha256(p) for p in files}
    lock={"created_at":utcnow(),"artifacts":items,"protocol":protocol,"protocol_hash":digest(protocol)}
    lock["lock_hash"]=digest(lock)
    path=Path(path)
    if path.exists(): raise FileExistsError("Lock already exists. Version an amendment, never overwrite a test lock.")
    write_json(path,lock); return lock


def verify_lock(path):
    lock=read_json(path)
    for file,expected in lock["artifacts"].items():
        if not Path(file).exists() or sha256(file)!=expected:
            raise RuntimeError(f"Locked artefact changed or missing: {file}")
    core={k:v for k,v in lock.items() if k!="lock_hash"}
    if digest(core)!=lock["lock_hash"]: raise RuntimeError("Lock record was altered")
    return lock


def record_unblinding(lock_path,access_path,cohort):
    lock=verify_lock(lock_path)
    p=Path(access_path)
    if p.exists():
        old=read_json(p)
        if old["lock_hash"]!=lock["lock_hash"]: raise RuntimeError("Cohort was already opened under another lock")
        return old
    result={"first_access_at":utcnow(),"cohort":cohort,"lock_hash":lock["lock_hash"]}
    write_json(p,result); return result


def check_lineage(assets, target="research"):
    byid={a["asset_id"]:a for a in assets}
    seen=set(); active=set()
    def visit(k):
        if k in active: raise ValueError("Cycle in lineage")
        if k in seen:return
        if k not in byid:raise ValueError(f"Missing parent asset: {k}")
        active.add(k); a=byid[k]
        if a.get(f"permitted_{target}_use",False) is not True: raise PermissionError(f"{k}: no {target} permission")
        for parent in a.get("parent_asset_ids",[]):visit(parent)
        active.remove(k); seen.add(k)
    for k in byid: visit(k)
    return {"cleared":True,"target":target,"assets":len(seen)}
