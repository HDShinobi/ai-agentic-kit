"""Adapter registry — how to launch each CLI HEADLESS. The protocol core is
adapter-agnostic; a new CLI is a new row. Prompts go to a file inside the
workspace, never inline in a shell arg. Model + effort (where supported) are
pinned on every dispatch (spec §4.3). NOTE: the §4.3 table is illustrative;
exact flags per CLI *version* are pinned here and updated as versions drift.
`claude` and `codex` below are LIVE-VERIFIED against real installed CLIs;
`command-code`/`opencode`/`gemini`/`kiro` remain illustrative (not installed
on the verifying machine) and are updated when confirmed.

Prompt delivery (Ruling B): each adapter declares `prompt_via` — "arg" means
the prompt file path is passed as a CLI argument; "stdin" means the dispatcher
must open the prompt file and pipe its contents to the child process's stdin.
Both `claude` (`claude -p` reads its prompt from stdin — a positional path is
NOT a reliable file read for it) and `codex` (`codex exec -m <model> -`) are
"stdin" adapters; every other adapter here takes the prompt file path as a
trailing CLI arg (unverified — see module note above).

Write capability (spec §4.5): only the CODE role is workspace-write; PLAN and
REVIEW are read-only. `compose_argv` takes a `writable` keyword so the
dispatcher can tell an adapter which case this dispatch is. Only `claude`
(`--permission-mode acceptEdits` when writable) and `codex` (`--sandbox
workspace-write` vs `read-only`) act on it today; every other adapter accepts
and ignores the keyword so the dispatcher can call all six uniformly.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from .config import RoleBinding, DeliveryConfig
from .errors import ConfigError

@dataclass(frozen=True)
class Adapter:
    id: str
    effort_supported: bool
    prompt_via: str            # "arg" | "stdin"
    _argv: Callable[..., list[str]]
    binary: str | None = None  # actual executable name, if it differs from `id` (e.g. kiro -> kiro-cli)

    def compose_argv(self, binding: RoleBinding, prompt_file: Path, *,
                     writable: bool = False) -> list[str]:
        return self._argv(binding, prompt_file, writable=writable)

    @property
    def resolved_binary(self) -> str:
        return self.binary or self.id

def _claude(b: RoleBinding, pf: Path, *, writable: bool = False) -> list[str]:
    # Live-verified: claude -p reads its prompt from STDIN, not a positional
    # arg -- pf is unused here (kept for the uniform adapter signature); the
    # dispatcher pipes the prompt file into stdin via prompt_via == "stdin".
    # model pinned via --model; effort via model tier (not a flag) → not a CLI arg here.
    argv = ["claude", "-p", "--model", b.model]
    if writable:
        argv += ["--permission-mode", "acceptEdits"]   # spec §4.5: CODE only
    return argv

def _codex(b: RoleBinding, pf: Path, *, writable: bool = False) -> list[str]:
    # Live-verified non-interactive invocation. codex reads the prompt from
    # stdin — the dispatcher pipes the prompt file into the child's stdin when
    # prompt_via == "stdin" (see ADAPTERS below). pf is unused here; the
    # uniform (binding, prompt_file) signature is kept so the dispatcher can
    # call every adapter's compose_argv the same way. cwd is set by the
    # dispatcher's subprocess cwd=, so no -C flag is needed here.
    argv = ["codex", "exec", "-m", b.model]
    if b.effort:
        argv += ["-c", f"model_reasoning_effort={b.effort}"]
    argv += ["--skip-git-repo-check", "--sandbox",
             "workspace-write" if writable else "read-only",   # spec §4.5
             "-"]        # read prompt from stdin; dispatcher pipes the prompt file in
    return argv

def _command_code(b: RoleBinding, pf: Path, *, writable: bool = False) -> list[str]:
    return ["command-code", "-p", "--model", b.model, str(pf)]

def _opencode(b: RoleBinding, pf: Path, *, writable: bool = False) -> list[str]:
    return ["opencode", "run", "--model", b.model, str(pf)]

def _gemini(b: RoleBinding, pf: Path, *, writable: bool = False) -> list[str]:
    return ["gemini", "-p", "--model", b.model, str(pf)]

def _kiro(b: RoleBinding, pf: Path, *, writable: bool = False) -> list[str]:
    return ["kiro-cli", "chat", "--no-interactive", "--trust-all-tools",
            "--model", b.model, str(pf)]

ADAPTERS: dict[str, Adapter] = {
    "claude": Adapter("claude", False, "stdin", _claude),
    "codex": Adapter("codex", True, "stdin", _codex),
    "command-code": Adapter("command-code", False, "arg", _command_code),
    "opencode": Adapter("opencode", False, "arg", _opencode),
    "gemini": Adapter("gemini", False, "arg", _gemini),
    "kiro": Adapter("kiro", False, "arg", _kiro, binary="kiro-cli"),
}

def get_adapter(cli: str) -> Adapter:
    try:
        return ADAPTERS[cli]
    except KeyError as exc:
        raise ConfigError(f"unknown adapter/cli id: {cli!r}; "
                          f"known: {sorted(ADAPTERS)}") from exc

def effort_warnings(cfg: DeliveryConfig) -> list[str]:
    out: list[str] = []
    for role, b in cfg.roles.items():
        ad = ADAPTERS.get(b.cli)
        if b.effort and ad is not None and not ad.effort_supported:
            out.append(f"effort={b.effort!r} set for role {role!r}, but adapter "
                       f"{b.cli!r} has no effort concept — value will be ignored")
    return out
