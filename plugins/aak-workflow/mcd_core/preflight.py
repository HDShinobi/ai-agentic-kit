"""Preflight: probe each referenced adapter for two INDEPENDENT facts — binary
present? and auth present? — mapping to distinct outcomes (spec §4.4). Never
mutates anything. A runtime failure during dispatch is NOT a preflight case
(that always escalates, §6).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Mapping
from .adapters import ADAPTERS
from .config import RoleBinding

# Adapters whose auth is a logged-in first-party session, not an env key.
_SESSION_AUTH = {"claude", "codex", "gemini"}

@dataclass(frozen=True)
class PreflightResult:
    outcome: str   # "dispatch" | "degrade" | "escalate"
    reason: str

def _auth_present(binding: RoleBinding, secrets: Mapping[str, str],
                  env: Mapping[str, str]) -> bool:
    key_env = secrets.get(binding.cli)
    if key_env:
        return bool(env.get(key_env))
    # No configured key_env: first-party session CLIs are treated as authed once
    # their binary is present (they carry their own login); a multi-model shell
    # with no key configured is treated as unauthed intent.
    return binding.cli in _SESSION_AUTH

def probe(binding: RoleBinding, secrets: Mapping[str, str], *,
          which: Callable[[str], str | None], env: Mapping[str, str],
          on_missing_auth: str = "escalate") -> PreflightResult:
    adapter = ADAPTERS.get(binding.cli)
    binary_name = adapter.resolved_binary if adapter is not None else binding.cli
    binary = which(binary_name)
    if binary is None:
        return PreflightResult("degrade",
            f"{binding.cli}: binary absent — degrade to {binding.cli}→subagent (Golden Rule #1)")
    if _auth_present(binding, secrets, env):
        return PreflightResult("dispatch", f"{binding.cli}: binary + auth present")
    if on_missing_auth == "degrade":
        return PreflightResult("degrade", f"{binding.cli}: auth absent — degrade (opted in)")
    return PreflightResult("escalate",
        f"{binding.cli}: binary present but auth absent — a configured-but-unauthed CLI "
        f"signals intent to use it; escalate rather than silently change which model runs")
