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
    try:
        r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    except OSError as exc:
        # A nonexistent/inaccessible repo makes subprocess.run(cwd=...) raise
        # a raw FileNotFoundError/NotADirectoryError/OSError before git even
        # spawns -- never let that leak past this module's typed-error
        # contract (mirrors dispatch.py's OSError -> DispatchError).
        raise ContainmentError(f"git invocation failed in {repo}: {exc}") from exc
    if r.returncode != 0:
        raise ContainmentError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout

def _branch_exists(repo: Path, name: str) -> bool:
    try:
        r = subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{name}"],
                           cwd=repo)
    except OSError as exc:
        # Sibling of _git's guard above: this call bypasses _git() (no
        # stdout/stderr capture needed, just the exit code) but the same
        # nonexistent/inaccessible repo raises the same raw
        # FileNotFoundError/NotADirectoryError/OSError before git even
        # spawns -- never let that leak past this module's typed-error
        # contract.
        raise ContainmentError(f"git invocation failed in {repo}: {exc}") from exc
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
    # `git status --porcelain` (no -z) renders a rename as "old -> new" and
    # quotes/escapes any path containing a space or other special character --
    # a naive line[3:] + " -> ".split() parse cannot recover those cleanly.
    # -z instead gives NUL-terminated entries with paths verbatim (no
    # quoting) and no arrow: a rename/copy is TWO consecutive entries, the
    # new path (with its XY status prefix) immediately followed by the bare
    # old path.
    out = _git(repo_root, "status", "--porcelain", "-z")
    entries = [e for e in out.split("\0") if e]
    dirty: set[str] = set()
    i = 0
    while i < len(entries):
        entry = entries[i]
        status, path = entry[:2], entry[3:]
        dirty.add(path)
        if status.startswith(("R", "C")):
            i += 1
            if i < len(entries):
                dirty.add(entries[i])
        i += 1
    return [p for p in owned_paths if p in dirty]

def branch_gate(repo_root: Path) -> str:
    branch = _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD").strip()
    if branch == "HEAD":
        raise ContainmentError("detached HEAD — halt and escalate (spec §5.1 step 1); "
                               "commits must land on a non-default feature branch")
    return branch
