"""Resumable HTTPS download, ZIP validation and safe local extraction."""
from __future__ import annotations
import os, shutil, stat, zipfile
from pathlib import Path
import requests
from .io import sha256,write_json,utcnow


def download(url, destination, expected_sha256=None, timeout=90):
    destination=Path(destination); destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():
        h=sha256(destination)
        if expected_sha256 and h!=expected_sha256: raise ValueError("Existing download checksum mismatch")
        return destination
    tmp=Path(str(destination)+".part"); size=tmp.stat().st_size if tmp.exists() else 0
    headers={"User-Agent":"OncoPlate-Research/3.0", "Accept-Encoding":"identity"}
    if size:headers["Range"]=f"bytes={size}-"
    with requests.get(url,stream=True,headers=headers,timeout=timeout) as r:
        if r.status_code==416:
            raise RuntimeError("Partial file exceeds server range; inspect .part and source version before retry")
        r.raise_for_status()
        if size and r.status_code==206:
            content_range=r.headers.get("Content-Range","")
            if not content_range.startswith(f"bytes {size}-"):raise RuntimeError("Server returned wrong resume offset")
            mode="ab"
        else:mode="wb";size=0
        with open(tmp,mode) as f:
            for chunk in r.iter_content(4*1024*1024):
                if chunk:f.write(chunk)
            f.flush();os.fsync(f.fileno())
    h=sha256(tmp)
    if expected_sha256 and h!=expected_sha256:raise ValueError("Downloaded checksum mismatch; .part retained for inspection")
    os.replace(tmp,destination)
    write_json(str(destination)+".provenance.json",{"url":url,"retrieved_at":utcnow(),"sha256":h,"publisher_hash_supplied":bool(expected_sha256)})
    return destination


def extract_zip(archive, destination, *, validate_crc=True):
    archive=Path(archive); destination=Path(destination).resolve();destination.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        required=sum(i.file_size for i in z.infolist())
        if required>shutil.disk_usage(destination).free:raise OSError("Insufficient LOCAL disk for archive; Drive capacity does not enlarge runtime disk")
        for info in z.infolist():
            target=(destination/info.filename).resolve()
            if target!=destination and destination not in target.parents:raise ValueError("Unsafe ZIP path")
            if stat.S_ISLNK(info.external_attr>>16):raise ValueError("ZIP symlink rejected")
        if validate_crc:
            bad=z.testzip()
            if bad:raise ValueError(f"Corrupt ZIP member: {bad}")
        z.extractall(destination)
    write_json(destination/"extraction.json",{"archive_sha256":sha256(archive),"uncompressed_bytes":required,"created_at":utcnow()})
    return destination
