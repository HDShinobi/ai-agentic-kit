from __future__ import annotations
from pathlib import Path
import subprocess
import pytest
from mcd_core.containment import (
    snapshot_git_state, detect_git_drift, restore_git_state,
    changed_paths, classify_scope, commit_owned,
)
from mcd_core.errors import ContainmentError

def _g(repo, *a): return subprocess.run(["git", *a], cwd=repo, check=True,
                                        capture_output=True, text=True).stdout

def test_worker_created_commit_is_detected_and_restored(git_repo, git):
    before = snapshot_git_state(git_repo)
    (git_repo / "rogue.txt").write_text("x\n", encoding="utf-8")   # a rogue worker...
    git("add", "rogue.txt"); git("commit", "-q", "-m", "rogue commit")
    drift = detect_git_drift(git_repo, before)
    assert drift                                  # HEAD moved
    restore_git_state(git_repo, before)
    assert git("rev-parse", "HEAD").strip() == before.head
    # working tree is NOT touched by restore
    assert (git_repo / "rogue.txt").exists()

def test_index_restored_to_snapshot_not_head(git_repo, git):
    (git_repo / "staged.txt").write_text("s\n", encoding="utf-8")
    git("add", "staged.txt")                      # mid-run staged content
    before = snapshot_git_state(git_repo)
    git("reset", "-q")                            # a rogue worker un-stages
    restore_git_state(git_repo, before)
    assert "staged.txt" in _g(git_repo, "diff", "--cached", "--name-only")

def test_changed_paths_excludes_ignored(git_repo, git):
    # RULING REVERSED (supersedes ca8ef0a's tooling-scratch whitelist): a
    # live end-to-end run proved the whitelist is whack-a-mole (a codex
    # worker's own `pytest` run created `.pytest_cache/`, which the
    # whitelist didn't cover, and still false-flagged as out-of-scope). The
    # project's own .gitignore is now the sole authority on what counts as
    # churn: a gitignored path can never be committed anyway (commit_owned()
    # only ever stages the declared `owned` set), and a sensitive ignored
    # file (a leaked .env/secret) is excluded from a non-first-party
    # worker's readable view by SKILL.md's data-egress boundary (spec §7)
    # before it ever runs -- not this check's job. So this test, which used
    # to assert an ignored file WAS detected, is now inverted: it must NOT
    # surface in changed_paths(), and therefore never reaches classify_scope
    # as an out-of-scope candidate either.
    (git_repo / ".gitignore").write_text("*.log\n", encoding="utf-8")
    git("add", ".gitignore"); git("commit", "-q", "-m", "ignore logs")
    base = git("rev-parse", "HEAD").strip()
    (git_repo / "app.py").write_text("code\n", encoding="utf-8")
    (git_repo / "secret.log").write_text("leak\n", encoding="utf-8")   # ignored
    changed = changed_paths(git_repo, base)
    assert "app.py" in changed
    assert "secret.log" not in changed
    assert classify_scope(changed, {"app.py"}) == set()

def test_changed_paths_excludes_gitignored_runtime_churn(git_repo, git):
    # The concrete regression that killed the ca8ef0a whitelist: a real
    # codex worker ran pytest mid-task, which created `.pytest_cache/` --
    # untracked, and not one of the whitelist's hand-picked prefixes
    # (.remember/, .claude/, .codex/), so it still false-flagged as
    # out-of-scope. Excluding ALL gitignored paths (rather than a
    # hand-maintained list of known tool directories) fixes this whole class
    # of bug: whatever the project's own .gitignore already declares as
    # churn is trusted, full stop -- no tool-specific entry required.
    (git_repo / ".gitignore").write_text(".pytest_cache/\n", encoding="utf-8")
    git("add", ".gitignore"); git("commit", "-q", "-m", "ignore pytest cache")
    base = git("rev-parse", "HEAD").strip()
    (git_repo / "app.py").write_text("code\n", encoding="utf-8")   # the worker's real, owned edit
    (git_repo / ".pytest_cache").mkdir()
    (git_repo / ".pytest_cache" / "README.md").write_text("x\n", encoding="utf-8")
    changed = changed_paths(git_repo, base)
    assert not any(p.startswith(".pytest_cache/") for p in changed)
    assert classify_scope(changed, {"app.py"}) == set()

def test_changed_paths_handles_space_in_tracked_filename(git_repo, git):
    # `git diff --name-only <ref>` (no -z) was fed through a bare .split(),
    # which shatters "a b.py" into {"a", "b.py"} on whitespace. Stress the
    # TRACKED-diff branch specifically: commit the space-named file so it is
    # tracked, then diff against the ref that predates it.
    base = git("rev-parse", "HEAD").strip()
    (git_repo / "a b.py").write_text("code\n", encoding="utf-8")
    git("add", "a b.py"); git("commit", "-q", "-m", "add a b.py")
    changed = changed_paths(git_repo, base)
    assert "a b.py" in changed
    assert "a" not in changed and "b.py" not in changed

def test_out_of_scope_detected(git_repo):
    assert classify_scope({"app.py", "other.py"}, {"app.py"}) == {"other.py"}

def test_changed_paths_flags_new_stray_file_outside_owned(git_repo, git):
    # A brand-new, NON-ignored file outside owned scope is exactly what this
    # check exists to catch -- still caught after the ruling reversal above.
    base = git("rev-parse", "HEAD").strip()
    (git_repo / "stray.py").write_text("x\n", encoding="utf-8")   # untracked, not gitignored
    changed = changed_paths(git_repo, base)
    assert "stray.py" in changed
    assert classify_scope(changed, {"app.py"}) == {"stray.py"}

def test_changed_paths_flags_modified_tracked_file_outside_owned(git_repo, git):
    # A modified TRACKED file outside owned scope is likewise still caught --
    # excluding ignored files never weakens tracked-file detection, since the
    # tracked-diff branch of changed_paths() is untouched by this change.
    (git_repo / "other.py").write_text("v1\n", encoding="utf-8")
    git("add", "other.py"); git("commit", "-q", "-m", "add other.py")
    base = git("rev-parse", "HEAD").strip()
    (git_repo / "other.py").write_text("v2\n", encoding="utf-8")
    changed = changed_paths(git_repo, base)
    assert "other.py" in changed
    assert classify_scope(changed, {"app.py"}) == {"other.py"}

def test_commit_owned_only_owned_paths(git_repo, git):
    (git_repo / "a.py").write_text("a\n", encoding="utf-8")
    (git_repo / "b.py").write_text("b\n", encoding="utf-8")
    git("add", "b.py")                            # pre-existing user-staged work
    sha = commit_owned(git_repo, ["a.py"], "feat: add a")
    files = _g(git_repo, "show", "--name-only", "--format=", sha).split()
    assert files == ["a.py"]                       # b.py NOT absorbed

def test_commit_owned_handles_space_in_filename(git_repo, git):
    # The post-commit verification (`committed == set(owned)`) read back
    # `git show --name-only --format=` through a bare .split(), which shatters
    # "a b.py" into {"a", "b.py"} -- that mismatch would wrongly raise
    # ContainmentError even though the commit itself is correct.
    (git_repo / "a b.py").write_text("code\n", encoding="utf-8")
    sha = commit_owned(git_repo, ["a b.py"], "feat: add a b")
    out = _g(git_repo, "show", "--name-only", "-z", "--format=", sha)
    assert [p for p in out.split("\0") if p] == ["a b.py"]

def test_commit_owned_rejects_ignored_without_force(git_repo, git):
    (git_repo / ".gitignore").write_text("gen/\n", encoding="utf-8")
    git("add", ".gitignore"); git("commit", "-q", "-m", "ignore gen")
    (git_repo / "gen").mkdir(); (git_repo / "gen" / "x.py").write_text("g\n", encoding="utf-8")
    with pytest.raises(ContainmentError, match="ignored"):
        commit_owned(git_repo, ["gen/x.py"], "feat: gen")
    sha = commit_owned(git_repo, ["gen/x.py"], "feat: gen", force_add=["gen/x.py"])
    assert "gen/x.py" in _g(git_repo, "show", "--name-only", "--format=", sha).split()
