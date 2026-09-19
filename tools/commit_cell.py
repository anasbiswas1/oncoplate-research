"""Single commit interface for this repository.

Invoked only from the scratch commit-console notebook:

    subprocess.run([sys.executable, "tools/commit_cell.py", "message"])

Steps: restore git identity from the Drive parent folder, strip notebook
outputs, stage, commit, push. Identical contract across projects.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

IDENTITY_NAME = "Md Anas Biswas"
IDENTITY_EMAIL = "anasbiswas@gmail.com"
DOTFILES = (".gitconfig", ".git-credentials")


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True)
    if proc.stdout.strip():
        print(proc.stdout.rstrip())
    if proc.stderr.strip():
        print(proc.stderr.rstrip(), file=sys.stderr)
    if check and proc.returncode != 0:
        raise SystemExit(f"FAILED: {' '.join(cmd)} (exit {proc.returncode})")
    return proc


def restore_identity(repo: Path) -> None:
    """Copy .gitconfig / .git-credentials from the Drive parent folder to $HOME."""
    parent = repo.parent
    home = Path(os.path.expanduser("~"))
    for name in DOTFILES:
        src = parent / name
        if src.is_file():
            shutil.copy2(src, home / name)
            if name == ".git-credentials":
                (home / name).chmod(0o600)
            print(f"identity: restored {name}")
    run(["git", "config", "user.name", IDENTITY_NAME], repo)
    run(["git", "config", "user.email", IDENTITY_EMAIL], repo)


def strip_outputs(repo: Path) -> None:
    """Clear notebook outputs in place. nbconvert is the permanent recipe."""
    notebooks = sorted(p for p in repo.rglob("*.ipynb") if ".ipynb_checkpoints" not in p.parts)
    if not notebooks:
        return
    proc = subprocess.run(
        [sys.executable, "-m", "jupyter", "nbconvert",
         "--ClearOutputPreprocessor.enabled=True", "--inplace",
         *[str(p) for p in notebooks]],
        cwd=str(repo), text=True, capture_output=True,
    )
    if proc.returncode != 0:
        # Fall back to nbformat so a missing nbconvert never blocks a commit.
        import nbformat
        for path in notebooks:
            nb = nbformat.read(path, as_version=4)
            changed = False
            for cell in nb.cells:
                if cell.cell_type == "code" and (cell.get("outputs") or cell.get("execution_count")):
                    cell["outputs"] = []
                    cell["execution_count"] = None
                    changed = True
            if changed:
                nbformat.write(nb, path)
        print(f"outputs: stripped {len(notebooks)} notebook(s) via nbformat fallback")
    else:
        print(f"outputs: stripped {len(notebooks)} notebook(s) via nbconvert")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("message", help="commit message")
    ap.add_argument("--repo", default=None, help="repo root (default: this file's parent)")
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).resolve() if args.repo else Path(__file__).resolve().parent.parent
    if not (repo / ".git").exists():
        raise SystemExit(f"Not a git checkout: {repo}. Run the one-time git bootstrap first.")

    print(f"repo: {repo}")
    restore_identity(repo)
    strip_outputs(repo)

    run(["git", "add", "-A"], repo)
    status = run(["git", "status", "--short"], repo)
    if not status.stdout.strip():
        print("nothing to commit")
        return 0

    run(["git", "commit", "-m", args.message], repo)
    if not args.no_push:
        run(["git", "push"], repo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
