from __future__ import annotations
from pathlib import Path
import subprocess
import pytest
from mcd_core.containment import (
    snapshot_git_state, detect_git_drift, restore_git_state,
    changed_paths, classify_scope, commit_owned, is_tooling_scratch,
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

def test_changed_paths_includes_ignored(git_repo, git):
    (git_repo / ".gitignore").write_text("*.log\n", encoding="utf-8")
    git("add", ".gitignore"); git("commit", "-q", "-m", "ignore logs")
    base = git("rev-parse", "HEAD").strip()
    (git_repo / "app.py").write_text("code\n", encoding="utf-8")
    (git_repo / "secret.log").write_text("leak\n", encoding="utf-8")   # ignored
    changed = changed_paths(git_repo, base)
    assert "app.py" in changed and "secret.log" in changed   # status-only check would miss the .log

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

def test_classify_scope_excludes_worker_tooling_scratch(git_repo):
    # Real end-to-end run finding: worker runtimes (Claude's Remember plugin,
    # a codex session) write gitignored scratch into the workspace during
    # dispatch. That scratch is neither owned nor a scope violation -- it can
    # never enter a commit because commit_owned() only stages the owned set.
    changed = {"app.py", ".remember/logs/x.log", ".claude/foo", ".codex/session"}
    assert classify_scope(changed, {"app.py"}) == set()

def test_classify_scope_still_flags_ignored_file_outside_whitelist(git_repo):
    # Ruling A preserved: a real ignored file OUTSIDE the tooling-scratch
    # whitelist (e.g. a leaked .env/secret) still escalates as out-of-scope.
    assert classify_scope({"app.py", ".env"}, {"app.py"}) == {".env"}
    assert classify_scope({"app.py", "secret.log"}, {"app.py"}) == {"secret.log"}

def test_classify_scope_still_flags_aak_config_dir(git_repo):
    # .aak/ is deliberately NOT whitelisted -- it holds delivery.yml, so a
    # worker writing there must still be flagged (config integrity).
    assert classify_scope({"app.py", ".aak/delivery.yml"}, {"app.py"}) == {".aak/delivery.yml"}

def test_classify_scope_still_flags_normal_out_of_scope_file(git_repo):
    assert classify_scope({"app.py", "other.py"}, {"app.py"}) == {"other.py"}

def test_is_tooling_scratch_prefix_match():
    assert is_tooling_scratch(".remember/logs/x.log")
    assert is_tooling_scratch(".claude/foo")
    assert is_tooling_scratch(".codex/session")

def test_is_tooling_scratch_exact_dir_match():
    assert is_tooling_scratch(".remember")
    assert is_tooling_scratch(".claude")
    assert is_tooling_scratch(".codex")

def test_is_tooling_scratch_strips_leading_dot_slash():
    assert is_tooling_scratch("./.remember/logs/x.log")
    assert is_tooling_scratch("./.claude")

def test_is_tooling_scratch_non_match():
    assert not is_tooling_scratch(".aak/delivery.yml")
    assert not is_tooling_scratch(".env")
    assert not is_tooling_scratch("other.py")
    assert not is_tooling_scratch(".git/HEAD")
    # a lookalike name sharing the prefix string but not actually inside
    # that directory must not match.
    assert not is_tooling_scratch(".remember-extra/x")

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
