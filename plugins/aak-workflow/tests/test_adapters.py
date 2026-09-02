from __future__ import annotations
from pathlib import Path
import pytest
from mcd_core.adapters import get_adapter, effort_warnings, ADAPTERS
from mcd_core.config import RoleBinding, DeliveryConfig, Defaults

PF = Path("/work/.aak/prompt.txt")

def test_all_six_adapters_registered():
    assert set(ADAPTERS) == {"claude", "codex", "command-code", "opencode", "gemini", "kiro"}

def test_codex_argv_pins_model_effort_and_uses_stdin():
    argv = get_adapter("codex").compose_argv(RoleBinding("codex", "gpt-5.6-terra", "medium"), PF)
    assert argv[:3] == ["codex", "exec", "-m"]
    assert "gpt-5.6-terra" in argv
    assert "model_reasoning_effort=medium" in " ".join(argv)
    assert argv[-1] == "-"                        # stdin sentinel, argv ends here
    assert str(PF) not in argv                    # prompt file is NOT a CLI arg for codex
    assert get_adapter("codex").prompt_via == "stdin"

def test_gemini_argv_ignores_effort_but_still_pins_model():
    argv = get_adapter("gemini").compose_argv(RoleBinding("gemini", "gemini-2.x", "high"), PF)
    assert "--model" in argv and "gemini-2.x" in argv
    assert "high" not in argv                      # no fake effort injected
    assert str(PF) in argv
    assert get_adapter("gemini").prompt_via == "arg"

def test_prompt_via_delivery():
    assert get_adapter("codex").prompt_via == "stdin"
    for cli in ("claude", "command-code", "opencode", "gemini", "kiro"):
        assert get_adapter(cli).prompt_via == "arg", f"{cli} should deliver prompt via arg"

def test_unknown_cli_rejected():
    with pytest.raises(Exception):
        get_adapter("bogus-cli")

def test_effort_on_effortless_adapter_warns():
    cfg = DeliveryConfig(
        roles={"review": RoleBinding("gemini", "gemini-2.x", "medium")},
        defaults=Defaults(), timeouts={}, secrets={})
    warns = effort_warnings(cfg)
    assert any("review" in w and "gemini" in w for w in warns)
