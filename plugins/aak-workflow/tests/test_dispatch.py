from __future__ import annotations
import sys, os
from pathlib import Path
import pytest
from mcd_core.dispatch import run_worker, WORKER_ENV_SCRUB
from mcd_core.errors import DispatchError

FAKES = Path(__file__).resolve().parent / "fakes"

def _run(script, *extra, wall=30, idle=30, activity_probe=None, cwd=None, stdin_file=None):
    return run_worker(
        [sys.executable, str(FAKES / script), *extra],
        cwd=cwd or FAKES, wall_sec=wall, idle_sec=idle,
        prompt_file=FAKES / "unused.txt", poll=0.02, activity_probe=activity_probe,
        stdin_file=stdin_file,
    )

def test_ok_worker_returns_stdout_exit0():
    out = _run("worker_ok.py")
    assert out.tripped is None and out.exit_code == 0
    assert "END OF HANDOFF" in out.stdout

def test_idle_hang_trips_idle_and_is_killed():
    out = _run("worker_hang.py", wall=30, idle=1, activity_probe=lambda pid: False)
    assert out.tripped == "idle"
    assert out.exit_code is None or out.exit_code != 0
    assert "which" in out.forensics and out.forensics["which"] == "idle"

def test_busy_silent_worker_not_tripped_by_idle():
    # No stdout for ~2s, but activity_probe reports the process group is busy.
    out = _run("worker_busy.py", "2", wall=30, idle=1, activity_probe=lambda pid: True)
    assert out.tripped is None
    assert "END OF HANDOFF" in out.stdout

def test_wall_trip_kills_even_if_busy():
    out = _run("worker_busy.py", "30", wall=1, idle=30, activity_probe=lambda pid: True)
    assert out.tripped == "wall"

def test_env_is_scrubbed_of_remote_creds():
    assert "GITHUB_TOKEN" in WORKER_ENV_SCRUB
    assert "ANTHROPIC_BASE_URL" in WORKER_ENV_SCRUB

# --- Ruling B: codex-style adapters read their prompt from stdin, not a CLI arg.
# run_worker must be able to pipe a prompt file into the child's stdin instead of
# always using the DEVNULL hang-prevention default.

def test_stdin_file_is_piped_to_worker(tmp_path):
    prompt = tmp_path / "prompt.txt"
    known = "the quick brown fox — task 7 stdin ruling B\n"
    prompt.write_text(known, encoding="utf-8")
    out = _run("worker_echo_stdin.py", wall=5, idle=5, stdin_file=prompt)
    assert out.tripped is None and out.exit_code == 0
    assert known.strip() in out.stdout
    assert "END OF HANDOFF" in out.stdout

def test_spawn_failure_raises_dispatch_error():
    # Task 7 follow-up: a bad argv[0] (CLI not on PATH) must surface as the
    # typed DispatchError the dispatch interface declares -- not a raw
    # FileNotFoundError/OSError leaking out of subprocess.Popen.
    with pytest.raises(DispatchError):
        run_worker(["/nonexistent/cli-xyz"], cwd=FAKES, wall_sec=5, idle_sec=5,
                   prompt_file=FAKES / "unused.txt")

def test_default_stdin_is_devnull_not_a_hang():
    # stdin_file=None must keep the brief's hang-prevention default: the child's
    # stdin is /dev/null, so a worker that reads stdin gets immediate EOF (empty
    # read), never a hang waiting on an attached terminal/pipe. (The existing
    # worker_ok test above already exercises the DEVNULL path end-to-end; this
    # test additionally proves *what* a worker sees on that fd: EOF, not data.)
    out = _run("worker_echo_stdin.py", wall=5, idle=5, stdin_file=None)
    assert out.tripped is None and out.exit_code == 0
    assert "stdin=\n" in out.stdout
