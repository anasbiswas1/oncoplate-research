from pathlib import Path
import sys,argparse
repo=Path(__file__).resolve().parents[1];sys.path.insert(0,str(repo/"src"))
from oncoplate.config import load_config
from oncoplate.demo import run_demo
p=argparse.ArgumentParser();p.add_argument("--root",default="/tmp/oncoplate_software_check");a=p.parse_args()
print(run_demo(load_config(repo,mode="demo",root=a.root)))
