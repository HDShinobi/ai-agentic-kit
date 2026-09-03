"""Git containment (spec §4.8). Workers have no git authority; Control alone
commits. This module gives Control the checks that make that enforceable when
the worktree shares `.git/` with the repo: snapshot/restore git-control state,
detect drift, compute the true changed-path set (tracked changes + new
non-ignored files -- gitignored churn is deliberately excluded, see
changed_paths' own comment below for why), and commit ONLY owned paths with a
commit==reviewed-diff verification. Recovery never touches the working tree.
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

def _split0(s: str) -> list[str]:
    return [p for p in s.split("\0") if p]

def changed_paths(repo: Path, baseline_ref: str) -> set[str]:
    # Ignored files are INTENTIONALLY EXCLUDED from the changed-path set that
    # scope checks operate on. The project's own .gitignore is treated as the
    # authoritative declaration of "churn, not signal":
    #   1. It can never be committed anyway -- commit_owned() only ever
    #      stages/commits the caller's declared `owned` set, so an ignored
    #      path can't slip into a commit regardless of whether it shows up
    #      here.
    #   2. It is expected runtime churn, not agent misbehavior -- test/build
    #      caches (.pytest_cache/, __pycache__/, ...) and agent scratch
    #      (.remember/, .claude/, .codex/) all land in a run workspace
    #      unavoidably. A prior fix (superseded) tried to hand-whitelist
    #      known scratch prefixes instead of trusting .gitignore; a live
    #      end-to-end run proved that approach is unbounded whack-a-mole --
    #      a codex worker's own `pytest` run created `.pytest_cache/`, which
    #      the whitelist didn't cover, and it still false-flagged as
    #      out-of-scope.
    #   3. A sensitive ignored file (a leaked .env/secret) is not this
    #      function's problem -- spec §7's data-egress boundary (SKILL.md's
    #      Security & data egress section) is what keeps such paths out of a
    #      non-first-party worker's readable view *before* dispatch, so they
    #      should not be reachable to leak in the first place.
    # Trusting .gitignore completely (rather than re-deriving a parallel
    # exclusion list) loses no real coverage: a mutated TRACKED file, or a
    # NEW file that is NOT gitignored, is still returned below and still
    # reaches classify_scope() as a real out-of-scope candidate.
    # -z + _split0 on every view (not a bare whitespace .split()) so a path
    # containing a space is never shattered into two paths.
    tracked = _split0(_git(repo, "diff", "--name-only", "-z", baseline_ref))
    untracked = _split0(_git(repo, "ls-files", "--others", "--exclude-standard", "-z"))
    return set(tracked) | set(untracked)

def classify_scope(changed: set[str], owned: set[str]) -> set[str]:
    # `changed` (from changed_paths() above) already excludes ignored files,
    # so a bare set difference is enough here -- no per-path filtering needed.
    return set(changed) - set(owned)

def _is_ignored(repo: Path, path: str) -> bool:
    try:
        r = subprocess.run(["git", "check-ignore", "-q", path], cwd=repo)
    except OSError as exc:
        # Sibling of _git's guard above: this call bypasses _git() (no
        # stdout/stderr capture needed, just the exit code) but the same
        # nonexistent/inaccessible repo raises the same raw
        # FileNotFoundError/NotADirectoryError/OSError before git even
        # spawns -- never let that leak past this module's typed-error
        # contract.
        raise ContainmentError(f"git invocation failed in {repo}: {exc}") from exc
    return r.returncode == 0

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
    # -z + _split0, not a bare .split(), so a committed path containing a
    # space is read back whole instead of shattered into two paths (which
    # would falsely trip the commit==reviewed-diff check just below).
    committed = set(_split0(_git(repo, "show", "--name-only", "-z", "--format=", sha)))
    if committed != set(owned):
        raise ContainmentError(
            f"commit contents {sorted(committed)} != reviewed owned diff {sorted(owned)} "
            f"— halt, not a completed task (spec §4.8 commit==reviewed-diff)")
    return sha
