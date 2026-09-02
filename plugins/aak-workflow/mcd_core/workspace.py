"""Run workspace lifecycle (spec §4.9). Default `worktree`: a persistent per-repo
git worktree on the feature branch, reused across runs so native build caches
stay warm; the user's own checkout is never touched. `shared`: run in the user's
checkout (the documented, higher-friction exception). Also the run-start overlap
gate and branch gate (spec §4.8, §5.1 step 1).
"""
from __future__ import annotations
import subprocess
from pathlib import Path
from .errors import ContainmentError

def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    if r.returncode != 0:
        raise ContainmentError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout

def _branch_exists(repo: Path, name: str) -> bool:
    r = subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{name}"],
                       cwd=repo)
    return r.returncode == 0

def prepare_workspace(repo_root: Path, feature_branch: str, *,
                      workspace_mode: str = "worktree",
                      workspaces_dir: Path | None = None) -> Path:
    repo_root = Path(repo_root)
    if workspace_mode == "shared":
        return repo_root
    base = Path(workspaces_dir) if workspaces_dir is not None else (repo_root / ".aak" / "worktrees")
    base.mkdir(parents=True, exist_ok=True)
    ws = base / feature_branch.replace("/", "__")
    if ws.is_dir() and (ws / ".git").exists():
        return ws                        # reuse across runs (warm caches)
    if not _branch_exists(repo_root, feature_branch):
        _git(repo_root, "branch", feature_branch)
    _git(repo_root, "worktree", "add", str(ws), feature_branch)
    return ws

def overlap_gate(repo_root: Path, owned_paths: list[str]) -> list[str]:
    out = _git(repo_root, "status", "--porcelain")
    dirty: set[str] = set()
    for line in out.splitlines():
        if not line.strip():
            continue
        path_part = line[3:]
        if " -> " in path_part:          # rename/copy: "old -> new"
            old, new = path_part.split(" -> ", 1)
            dirty.add(old.strip()); dirty.add(new.strip())
        else:
            dirty.add(path_part.strip())
    return [p for p in owned_paths if p in dirty]

def branch_gate(repo_root: Path) -> str:
    branch = _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD").strip()
    if branch == "HEAD":
        raise ContainmentError("detached HEAD — halt and escalate (spec §5.1 step 1); "
                               "commits must land on a non-default feature branch")
    return branch
