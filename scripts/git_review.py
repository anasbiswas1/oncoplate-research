"""Read-only Git/privacy review. Does not stage, commit, push, or print secrets."""
from pathlib import Path
import subprocess,sys
repo=Path(__file__).resolve().parents[1]
if not (repo/".git").exists():raise SystemExit("This archive has no Git history. Establish a reviewed checkout before committing.")
print(subprocess.check_output(["git","-C",str(repo),"status","--short"],text=True))
staged=subprocess.check_output(["git","-C",str(repo),"diff","--cached","--name-only"],text=True).splitlines()
for name in staged:
    p=Path(name)
    if p.suffix.lower() in {".pt",".npz",".npy",".jpg",".jpeg",".png",".parquet",".env"} or any(x in p.parts for x in ("data","private","runs","features","checkpoints")):
        raise SystemExit(f"STOP: review restricted/large staged asset: {name}")
    if p.name=="approvals.json" or "token" in p.name.lower():raise SystemExit(f"STOP: potential sensitive governance/secret file: {name}")
print("No disallowed file types among staged paths. Content/rights review is still required. Nothing was pushed.")
