from __future__ import annotations
import pytest
from mcd_core.handoff import parse_handoff, SENTINEL
from mcd_core.errors import HandoffError

def _block(status="DONE", role="review", disposition="ACCEPT", tail=SENTINEL):
    return (f"...work...\nStatus: {status}\nRole: {role}\nModel: opus\n"
            f"Changed paths: src/a.py\nContract coverage: ok\n"
            f"Verification: pytest -> pass\nDeviations:\nUnresolved:\n"
            f"Disposition: {disposition}\n{tail}\n")

def test_wellformed_block_parses():
    h = parse_handoff(_block(), exit_code=0)
    assert h.status == "DONE" and h.disposition == "ACCEPT"
    assert h.changed_paths == ["src/a.py"]

def test_missing_sentinel_is_truncation():
    with pytest.raises(HandoffError, match="sentinel"):
        parse_handoff(_block(tail="<<cut off"), exit_code=0)

def test_sentinel_present_but_nonzero_exit_is_failure():
    with pytest.raises(HandoffError, match="exit"):
        parse_handoff(_block(), exit_code=137)   # e.g. SIGKILL after timeout

def test_done_transport_with_blocked_disposition():
    h = parse_handoff(_block(disposition="BLOCKED"), exit_code=0)
    assert h.status == "DONE" and h.disposition == "BLOCKED"
