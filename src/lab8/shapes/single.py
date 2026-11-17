"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

from typing import Any

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    budget = Budget()
    trace = Trace(make_run_id("single", claim_id, seed))

    def done(status: str, proposal: int = 0, reason: str | None = None) -> RunResult:
        # Draft from the validated result, never from raw claim/order rows.
        complete(budget, seed=seed, purpose="draft", prompt=f"status={status}; proposal={proposal}")
        trace.add("decision", {"status": status, "proposal_amount": proposal, "reason": reason})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    try:
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        trace.add("claim", {"found": claim["found"], "has_order_id": bool(claim.get("order_id"))})
        if not claim["found"]:
            return done("failed", reason="unknown_claim")
        if not claim.get("order_id"):
            return done("needs_info", reason="missing_order_id")

        observed: dict[str, dict[str, Any]] = {}
        read_order = ["lookup_order", "lookup_policy"]

        def decide(observation: dict[str, Any]) -> dict[str, Any]:
            last_tool = observation.get("last_tool")
            if last_tool is None:
                # MockLLM exposes a parser, not a tool-calling API. Its output
                # only chooses which of two read tools to inspect first.
                parsed = complete(budget, seed=seed, purpose="parse", prompt=claim["ticket"])
                if parsed.startswith("parsed_delay=") and parsed.removeprefix("parsed_delay=").isdigit():
                    read_order[:] = ["lookup_policy", "lookup_order"]
            else:
                observed[last_tool] = observation["last_result"]
                trace.add("react_observation", {"tool": last_tool})
                complete(
                    budget,
                    seed=seed,
                    purpose="plan",
                    prompt=f"read_tools_observed={','.join(observed)}; max_steps=8",
                )

            order_view = observed.get("lookup_order")
            if order_view is not None and not order_view["visible"]:
                return {"final": {"status": "escalated", "reason": order_view["reason"]}}

            # Bound the model's routing to read tools with arguments taken from
            # the trusted claim view. It cannot choose a principal or an amount.
            for name in read_order:
                if name not in observed:
                    args = (
                        {"order_id": claim["order_id"], "principal_id": claim["principal_id"]}
                        if name == "lookup_order"
                        else {}
                    )
                    trace.add("react_action", {"tool": name})
                    return {"tool": name, "args": args}
            return {"final": {"ready": True}}

        investigation = run_react(
            conn,
            budget,
            observation={"claim": claim},
            decide=decide,
            max_steps=8,
            worker=True,
        )
        if investigation["stopped"] != "final":
            return done("failed", reason="step_cap")
        if investigation["final"].get("status") == "escalated":
            return done("escalated", reason=investigation["final"]["reason"])
        if not investigation["final"].get("ready"):
            return done("failed", reason="incomplete_investigation")

        # Money is computed after the read-only loop, using the DB order view.
        # The delay parsed from the ticket is never copied into that view.
        budget.add_tool(tool_cost())
        quote = compute_compensation(conn, observed["lookup_order"]["order"])
        proposal = int(quote["amount_vnd"])
        trace.add("quote", quote)
        if proposal <= 0:
            return done("denied", reason=quote["reason"])

        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        trace.add("host_outcome", {"ok": outcome["ok"], "reason": outcome["reason"]})
        if not outcome["ok"]:
            status = "failed" if outcome["conflict"] else "denied"
            return done(status, proposal, outcome["reason"])
        return done("resolved", proposal)
    finally:
        conn.close()
