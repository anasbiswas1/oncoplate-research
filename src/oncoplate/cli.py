"""Command line entry points; Colab notebooks call the same tested functions."""
import argparse,json
from pathlib import Path
from .config import load_config,initialize,paths
from .io import write_table


def main():
    parser=argparse.ArgumentParser(prog="oncoplate")
    parser.add_argument("--repo",default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--root",default=None)
    parser.add_argument("--dataset",default=None)
    sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("init");sub.add_parser("status");sub.add_parser("demo")
    train=sub.add_parser("train");train.add_argument("--backbone",default="resnet50");train.add_argument("--regime",choices=["frozen","finetune"],default="frozen");train.add_argument("--head",choices=["independent","joint"],default="independent");train.add_argument("--seed",type=int,default=0)
    grid=sub.add_parser("grid");grid.add_argument("--run-id",action="append",default=[]);grid.add_argument("--execute",action="store_true")
    args=parser.parse_args();cfg=load_config(args.repo,mode="demo" if args.command=="demo" else "research",root=args.root)
    if args.dataset:cfg["study"]["dataset"]=args.dataset
    if args.command=="init":print({k:str(v) for k,v in initialize(cfg).items()})
    elif args.command=="demo":
        from .demo import run_demo
        print(json.dumps(run_demo(cfg),indent=2))
    elif args.command in ("status","grid"):
        from .pipeline import grid_manifest,run_grid
        manifest=grid_manifest(cfg)
        if args.command=="grid" and args.execute:
            if not args.run_id:raise SystemExit("Select --run-id explicitly; no unattended whole-grid launch")
            manifest=run_grid(cfg,args.run_id)
        print(manifest.to_string(index=False))
    elif args.command=="train":
        from .pipeline import run_training,spec_from_cfg
        print(run_training(cfg,spec_from_cfg(cfg,args.backbone,args.regime,args.head,args.seed)))

if __name__=="__main__":main()
