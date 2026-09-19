"""One-time git bootstrap for this repository.

Run once from the scratch commit-console notebook. The token is collected in
the notebook with getpass and passed in ONCOPLATE_GITHUB_TOKEN; it is never
read here interactively, because a subprocess has no terminal to prompt on.

Writes .gitconfig and .git-credentials to the Drive parent folder so every
later runtime restores them through tools/commit_cell.py.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

IDENTITY_NAME = "Md Anas Biswas"
IDENTITY_EMAIL = "anasbiswas@gmail.com"
GITHUB_USER = "anasbiswas1"
TOKEN_VAR = "ONCOPLATE_GITHUB_TOKEN"


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True)
    if proc.stdout.strip():
        print(proc.stdout.rstrip())
    if proc.stderr.strip():
        print(proc.stderr.rstrip(), file=sys.stderr)
    if check and proc.returncode != 0:
        raise SystemExit(f"FAILED: {' '.join(cmd)} (exit {proc.returncode})")
    return proc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--remote", required=True, help="https://github.com/<user>/<repo>.git")
    ap.add_argument("--repo", default=None)
    ap.add_argument("--branch", default="main")
    args = ap.parse_args()

    repo = Path(args.repo).resolve() if args.repo else Path(__file__).resolve().parent.parent
    parent = repo.parent
    home = Path(os.path.expanduser("~"))

    # 1. Identity dotfiles live at the Drive parent so they
