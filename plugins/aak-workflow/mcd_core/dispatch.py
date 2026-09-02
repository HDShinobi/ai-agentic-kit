"""Run a worker CLI headless with two independent bounds (spec §6.1):
a hard wall-clock deadline (never extended) and an activity-aware idle detector.
Prevention: stdin=/dev/null by default (Ruling B: a piped prompt file instead,
for adapters whose CLI reads its prompt from stdin — e.g. codex); env scrubbed
of remote creds + base-url override, with CI/GIT_TERMINAL_PROMPT/NO_COLOR set
so credential/stdin prompts die fast. On trip: kill the whole process group
(SIGTERM→grace→SIGKILL), reap, capture partial stdout. This is a PROCESS
FAILURE (FAILED_HANG), never BLOCKED.
"""
from __future__ import annotations
import os, signal, subprocess, time, threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .errors import DispatchError

# Removed from the worker env: no remote credential can reach a worker, and no
# global base-url override may leak first-party traffic to a foreign endpoint.
WORKER_ENV_SCRUB: tuple[str, ...] = (
    "GITHUB_TOKEN", "GH_TOKEN", "GIT_ASKPASS", "SSH_AUTH_SOCK",
    "ANTHROPIC_BASE_URL", "OPENAI_BASE_URL",
)
_ENV_SET = {"CI": "1", "GIT_TERMINAL_PROMPT": "0", "NO_COLOR": "1",
            "GIT_SSH_COMMAND": "ssh -o BatchMode=yes"}
_GRACE_SEC = 10.0

@dataclass
class DispatchOutcome:
    stdout: str
    exit_code: int | None
    tripped: str | None                 # None | "wall" | "idle"
    forensics: dict = field(default_factory=dict)

def _worker_env(base: dict[str, str] | None) -> dict[str, str]:
    env = dict(base if base is not None else os.environ)
    for k in WORKER_ENV_SCRUB:
        env.pop(k, None)
    env.update(_ENV_SET)
    return env

def _kill_group(proc: subprocess.Popen) -> None:
    try:
        pgid = os.getpgid(proc.pid)
    except ProcessLookupError:
        return
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + _GRACE_SEC
    while time.monotonic() < deadline and proc.poll() is None:
        time.sleep(0.05)
    if proc.poll() is None:
        try:
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        proc.wait(timeout=5)            # reap; no zombies
    except subprocess.TimeoutExpired:
        pass

def run_worker(argv: list[str], *, cwd: Path, wall_sec: int, idle_sec: int,
               prompt_file: Path, env: dict[str, str] | None = None,
               poll: float = 0.05,
               activity_probe: Callable[[int], bool] | None = None,
               stdin_file: Path | None = None) -> DispatchOutcome:
    chunks: list[str] = []
    lock = threading.Lock()
    last_activity = time.monotonic()

    # Ruling B: most adapters take the prompt file as a CLI arg, so the child's
    # stdin stays /dev/null (the hang-prevention default — never attach a
    # terminal/pipe a worker could block reading from). codex instead reads its
    # prompt from stdin, so when the caller passes stdin_file we open it and
    # hand the child that fd directly; reading a finite file yields EOF on its
    # own, so this stays hang-safe. The handle is closed right after Popen()
    # returns — the child holds its own dup'd fd, so closing ours doesn't
    # affect it.
    stdin_source = open(stdin_file, "rb") if stdin_file is not None else subprocess.DEVNULL
    try:
        try:
            proc = subprocess.Popen(
                argv, cwd=str(cwd), stdin=stdin_source,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, env=_worker_env(env), start_new_session=True,
            )
        except OSError as exc:
            # Bad argv[0] (typo, CLI not on PATH) or another spawn-time OS
            # failure: surface as the typed error the dispatch interface
            # declares, never a raw FileNotFoundError/OSError traceback.
            raise DispatchError(f"failed to spawn worker {argv[0]!r}: {exc}") from exc
    finally:
        if stdin_file is not None:
            stdin_source.close()

    def _drain() -> None:
        nonlocal last_activity
        assert proc.stdout is not None
        for line in proc.stdout:        # independent reader — no pipe deadlock
            with lock:
                chunks.append(line)
                last_activity = time.monotonic()
    reader = threading.Thread(target=_drain, daemon=True)
    reader.start()

    start = time.monotonic()
    tripped: str | None = None
    while proc.poll() is None:
        now = time.monotonic()
        if now - start >= wall_sec:
            tripped = "wall"; break
        with lock:
            quiet_for = now - last_activity
        if quiet_for >= idle_sec:
            busy = activity_probe(proc.pid) if activity_probe else _default_busy(proc.pid)
            if busy:
                with lock:
                    last_activity = now  # genuine work resets the idle clock
            else:
                tripped = "idle"; break
        time.sleep(poll)

    if tripped:
        _kill_group(proc)
    reader.join(timeout=2)
    with lock:
        stdout = "".join(chunks)
    exit_code = proc.poll()
    forensics = {"which": tripped, "elapsed_sec": round(time.monotonic() - start, 3),
                 "argv0": argv[0], "prompt_file": str(prompt_file)} if tripped else {}
    return DispatchOutcome(stdout=stdout, exit_code=exit_code,
                           tripped=tripped, forensics=forensics)

def _default_busy(pid: int) -> bool:
    """Best-effort liveness: is the process group doing CPU/IO work? Falls back
    to True (assume busy) when the platform tool is unavailable — safer to let
    the wall clock be the true bound than to kill a healthy silent build."""
    try:
        pgid = os.getpgid(pid)
    except ProcessLookupError:
        return False
    out = subprocess.run(["ps", "-o", "%cpu=", "-g", str(pgid)],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return True
    return any(float(v) > 1.0 for v in out.stdout.split() if v.strip())
