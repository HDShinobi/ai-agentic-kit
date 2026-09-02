"""Git containment (spec §4.8). Workers have no git authority; Control alone
commits. This module gives Control the checks that make that enforceable when
the worktree shares `.git/` with the repo: snapshot/restore git-control state,
detect drift, compute the true changed-path set (including ignored files),
and commit ONLY owned paths with a commit==reviewed-diff verification.
Recovery never touches the working tree.
"""
from __future__ import annotations
import subprocess
from dataclasses import dataclass
from pathlib import Path
from .errors import ContainmentError

def _git(repo: Path, *args: str, check: bool = True) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    except OSError as exc:
        # A nonexistent/inaccessible repo makes subprocess.run(cwd=...) raise
        # a raw FileNotFoundError/NotADirectoryError/OSError before git even
        # spawns -- never let that leak past this module's typed-error
        # contract (mirrors dispatch.py's OSError -> DispatchError; kept
        # consistent with mcd_core.workspace._git's identical hardening).
        raise ContainmentError(f"git invocation failed in {repo}: {exc}") from exc
    if check and r.returncode != 0:
        raise ContainmentError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout

@dataclass(frozen=True)
class GitState:
    head: str
    refs: dict[str, str]
    index_tree: str            # `git write-tree`-style hash of the current index

def _refs(repo: Path) -> dict[str, str]:
    out = _git(repo, "show-ref")
    refs: dict[str, str] = {}
    for line in out.splitlines():
        sha, name = line.split(" ", 1)
        refs[name.strip()] = sha
    return refs

def snapshot_git_state(repo: Path) -> GitState:
    head = _git(repo, "rev-parse", "HEAD").strip()
    index_tree = _git(repo, "write-tree").strip()   # captures staged content
    return GitState(head=head, refs=_refs(repo), index_tree=index_tree)

def detect_git_drift(repo: Path, before: GitState) -> list[str]:
    now = snapshot_git_state(repo)
    drift: list[str] = []
    if now.head != before.head:
        drift.append(f"HEAD moved {before.head[:8]}→{now.head[:8]}")
    if now.refs != before.refs:
        drift.append("refs changed")
    if now.index_tree != before.index_tree:
        drift.append("index changed")
    return drift

def restore_git_state(repo: Path, before: GitState) -> None:
    # refs: restore recorded, delete worker-created (never touch the working tree)
    current = _refs(repo)
    for name, sha in before.refs.items():
        if current.get(name) != sha:
            _git(repo, "update-ref", name, sha)
    for name in set(current) - set(before.refs):
        _git(repo, "update-ref", "-d", name, check=False)
    # current branch ref to recorded sha
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip()
    if branch != "HEAD":
        _git(repo, "update-ref", f"refs/heads/{branch}", before.head)
    # index to the recorded snapshot (NOT to HEAD — preserves mid-run staged content)
    _git(repo, "read-tree", before.index_tree)

def changed_paths(repo: Path, baseline_ref: str) -> set[str]:
    # `git status`/a single ls-files call is not enough to find the true
    # changed-path set: tracked changes, brand-new untracked files, and
    # .gitignore'd untracked files (e.g. a leaked secret) live in three
    # disjoint git views. Union all three so none can slip past scope checks.
    def _split0(s: str) -> list[str]:
        return [p for p in s.split("\0") if p]
    tracked = _git(repo, "diff", "--name-only", baseline_ref).split()
    untracked = _split0(_git(repo, "ls-files", "--others", "--exclude-standard", "-z"))
    ignored = _split0(_git(repo, "ls-files", "--others", "--ignored", "--exclude-standard", "-z"))
    return set(tracked) | set(untracked) | set(ignored)

def classify_scope(changed: set[str], owned: set[str]) -> set[str]:
    return set(changed) - set(owned)

def _is_ignored(repo: Path, path: str) -> bool:
    return subprocess.run(["git", "check-ignore", "-q", path], cwd=repo).returncode == 0

def commit_owned(repo: Path, owned: list[str], message: str, *,
                 force_add: list[str] = []) -> str:
    force = set(force_add)
    for p in owned:
        if _is_ignored(repo, p) and p not in force:
            raise ContainmentError(
                f"owned path {p!r} is .gitignore'd — a candidate should not hinge on "
                f"committing an ignored file; declare force_add to override (spec §4.8)")
    for p in owned:
        _git(repo, "add", "-f", p) if p in force else _git(repo, "add", p)
    _git(repo, "commit", "--only", "-m", message, "--", *owned)
    sha = _git(repo, "rev-parse", "HEAD").strip()
    committed = set(_git(repo, "show", "--name-only", "--format=", sha).split())
    if committed != set(owned):
        raise ContainmentError(
            f"commit contents {sorted(committed)} != reviewed owned diff {sorted(owned)} "
            f"— halt, not a completed task (spec §4.8 commit==reviewed-diff)")
    return sha
