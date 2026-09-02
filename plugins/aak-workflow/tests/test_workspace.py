from __future__ import annotations
from pathlib import Path
import pytest
from mcd_core.workspace import prepare_workspace, overlap_gate, branch_gate
from mcd_core.errors import ContainmentError

def test_worktree_created_on_feature_branch_and_isolated(git_repo, git):
    ws = prepare_workspace(git_repo, "feat/x", workspaces_dir=git_repo.parent / "wt")
    assert ws != git_repo and ws.is_dir()
    # editing in the worktree does not appear in the user's checkout
    (ws / "seed.txt").write_text("worker edit\n", encoding="utf-8")
    assert (git_repo / "seed.txt").read_text() == "baseline\n"

def test_worktree_reused_across_runs(git_repo):
    d = git_repo.parent / "wt"
    a = prepare_workspace(git_repo, "feat/x", workspaces_dir=d)
    b = prepare_workspace(git_repo, "feat/x", workspaces_dir=d)
    assert a == b     # same path reused → caches survive

def test_overlap_gate_flags_owned_dirty_user_path(git_repo):
    (git_repo / "seed.txt").write_text("user is editing\n", encoding="utf-8")
    assert overlap_gate(git_repo, ["seed.txt"]) == ["seed.txt"]
    assert overlap_gate(git_repo, ["other.txt"]) == []

def test_branch_gate_rejects_detached_head(git_repo, git):
    head = git("rev-parse", "HEAD").strip()
    git("checkout", "-q", head)      # detached
    with pytest.raises(ContainmentError, match="detached"):
        branch_gate(git_repo)

def test_shared_mode_returns_repo_root(git_repo):
    assert prepare_workspace(git_repo, "feat/x", workspace_mode="shared") == git_repo
