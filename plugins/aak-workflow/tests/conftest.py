from __future__ import annotations
import subprocess
from pathlib import Path
import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent

@pytest.fixture(scope="session")
def plugin_root() -> Path:
    return PLUGIN_ROOT

def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True,
        capture_output=True, text=True,
    ).stdout

@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    """A real, isolated git repo with one baseline commit on a feature branch."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "seed.txt").write_text("baseline\n", encoding="utf-8")
    _git(repo, "add", "seed.txt")
    _git(repo, "commit", "-q", "-m", "seed")
    return repo

@pytest.fixture()
def git(git_repo):
    def run(*args: str) -> str:
        return _git(git_repo, *args)
    return run
