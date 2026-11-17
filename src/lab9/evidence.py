"""Generate redacted taxonomy evidence without changing the supplied variants."""
from __future__ import annotations

import json
from pathlib import Path

from lab8.shapes import SHAPES
from lab9.trace_case import investigate
from lab9.variant_agent import make_shape

CASES = [
    ("FM-01", "C-001", "leaky_trace"), ("FM-02", "C-007", "ignore_denied"),
    ("FM-03", "C-002", "ticket_trust"), ("FM-04", "C-014", "sum_parts"),
    ("FM-05", "C-014", "pre_deducted"), ("FM-06", "C-006", "stale_clause"),
    ("FM-07", "C-001", "sibling_refund"), ("FM-08", "C-008", "misreport"),
]


def main() -> int:
    lines = ["# Bằng chứng trace đã lược dữ liệu nhạy cảm", "",
             "Sinh bằng `python -m lab9.evidence`. Mọi case dùng seed 11 và DB tạm mới.",
             "Không sửa agent Lab 8, variants hay traps; chỉ đăng ký công tắc có sẵn trong bộ nhớ.", ""]
    for fm, claim, bug in CASES:
        shape = f"evidence_{bug}"
        SHAPES[shape] = make_shape(shape, {"no_override", bug})
        case = investigate(shape, claim, 11)
        trial = case["trial"]
        lines += [f"## {fm}: {shape} {claim}@11", "", "```text"]
        for n, event in enumerate(trial["events"], 1):
            kind, payload = event.get("kind"), event.get("payload")
            if kind == "debug_claim_row":
                detail = "[REDACTED: raw claim contained fields forbidden by the trace contract]"
            elif kind == "investigator":
                view = payload.get("lookup_order", {})
                detail = json.dumps({"visible": view.get("visible"), "reason": view.get("reason"),
                                     "db_delay_days": view.get("order", {}).get("delay_days")}, ensure_ascii=False)
            elif kind in ("quote", "proposal", "model_override", "refund_history", "batch_refund", "reply", "decision"):
                detail = json.dumps(payload, ensure_ascii=False)
            else:
                detail = "[sanitized handoff metadata]"
            lines.append(f"{n}. {kind}: {detail}")
        snap, label = trial["snapshot"], case["label"]
        # Lab 8's leak reason embeds the forbidden token: publish only its type.
        reason = str(trial["lab8_reason"]).split(":", 1)[0]
        lines += [f"ledger={snap['refund_vnd']}; expected={label['refund_vnd']}; "
                  f"unexpected_rows={trial['unexpected_rows']}; lab8_pass={trial['lab8_pass']}; reason={reason}",
                  "```", ""]
    case = investigate("fixed", "C-110", 11, Path("config/metric_spec_v2.yaml"))
    lines += ["## FM-09: fixed C-110@11 (kiểm tra guard)", "",
              f"Result status: `{case['trial']['result']['status']}`; ledger: `{case['trial']['snapshot']['refund_vnd']}`.",
              "Investigator từ chối vì `outside_principal_scope`. Đây là bằng chứng guard hoạt động;",
              "không phải bằng chứng một lần truy cập trái phép đã thành công.", ""]
    target = Path("../docs/trace_evidence.md")
    target.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
