"""Canonical provider+model identity, established from the TRUSTED side (config
mapping), never from the worker's handoff `Model:` line. REVIEW≠CODE, fallback
selection, and same-model reporting all compare this identity so aliases like
`opus` and `anthropic/opus` cannot falsely satisfy the invariant (spec §4.7).
"""
from __future__ import annotations
from .config import RoleBinding

# The ONLY place cli→provider lives. A multi-model shell (command-code/opencode)
# has no single provider — its identity keys on provider/model in the slug itself.
PROVIDER_BY_CLI: dict[str, str] = {
    "claude": "anthropic",
    "codex": "openai",
    "gemini": "google",
}
_MULTI_MODEL_SHELLS = {"command-code", "opencode"}

def canonical_identity(cli: str, model: str) -> str:
    """Return `provider:model`. Provider comes from a `provider/model` prefix in
    the model string if present, else from the cli. The model slug is lowercased
    but otherwise preserved (a trailing `-high` is part of the slug)."""
    m = model.strip().lower()
    provider: str | None = None
    if "/" in m:                       # e.g. "anthropic/opus", "openrouter/glm-5"
        provider, m = m.split("/", 1)
    if provider is None:
        provider = PROVIDER_BY_CLI.get(cli.strip().lower())
    if provider is None:               # multi-model shell without an explicit prefix
        provider = cli.strip().lower() if cli.strip().lower() in _MULTI_MODEL_SHELLS else "unknown"
    return f"{provider}:{m}"

def review_differs_from_code(code: RoleBinding, review: RoleBinding) -> bool:
    return canonical_identity(code.cli, code.model) != canonical_identity(review.cli, review.model)
