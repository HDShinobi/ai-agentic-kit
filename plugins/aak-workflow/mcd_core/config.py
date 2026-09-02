"""Load and validate .aak/delivery.yml — the per-project role→CLI+model map.

Absent file → None (the skill is inert). Malformed content or unknown keys →
ConfigError (fail closed; never guess a default that changes which model runs).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

from .errors import ConfigError

CONFIG_REL = Path(".aak") / "delivery.yml"
_WORKSPACE = {"worktree", "shared"}
_ON_MISSING_AUTH = {"escalate", "degrade"}
_TOP_KEYS = {"roles", "defaults", "timeouts", "secrets"}
_ROLE_KEYS = {"cli", "model", "effort"}
_DEFAULT_KEYS = {"degrade_to", "review_must_differ_from_code", "workspace",
                 "review_fallback", "on_missing_auth"}

@dataclass(frozen=True)
class RoleBinding:
    cli: str
    model: str
    effort: str | None = None

@dataclass(frozen=True)
class TimeoutPolicy:
    wall_sec: int
    idle_sec: int

@dataclass(frozen=True)
class Defaults:
    degrade_to: str = "claude-subagent"
    review_must_differ_from_code: bool = True
    workspace: str = "worktree"
    review_fallback: list[str] = field(default_factory=list)
    on_missing_auth: str = "escalate"

@dataclass(frozen=True)
class DeliveryConfig:
    roles: dict[str, RoleBinding]
    defaults: Defaults
    timeouts: dict[str, TimeoutPolicy]
    secrets: dict[str, str]

def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ConfigError(msg)

def _reject_unknown(got, allowed, where: str) -> None:
    extra = set(got) - allowed
    _require(not extra, f"unknown key(s) in {where}: {sorted(extra)}")

def load_delivery_config(repo_root: Path) -> DeliveryConfig | None:
    path = Path(repo_root) / CONFIG_REL
    if not path.is_file():
        return None
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - env-specific
        raise ConfigError(
            "pyyaml is required to read .aak/delivery.yml — "
            "`pip install -r requirements-dev.txt`"
        ) from exc
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    raw = {} if raw is None else raw
    _require(isinstance(raw, dict), "delivery.yml must be a mapping")
    _reject_unknown(raw, _TOP_KEYS, "delivery.yml")

    roles_raw = raw.get("roles")
    roles_raw = {} if roles_raw is None else roles_raw
    _require(isinstance(roles_raw, dict), "roles must be a mapping")
    roles: dict[str, RoleBinding] = {}
    for name, spec in roles_raw.items():
        _require(isinstance(spec, dict), f"role {name!r} must be a mapping")
        _reject_unknown(spec, _ROLE_KEYS, f"role {name!r}")
        _require("cli" in spec, f"role {name!r} missing cli")
        _require("model" in spec, f"role {name!r} missing model")
        roles[name] = RoleBinding(str(spec["cli"]), str(spec["model"]),
                                  spec.get("effort"))

    d = raw.get("defaults")
    d = {} if d is None else d
    _require(isinstance(d, dict), "defaults must be a mapping")
    _reject_unknown(d, _DEFAULT_KEYS, "defaults")
    workspace = d.get("workspace", "worktree")
    _require(workspace in _WORKSPACE, f"defaults.workspace must be one of {_WORKSPACE}")
    on_missing_auth = d.get("on_missing_auth", "escalate")
    _require(on_missing_auth in _ON_MISSING_AUTH,
             f"defaults.on_missing_auth must be one of {_ON_MISSING_AUTH}")
    defaults = Defaults(
        degrade_to=str(d.get("degrade_to", "claude-subagent")),
        review_must_differ_from_code=bool(d.get("review_must_differ_from_code", True)),
        workspace=workspace,
        review_fallback=list(d.get("review_fallback", []) or []),
        on_missing_auth=on_missing_auth,
    )

    timeouts_raw = raw.get("timeouts")
    timeouts_raw = {} if timeouts_raw is None else timeouts_raw
    _require(isinstance(timeouts_raw, dict), "timeouts must be a mapping")
    timeouts: dict[str, TimeoutPolicy] = {}
    for role, spec in timeouts_raw.items():
        _require(isinstance(spec, dict), f"timeouts.{role} must be a mapping")
        _reject_unknown(spec, {"wall_min", "idle_min"}, f"timeouts.{role}")
        wm, im = spec.get("wall_min"), spec.get("idle_min")
        for label, v in (("wall_min", wm), ("idle_min", im)):
            _require(isinstance(v, int) and not isinstance(v, bool),
                     f"timeouts.{role}.{label} must be an integer")
        wall, idle = int(wm), int(im)
        _require(wall > 0 and idle > 0, f"timeouts.{role} needs positive wall_min/idle_min")
        timeouts[role] = TimeoutPolicy(wall * 60, idle * 60)

    secrets_raw = raw.get("secrets")
    secrets_raw = {} if secrets_raw is None else secrets_raw
    _require(isinstance(secrets_raw, dict), "secrets must be a mapping")
    secrets = {str(k): str(v) for k, v in secrets_raw.items()}
    return DeliveryConfig(roles=roles, defaults=defaults,
                          timeouts=timeouts, secrets=secrets)
