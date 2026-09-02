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

def test_changed_paths_includes_ignored(git_repo, git):
    (git_repo / ".gitignore").write_text("*.log\n", encoding="utf-8")
    git("add", ".gitignore"); git("commit", "-q", "-m", "ignore logs")
    base = git("rev-parse", "HEAD").strip()
    (git_repo / "app.py").write_text("code\n", encoding="utf-8")
    (git_repo / "secret.log").write_text("leak\n", encoding="utf-8")   # ignored
    changed = changed_paths(git_repo, base)
    assert "app.py" in changed and "secret.log" in changed   # status-only check would miss the .log

def test_out_of_scope_detected(git_repo):
    assert classify_scope({"app.py", "other.py"}, {"app.py"}) == {"other.py"}

def test_commit_owned_only_owned_paths(git_repo, git):
    (git_repo / "a.py").write_text("a\n", encoding="utf-8")
    (git_repo / "b.py").write_text("b\n", encoding="utf-8")
    git("add", "b.py")                            # pre-existing user-staged work
    sha = commit_owned(git_repo, ["a.py"], "feat: add a")
    files = _g(git_repo, "show", "--name-only", "--format=", sha).split()
    assert files == ["a.py"]                       # b.py NOT absorbed

def test_commit_owned_rejects_ignored_without_force(git_repo, git):
    (git_repo / ".gitignore").write_text("gen/\n", encoding="utf-8")
    git("add", ".gitignore"); git("commit", "-q", "-m", "ignore gen")
    (git_repo / "gen").mkdir(); (git_repo / "gen" / "x.py").write_text("g\n", encoding="utf-8")
    with pytest.raises(ContainmentError, match="ignored"):
        commit_owned(git_repo, ["gen/x.py"], "feat: gen")
    sha = commit_owned(git_repo, ["gen/x.py"], "feat: gen", force_add=["gen/x.py"])
    assert "gen/x.py" in _g(git_repo, "show", "--name-only", "--format=", sha).split()
