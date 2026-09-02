from __future__ import annotations
import pytest
from mcd_core.identity import canonical_identity, review_differs_from_code
from mcd_core.config import RoleBinding

def test_aliases_collapse_to_one_identity():
    a = canonical_identity("claude", "opus")
    b = canonical_identity("claude", "anthropic/opus")
    assert a == b == "anthropic:opus"

def test_high_suffix_is_part_of_model_not_effort():
    # dely gotcha: a slug ending -high names the model, not the effort flag.
    assert canonical_identity("codex", "gpt-5-high") == "openai:gpt-5-high"
    assert canonical_identity("codex", "gpt-5-high") != canonical_identity("codex", "gpt-5")

def test_review_equals_code_when_same_identity_via_alias():
    code = RoleBinding("claude", "opus")
    review = RoleBinding("claude", "anthropic/opus")
    assert review_differs_from_code(code, review) is False  # must NOT falsely satisfy

def test_review_differs_across_providers():
    code = RoleBinding("codex", "gpt-5.6-terra")
    review = RoleBinding("claude", "opus")
    assert review_differs_from_code(code, review) is True
