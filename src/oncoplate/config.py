from __future__ import annotations
import copy, os
from pathlib import Path
import yaml
from .io import write_json, environment_manifest, freeze_environment


def load_config(repo: str | Path, *, mode="research", root=None) -> dict:
    repo=Path(repo).resolve()
    with open(repo/"config/default.yaml") as f: cfg=yaml.safe_load(f)
    cfg["repo"]=str(repo); cfg["mode"]=mode
    base=Path(root or os.environ.get("ONCOPLATE_DRIVE_ROOT",cfg["paths"]["drive_root"]))
    if mode=="demo": base=base/"DEMO_ONLY"
    cfg["root"]=str(base.resolve())
    active=base/"governance/active_study.json"
    if mode!="demo" and active.exists():
        from .io import read_json
        cfg["study"]["dataset"]=read_json(active)["dataset"]
    if mode!="demo" and os.environ.get("ONCOPLATE_DATASET"):
        cfg["study"]["dataset"]=os.environ["ONCOPLATE_DATASET"]
    cfg["local_root"]=os.environ.get("ONCOPLATE_LOCAL_ROOT",cfg["paths"]["local_root"])
    if mode=="demo":
        cfg["study"]["dataset"]="synthetic_fixture"
        cfg["training"].update(max_epochs=3,head_epochs=8,patience=3,num_workers=0,pretrained=False)
    return cfg


def paths(cfg:dict) -> dict[str,Path]:
    root=Path(cfg["root"])
    dataset=cfg["study"]["dataset"]
    return {"root":root,"raw":root/"data/raw"/dataset,
            "prepared":root/"data/processed"/dataset,"runs":root/"runs"/dataset,
            "features":root/"features"/dataset,"private":root/"private"/dataset,
            "reports":root/"reports"/dataset,"permissions":root/"governance",
            "local":Path(cfg["local_root"])/dataset,"exports":root/"exports"/dataset}


def initialize(cfg):
    for p in paths(cfg).values(): p.mkdir(parents=True,exist_ok=True)
    write_json(paths(cfg)["reports"]/"environment_manifest.json",environment_manifest())
    freeze_environment(paths(cfg)["reports"]/"requirements-runtime-lock.txt")
    return paths(cfg)
