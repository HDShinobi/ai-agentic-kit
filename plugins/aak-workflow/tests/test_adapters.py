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

def test_codex_argv_has_skip_git_check_and_sandbox_flag():
    # Real invocation (live-verified): non-interactive codex needs
    # --skip-git-repo-check (the workspace is a worktree/nested checkout) and
    # an explicit --sandbox mode -- neither was in the old illustrative argv.
    argv = get_adapter("codex").compose_argv(RoleBinding("codex", "gpt-5.6-terra", None), PF)
    assert "--skip-git-repo-check" in argv
    assert "--sandbox" in argv
    assert argv[-1] == "-"

def test_codex_writable_controls_sandbox_mode():
    # spec §4.5: only the CODE role is workspace-write; PLAN/REVIEW stay read-only.
    ro = get_adapter("codex").compose_argv(RoleBinding("codex", "gpt-5.6-terra", None), PF,
                                           writable=False)
    rw = get_adapter("codex").compose_argv(RoleBinding("codex", "gpt-5.6-terra", None), PF,
                                           writable=True)
    assert ro[ro.index("--sandbox") + 1] == "read-only"
    assert rw[rw.index("--sandbox") + 1] == "workspace-write"

def test_claude_argv_uses_stdin_with_no_positional_prompt():
    # Real invocation (live-verified): claude -p reads its prompt from STDIN --
    # a positional prompt-file path is NOT a reliable file read for it.
    argv = get_adapter("claude").compose_argv(RoleBinding("claude", "opus", None), PF)
    assert argv == ["claude", "-p", "--model", "opus"]
    assert str(PF) not in argv
    assert get_adapter("claude").prompt_via == "stdin"

def test_claude_writable_appends_permission_mode():
    ro = get_adapter("claude").compose_argv(RoleBinding("claude", "opus", None), PF, writable=False)
    rw = get_adapter("claude").compose_argv(RoleBinding("claude", "opus", None), PF, writable=True)
    assert "--permission-mode" not in ro
    assert rw == ["claude", "-p", "--model", "opus", "--permission-mode", "acceptEdits"]

def test_gemini_argv_ignores_effort_but_still_pins_model():
    argv = get_adapter("gemini").compose_argv(RoleBinding("gemini", "gemini-2.x", "high"), PF)
    assert "--model" in argv and "gemini-2.x" in argv
    assert "high" not in argv                      # no fake effort injected
    assert str(PF) in argv
    assert get_adapter("gemini").prompt_via == "arg"

def test_prompt_via_delivery():
    # claude + codex are both live-verified stdin readers; the rest are
    # unverified "arg" adapters (gemini/command-code/kiro/opencode) until
    # confirmed installed.
    for cli in ("codex", "claude"):
        assert get_adapter(cli).prompt_via == "stdin", f"{cli} should deliver prompt via stdin"
    for cli in ("command-code", "opencode", "gemini", "kiro"):
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

def test_resolved_binary():
    assert get_adapter("kiro").resolved_binary == "kiro-cli"
    assert get_adapter("claude").resolved_binary == "claude"
