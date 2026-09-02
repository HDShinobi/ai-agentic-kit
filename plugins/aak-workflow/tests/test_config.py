from __future__ import annotations
from pathlib import Path
import textwrap
import pytest
from mcd_core.config import load_delivery_config, DeliveryConfig
from mcd_core.errors import ConfigError

def _write(repo: Path, body: str) -> None:
    (repo / ".aak").mkdir(exist_ok=True)
    (repo / ".aak" / "delivery.yml").write_text(textwrap.dedent(body), encoding="utf-8")

def test_absent_config_is_inert(tmp_path):
    assert load_delivery_config(tmp_path) is None

def test_minimal_first_party_config(tmp_path):
    _write(tmp_path, """
      roles:
        plan:   {cli: gemini, model: gemini-2.x}
        code:   {cli: codex,  model: gpt-5.6-terra, effort: medium}
        review: {cli: claude, model: opus}
      defaults:
        degrade_to: claude-subagent
        review_must_differ_from_code: true
        workspace: worktree
        review_fallback: [review]
      timeouts:
        code: {wall_min: 120, idle_min: 10}
    """)
    cfg = load_delivery_config(tmp_path)
    assert isinstance(cfg, DeliveryConfig)
    assert cfg.roles["code"].cli == "codex"
    assert cfg.roles["code"].effort == "medium"
    assert cfg.roles["review"].effort is None
    assert cfg.defaults.workspace == "worktree"
    assert cfg.defaults.review_must_differ_from_code is True
    assert cfg.timeouts["code"].wall_sec == 120 * 60
    assert cfg.timeouts["code"].idle_sec == 10 * 60

def test_unknown_top_level_key_rejected(tmp_path):
    _write(tmp_path, "roles: {code: {cli: codex, model: x}}\nbogus: 1\n")
    with pytest.raises(ConfigError, match="unknown"):
        load_delivery_config(tmp_path)

def test_invalid_workspace_rejected(tmp_path):
    _write(tmp_path, """
      roles: {code: {cli: codex, model: x}}
      defaults: {workspace: sandbox}
    """)
    with pytest.raises(ConfigError, match="workspace"):
        load_delivery_config(tmp_path)

def test_role_missing_required_fields_rejected(tmp_path):
    _write(tmp_path, "roles: {code: {cli: codex}}\n")   # no model
    with pytest.raises(ConfigError, match="model"):
        load_delivery_config(tmp_path)

def test_empty_file_is_all_defaults(tmp_path):
    _write(tmp_path, "")
    cfg = load_delivery_config(tmp_path)
    assert isinstance(cfg, DeliveryConfig)
    assert cfg.roles == {}

def test_invalid_on_missing_auth_rejected(tmp_path):
    _write(tmp_path, """
      roles: {code: {cli: codex, model: x}}
      defaults: {on_missing_auth: nonsense}
    """)
    with pytest.raises(ConfigError, match="on_missing_auth"):
        load_delivery_config(tmp_path)

def test_non_mapping_roles_rejected(tmp_path):
    _write(tmp_path, "roles: oops\n")
    with pytest.raises(ConfigError, match="roles"):
        load_delivery_config(tmp_path)

def test_non_numeric_timeout_rejected(tmp_path):
    _write(tmp_path, """
      roles: {code: {cli: codex, model: x}}
      timeouts:
        code: {wall_min: "ten", idle_min: 5}
    """)
    with pytest.raises(ConfigError, match="wall_min"):
        load_delivery_config(tmp_path)
