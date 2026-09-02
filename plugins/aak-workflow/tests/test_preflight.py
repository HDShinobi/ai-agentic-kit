from __future__ import annotations
from mcd_core.preflight import probe, PreflightResult
from mcd_core.config import RoleBinding

def _which(present: set[str]):
    return lambda name: f"/usr/bin/{name}" if name in present else None

def test_binary_and_auth_present_dispatch():
    r = probe(RoleBinding("command-code", "glm-5.2"), {"command-code": "CC_KEY"},
              which=_which({"command-code"}), env={"CC_KEY": "x"})
    assert r.outcome == "dispatch"

def test_binary_absent_degrades():
    r = probe(RoleBinding("command-code", "glm-5.2"), {"command-code": "CC_KEY"},
              which=_which(set()), env={"CC_KEY": "x"})
    assert r.outcome == "degrade"

def test_binary_present_auth_absent_escalates_by_default():
    r = probe(RoleBinding("command-code", "glm-5.2"), {"command-code": "CC_KEY"},
              which=_which({"command-code"}), env={})
    assert r.outcome == "escalate"

def test_binary_present_auth_absent_degrades_when_opted_in():
    r = probe(RoleBinding("command-code", "glm-5.2"), {"command-code": "CC_KEY"},
              which=_which({"command-code"}), env={}, on_missing_auth="degrade")
    assert r.outcome == "degrade"

def test_first_party_needs_no_key_env():
    # claude/codex/gemini report a logged-in session; no key_env configured.
    r = probe(RoleBinding("claude", "opus"), secrets={},
              which=_which({"claude"}), env={})
    assert r.outcome == "dispatch"
