"""Regression evidence from C-002, FM-08 and report-integrity attacks."""
import copy

import pytest

pytestmark = pytest.mark.student


@pytest.fixture(autouse=True)
def restore_shape_registry():
    """Day 9 runtime variants must not pollute Day 8's four-shape contract."""
    from lab8.shapes import SHAPES
    original = dict(SHAPES)
    yield
    SHAPES.clear()
    SHAPES.update(original)


def context(output, expected=None):
    from pydantic_evals.evaluators import EvaluatorContext
    return EvaluatorContext(name="regression", inputs={}, metadata=None,
        expected_output=expected, output=output, duration=0.0,
        _span_tree=None, attributes={}, metrics={})


@pytest.mark.parametrize("reply", ["Dạ đã hoàn 20.000đ.", "Refunded 20,000 VND.",
                                  "Đã hoàn 20000 đồng.", "Đơn O-20000 được hoàn 20 000 VNĐ."])
def test_reply_amount_accepts_equivalent_formats(reply):
    from lab9.graders import ReplyLedgerConsistent
    t = {"result": {}, "snapshot": {"refund_vnd": 20000},
         "events": [{"kind": "reply", "payload": {"text": reply}}]}
    assert ReplyLedgerConsistent().evaluate(context(t)).value is True


def test_reply_uses_ledger_even_when_proposal_and_label_are_different():
    from lab9.graders import ReplyLedgerConsistent
    t = {"result": {"proposal_amount": 35000}, "snapshot": {"refund_vnd": 20000},
         "events": [{"kind": "reply", "payload": {"text": "Đã hoàn 35.000đ."}}]}
    assert ReplyLedgerConsistent().evaluate(context(t, {"refund_vnd": 20000})).value is False
    t["events"][0]["payload"]["text"] = "LogiX đã hoàn phí 20.000đ cho đơn O-808."
    assert ReplyLedgerConsistent().evaluate(context(t)).value is True


def test_trace_c002_first_wrong_step_and_fixed_control():
    from lab9.trace_case import investigate
    from lab9.graders import DbFactKept, RefundAmountCorrect
    bad, fixed = [investigate(shape, "C-002", 11) for shape in ("seeded_regression", "fixed")]
    events = bad["trial"]["events"]
    assert [e["kind"] for e in events[:3]] == ["handoff", "investigator", "model_override"]
    assert events[1]["payload"]["lookup_order"]["order"]["delay_days"] == 2
    assert events[2]["payload"]["delay_days"] == 5
    assert bad["trial"]["snapshot"]["refund_vnd"] == 20000
    assert fixed["trial"]["snapshot"]["refund_vnd"] == 0
    for grader in (DbFactKept(), RefundAmountCorrect()):
        assert grader.evaluate(context(bad["trial"], bad["label"])).value is False
        assert grader.evaluate(context(fixed["trial"], fixed["label"])).value is True


def test_fm08_detects_real_misreport_and_accepts_refactor():
    from lab8.shapes import SHAPES
    from lab9.variant_agent import make_shape
    from lab9.trace_case import investigate
    from lab9.graders import ReplyLedgerConsistent
    SHAPES["test_misreport"] = make_shape("test_misreport", {"no_override", "misreport"})
    for shape, expected in (("test_misreport", False), ("honest_refactor", True)):
        case = investigate(shape, "C-008", 11)
        assert case["trial"]["lab8_pass"] is True  # Lab 8 alone misses the reply error.
        assert ReplyLedgerConsistent().evaluate(context(case["trial"], case["label"])).value is expected


def test_proposal_detects_double_deduction_when_ledger_stays_zero():
    from lab9.trace_case import investigate
    from lab9.graders import ProposalAmountCorrect, RefundAmountCorrect
    case = investigate("seeded_regression", "C-013", 11)
    ctx = context(case["trial"], case["label"])
    assert RefundAmountCorrect().evaluate(ctx).value is True
    assert ProposalAmountCorrect().evaluate(ctx).value is False


@pytest.mark.parametrize("args", [(0, 0, 1), (-1, 0, 1), (5, -1, 1), (5, 6, 1),
                                  (5, 1, -1), (5, 1, 6), (5.0, 1, 1), (True, 1, 1)])
def test_advanced_both_estimators_reject_invalid_inputs(args):
    from lab9.stats import pass_at_k, pass_hat_k
    for estimate in (pass_at_k, pass_hat_k):
        with pytest.raises(ValueError):
            estimate(*args)


def report():
    rows = [{"item_id": f"E-{i}", "seed": s, "pass_rate": True,
             "slices": ["money_movement"] if i == 0 else ["adversarial"]}
            for i in range(3) for s in (11, 22)]
    return {"manifest": {"items": 3, "seeds": [11, 22], "eval_set_sha": "same"},
            "rows": rows, "metrics": {"pass_rate": 1.0}, "evaluator_failures": []}


SPEC = {"eval_set_version": "v2", "seeds": [11, 22],
        "metrics": [{"id": "pass_rate", "kind": "capability", "grader": "code",
                     "blocking": True, "threshold": {"min": 0.8, "no_significant_drop": True}}],
        "slices": [{"name": "money_movement", "metric": "pass_rate", "min": 0.9,
                    "no_significant_drop": True, "blocking": True}]}


@pytest.mark.parametrize("attack", ["duplicate", "evaluator_failure", "row_nan", "null",
                                    "relabel", "summary", "seed", "missing_metric"])
def test_advanced_integrity_catches_attacks_on_green_reports(attack):
    from lab9.gate import check
    base, pr = report(), report()
    if attack == "duplicate":
        pr["rows"][-1] = copy.deepcopy(pr["rows"][0])
    elif attack == "evaluator_failure":
        pr["evaluator_failures"] = ["grader crashed on an otherwise green run"]
    elif attack in ("row_nan", "null"):
        pr["rows"][0]["pass_rate"] = float("nan") if attack == "row_nan" else None
    elif attack == "relabel":
        for row in pr["rows"]:
            row["slices"] = []
    elif attack == "summary":
        pr["rows"][0]["pass_rate"] = False
    elif attack == "seed":
        pr["rows"][0]["seed"] = 999
    elif attack == "missing_metric":
        pr["metrics"] = {}
    assert check(pr, base, SPEC)[0] == ["integrity"]


@pytest.mark.parametrize("attack", ["drop_metric", "disable_block", "remove_ci", "lower_min",
                                    "drop_slice", "slice_ci", "slice_block", "slice_min"])
def test_advanced_ratchet_preserves_metrics_and_slices(attack):
    from lab9.gate import integrity_check
    loose = copy.deepcopy(SPEC)
    metric, slice_ = loose["metrics"][0], loose["slices"][0]
    if attack == "drop_metric":
        loose["metrics"] = []
    elif attack == "disable_block":
        metric["blocking"] = False
    elif attack == "remove_ci":
        metric["threshold"].pop("no_significant_drop")
    elif attack == "lower_min":
        metric["threshold"]["min"] = 0.7
    elif attack == "drop_slice":
        loose["slices"] = []
    elif attack == "slice_ci":
        slice_.pop("no_significant_drop")
    elif attack == "slice_block":
        slice_["blocking"] = False
    elif attack == "slice_min":
        slice_["min"] = 0.5
    assert any("ratchet" in p for p in integrity_check(report(), report(), loose, SPEC))


def test_advanced_baseline_compared_with_itself_passes():
    from lab9.gate import check
    assert check(report(), report(), SPEC, SPEC)[0] == []


def test_advanced_slice_gate_handles_a_single_item_and_row_order():
    from lab9.gate import slice_check
    base, pr = report(), report()
    for row in pr["rows"]:
        if row["item_id"] == "E-0":
            row["pass_rate"] = False
    pr["rows"].reverse()
    blocked, _ = slice_check(pr, base, SPEC)
    assert blocked == ["slice:money_movement/pass_rate"]


def test_advanced_quiet_override_is_caught_without_an_override_event():
    from pathlib import Path
    from lab8.shapes import SHAPES
    from lab9.variant_agent import make_shape
    from lab9.trace_case import investigate
    from lab9.graders import DbFactKept, RefundAmountCorrect
    SHAPES["test_quiet"] = make_shape("test_quiet", {"no_override", "quiet_override"})
    case = investigate("test_quiet", "C-101", 11, Path("config/metric_spec_v2.yaml"))
    ctx = context(case["trial"], case["label"])
    assert DbFactKept().evaluate(ctx).value is True
    assert RefundAmountCorrect().evaluate(ctx).value is False
    assert case["trial"]["lab8_pass"] is False


def test_evalset_build_has_portable_lf_bytes(tmp_path, monkeypatch):
    """Windows CRLF conversion must not change dataset/label hashes in Linux CI."""
    from pathlib import Path
    from lab9 import evalset
    paths = [tmp_path / name for name in ("items1.jsonl", "labels1.json", "items2.jsonl", "labels2.json")]
    for name, path in zip(("ITEMS", "LABELS", "ITEMS_V2", "LABELS_V2"), paths):
        monkeypatch.setattr(evalset, name, path)
    evalset.build(source=Path("data/public_claims.jsonl"))
    evalset.build_v2(items_v1=paths[0], labels_v1=paths[1])
    for path in paths:
        assert b"\r" not in path.read_bytes()
