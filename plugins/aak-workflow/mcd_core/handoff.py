"""Parse the fixed handoff block Control relies on. Worker output is untrusted
data: only this block is parsed. A handoff is a SUCCESS only when the worker
exited 0 AND emitted the `END OF HANDOFF` sentinel (spec §4.6, §6.1) — a
sentinel from a process that exited non-zero (killed on timeout, crashed) is
diagnostic output, not a result.
"""
from __future__ import annotations
from dataclasses import dataclass
from .errors import HandoffError

SENTINEL = "END OF HANDOFF"
_FIELDS = {"status": "Status:", "role": "Role:", "model": "Model:",
           "disposition": "Disposition:", "verification": "Verification:"}

@dataclass(frozen=True)
class Handoff:
    status: str
    role: str
    model: str
    changed_paths: list[str]
    disposition: str | None
    verification: str
    raw: str

def _field(text: str, prefix: str) -> str | None:
    for line in text.splitlines():
        if line.strip().startswith(prefix):
            return line.split(prefix, 1)[1].strip()
    return None

def parse_handoff(stdout: str, exit_code: int) -> Handoff:
    if exit_code != 0:
        raise HandoffError(f"worker exit {exit_code} — not a success even if a "
                           f"handoff block is present (§6.1)")
    if SENTINEL not in stdout:
        raise HandoffError("missing END OF HANDOFF sentinel — output truncated "
                           "mid-write; retry/escalate, never parse (§4.6)")
    status = _field(stdout, _FIELDS["status"])
    if not status:
        raise HandoffError("handoff has no Status: line")
    raw_paths = _field(stdout, "Changed paths:") or ""
    changed = [p.strip() for p in raw_paths.replace(",", " ").split() if p.strip()]
    return Handoff(
        status=status,
        role=_field(stdout, _FIELDS["role"]) or "",
        model=_field(stdout, _FIELDS["model"]) or "",
        changed_paths=changed,
        disposition=_field(stdout, _FIELDS["disposition"]),
        verification=_field(stdout, _FIELDS["verification"]) or "",
        raw=stdout,
    )
