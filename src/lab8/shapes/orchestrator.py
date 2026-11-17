"""Shape C — orchestrator plus read-only investigators. Student work.

1. Build a handoff with `lab8.handoff.make_handoff`. Allowed tools are read-only.
   Never put parent_secret, raw headers, or the full claim row into facts.
2. `lab8.runtime.run_readonly_investigators` runs those tools.
3. The orchestrator quotes from the investigator's order view and calls
   `durability.issue_refund`. Investigators have no write registry.
   Pass the full quote; the host subtracts earlier refunds on the same order.
   `lookup_refund_history` is a read-only tool you may hand to an investigator.
4. Trace the sanitized handoff, not the parent context.

An LLM summary of the parent context is not a sanitizer. Use the allowlist.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    return _run_claim(claim_id, seed=seed, store_path=store_path, crash_at=crash_at,
                      include_history=True)


def _run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
    include_history: bool,
) -> RunResult:
    conn = connect(store_path)
    budget = Budget()
    trace = Trace(make_run_id("orchestrator", claim_id, seed))

    def done(status: str, proposal: int = 0, reason: str | None = None) -> RunResult:
        complete(budget, seed=seed, purpose="draft", prompt=f"status={status}; proposal={proposal}")
        trace.add("decision", {"status": status, "proposal_amount": proposal, "reason": reason})
        return finish(conn, shape="orchestrator", claim_id=claim_id, seed=seed,
                      status=status, proposal_amount=proposal, budget=budget,
                      trace=trace, error_reason=reason)

    try:
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        trace.add("claim", {"found": claim["found"], "has_order_id": bool(claim.get("order_id"))})
        if not claim["found"]:
            return done("failed", reason="unknown_claim")
        if not claim.get("order_id"):
            return done("needs_info", reason="missing_order_id")

        # Planning and handoff exclude the untrusted ticket and parent context.
        complete(budget, seed=seed, purpose="plan", prompt=f"investigate claim={claim_id}")
        handoff = make_handoff(
            request_id=f"REQ-{claim_id}", claim_id=claim_id,
            task="verify_order_policy_and_quote", facts={},
            allowed_tools=["lookup_order", "lookup_policy"]
                          + (["lookup_refund_history"] if include_history else [])
                          + ["compute_compensation"],
        )
        trace.add("handoff", handoff)
        investigated = run_readonly_investigators(conn, budget, handoff, claim["principal_id"])
        tools = investigated["tools"]
        order_view = tools.get("lookup_order") or {}
        trace.add("investigator", {
            "order_visible": bool(order_view.get("visible")),
            "order_reason": order_view.get("reason"),
            "policy_count": len((tools.get("lookup_policy") or {}).get("policies") or []),
            "history_visible": bool((tools.get("lookup_refund_history") or {}).get("visible")),
        })
        if not order_view.get("visible"):
            return done("escalated", reason=order_view.get("reason"))

        quote = tools.get("compute_compensation")
        if quote is None:
            return done("failed", reason="incomplete_investigation")
        proposal = int(quote["amount_vnd"])
        trace.add("quote", quote)
        if proposal <= 0:
            return done("denied", reason=quote["reason"])

        # Pass the full quote; the host validates approval and order cap atomically.
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        trace.add("host_outcome", {"ok": outcome["ok"], "reason": outcome["reason"]})
        if not outcome["ok"]:
            return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
        return done("resolved", proposal)
    finally:
        conn.close()
