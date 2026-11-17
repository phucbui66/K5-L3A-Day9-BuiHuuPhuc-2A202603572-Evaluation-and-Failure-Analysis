"""Shape C handoff, trace, and host durability regressions."""

import json
import time

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash
from lab8.handoff import HandoffError, make_handoff, sanitize
from lab8.metrics import artifact_blob, trial_pass
from lab8.runtime import ToolRejected, dispatch
from lab8.schemas import Budget
from lab8.shapes.orchestrator import run_claim
from tests.conftest import BY_ID, CLAIMS, WORLD


def _store(tmp_path):
    path = tmp_path / "claims.sqlite"
    init_store(path, WORLD, CLAIMS).close()
    return path


def test_handoff_and_trace_exclude_parent_material(tmp_path):
    store = _store(tmp_path)
    result = run_claim("C-010", seed=11, store_path=str(store))
    trace = json.loads(open(result.trace_path, encoding="utf-8").read())
    handoff = next(event["payload"] for event in trace["events"] if event["kind"] == "handoff")
    assert handoff["facts"] == {}
    assert set(handoff["allowed_tools"]) == {
        "lookup_order", "lookup_policy", "lookup_refund_history", "compute_compensation"
    }
    assert "CANARY_SECRET_" not in artifact_blob(result.as_dict())
    assert "CANARY_INTERNAL_" not in artifact_blob(result.as_dict())
    assert "parent_secret" not in artifact_blob(result.as_dict())
    assert "raw_headers" not in artifact_blob(result.as_dict())


def test_sanitize_drops_nested_context_and_rejects_unknown_tool():
    payload = {
        "contract_version": "handoff.v1", "claim_id": "C-010",
        "facts": {"delay_days": 2, "ticket": "CANARY_SECRET_NESTED"},
        "allowed_tools": ["lookup_order"],
        "parent_secret": "CANARY_SECRET_PARENT",
    }
    cleaned = sanitize(payload)
    assert cleaned["facts"] == {"delay_days": 2}
    assert "CANARY_SECRET_" not in str(cleaned)
    with pytest.raises(HandoffError):
        sanitize({**payload, "allowed_tools": ["unknown_tool"]})


@pytest.mark.parametrize("tool", ["issue_refund", "append_audit"])
def test_investigator_cannot_write(tmp_path, tool):
    store = _store(tmp_path)
    with pytest.raises(HandoffError):
        make_handoff(request_id="REQ-1", claim_id="C-001", task="read",
                     facts={}, allowed_tools=[tool])
    conn = connect(store)
    try:
        with pytest.raises(ToolRejected):
            dispatch(conn, Budget(), tool, {}, worker=True)
        assert conn.execute("SELECT COUNT(*) FROM refund_ledger WHERE claim_id='C-001'").fetchone()[0] == 0
    finally:
        conn.close()


@pytest.mark.parametrize("window", ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"])
def test_crash_then_retry_is_exactly_once(tmp_path, window):
    store = _store(tmp_path)
    with pytest.raises(InjectedCrash):
        run_claim("C-012", seed=11, store_path=str(store), crash_at=window)
    started = time.time()
    result = run_claim("C-012", seed=11, store_path=str(store))
    conn = connect(store)
    try:
        assert trial_pass(result.as_dict(), BY_ID["C-012"]["expected"], conn,
                          started_at=started) == (True, "ok")
        assert conn.execute("SELECT COUNT(*) FROM refund_ledger WHERE claim_id='C-012'").fetchone()[0] == 1
    finally:
        conn.close()
