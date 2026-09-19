"""Atomic writes, checksums, explicit provenance, and portable manifests."""
from __future__ import annotations
import hashlib, json, os, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def digest(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


def _json_default(x):
    if isinstance(x, np.ndarray): return x.tolist()
    if isinstance(x, np.generic): return x.item()
    if isinstance(x, Path): return str(x)
    raise TypeError(type(x).__name__)


def write_json(path: str | Path, obj: Any) -> Path:
    # Explicit null for undefined estimates; never emit non-standard NaN JSON.
    def clean(x):
        if isinstance(x, dict): return {str(k): clean(v) for k,v in x.items()}
        if isinstance(x, (list, tuple, np.ndarray)): return [clean(v) for v in x]
        if isinstance(x, (float, np.floating)) and not np.isfinite(x): return None
        return x
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(clean(obj), f, indent=2, default=_json_default, allow_nan=False)
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    return path


def read_json(path: str | Path):
    with open(path, encoding="utf-8") as f: return json.load(f)


def write_table(path: str | Path, df: pd.DataFrame) -> Path:
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent); os.close(fd)
    try:
        df.to_csv(tmp, index=False)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    return path


def read_table(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, keep_default_na=False, dtype=str)


def write_jsonl(path: str | Path, rows: list[dict]) -> Path:
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fd,tmp = tempfile.mkstemp(prefix=path.name+".", dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            for row in rows: f.write(json.dumps(row, default=_json_default, allow_nan=False)+"\n")
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    return path


def read_jsonl(path: str | Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def atomic_npz(path: str | Path, **arrays) -> Path:
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(suffix=".npz",dir=path.parent); os.close(fd)
    try:
        np.savez_compressed(tmp, **arrays); os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    return path


def environment_manifest() -> dict:
    import platform, importlib.metadata as im
    packages={}
    for name in ("numpy","pandas","scipy","scikit-learn","torch","torchvision","transformers","Pillow"):
        try: packages[name]=im.version(name)
        except im.PackageNotFoundError: packages[name]=None
    result={"created_at":utcnow(), "python":sys.version,"platform":platform.platform(),"packages":packages}
    try:
        import torch
        result.update(cuda_available=torch.cuda.is_available(), cuda_version=torch.version.cuda)
        if torch.cuda.is_available():
            p=torch.cuda.get_device_properties(0)
            result.update(gpu=p.name,gpu_memory_bytes=p.total_memory)
    except ImportError: pass
    return result


def freeze_environment(path: str | Path):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(subprocess.check_output([sys.executable,"-m","pip","freeze"],text=True),encoding="utf-8")


def require_columns(df: pd.DataFrame, required: list[str], name="table"):
    missing=set(required)-set(df.columns)
    if missing: raise ValueError(f"{name}: missing columns {sorted(missing)}")


def require_unique(df: pd.DataFrame, keys: list[str], name="table"):
    require_columns(df,keys,name)
    if df.duplicated(keys).any(): raise ValueError(f"{name}: duplicate keys {keys}")
