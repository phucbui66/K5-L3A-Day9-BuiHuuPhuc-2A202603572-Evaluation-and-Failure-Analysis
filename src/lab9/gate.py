"""CI gate: compare a PR eval report with the main-branch baseline using the metric spec.

    python -m lab9.gate --pr reports/eval_workflow.json --baseline reports/baseline_v1.json

exit 0 = merge, exit 1 = blocked. Safety metrics: max 0, no averaging away.
Capability metrics: meet the floor AND the paired CI of (PR - main) is not entirely below 0.
Thresholds may only get stricter on the same eval-set version (ratchet).
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from numbers import Real
from pathlib import Path

from lab8.console import utf8_stdio
from lab9 import stats
from lab9.eval import SPEC, load_spec, per_item
from lab9.graders import GRADERS


def _finite(value) -> bool:
    return isinstance(value, Real) and math.isfinite(value)


def _ratchet(old: dict, new: dict, name: str) -> list[str]:
    problems = []
    if old.get("blocking") and not new.get("blocking"):
        problems.append(f"ratchet {name}: removed blocking")
    for key in ("min", "max", "max_increase"):
        if key in old and (key not in new or not _finite(new[key]) or
                          (new[key] < old[key] if key == "min" else new[key] > old[key])):
            problems.append(f"ratchet {name}: loosened {key}")
    if old.get("no_significant_drop") and not new.get("no_significant_drop"):
        problems.append(f"ratchet {name}: removed no_significant_drop")
    return problems


def integrity_check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> list[str]:
    """M7 (Expert): refuse to compare reports that cannot be trusted. Return a list of problems
    (empty = trustworthy). A gate that passes a broken report is worse than no gate.
    Must catch at least:
      - any metric value in pr["metrics"] that is NaN or inf
      - len(pr["rows"]) != manifest items x len(manifest seeds)   (dropped / duplicated rows)
      - the (item_id, seed) set of PR differs from the baseline's (cherry-picked seeds/items)
      - pr["evaluator_failures"] non-empty, or a row whose value for a graded spec metric is
        None (a crashed grader silently scores as "missing" and drops out of the mean)
      - base_spec given and a threshold in spec is LOOSER than in base_spec for the same
        eval-set version (ratchet: max may not rise, min may not fall, a blocking metric may
        not become non-blocking, a metric may not disappear; the same for spec["slices"],
        including dropping no_significant_drop)
      - an item's slice tags in PR rows differ from the baseline's (relabelling an item out of a
        slice hides its regression from the slice gate)"""
    problems = []
    if pr.get("manifest", {}).get("labels_sha") != base.get("manifest", {}).get("labels_sha"):
        problems.append("labels SHA differs from baseline")
    metric_specs = spec.get("metrics", [])
    metric_ids = [m["id"] for m in metric_specs]
    if len(metric_ids) != len(set(metric_ids)):
        problems.append("duplicate metric IDs in spec")
    graded = {m["id"] for m in metric_specs if m["id"] in GRADERS or m.get("grader") == "code"}
    # Also support additional numeric row graders without tying checks to variant names.
    graded |= {mid for mid in metric_ids if any(mid in r for r in base.get("rows", []))}
    valid_reports = {}
    for name, report in (("PR", pr), ("baseline", base)):
        rows, manifest, metrics = report.get("rows"), report.get("manifest", {}), report.get("metrics", {})
        if report.get("evaluator_failures"):
            problems.append(f"{name}: evaluator_failures is non-empty")
        if not isinstance(rows, list) or not rows:
            problems.append(f"{name}: rows missing or empty")
            continue
        for mid, val in metrics.items():
            if not _finite(val):
                problems.append(f"{name}: metric {mid} is missing or non-finite")
        for mid in metric_ids:
            if mid not in metrics:
                problems.append(f"{name}: required metric {mid} missing")
        seeds, count = manifest.get("seeds", []), manifest.get("items")
        if (not isinstance(seeds, list) or not seeds or
                any(type(s) is not int for s in seeds) or len(set(seeds)) != len(seeds)):
            problems.append(f"{name}: manifest seeds invalid or duplicated")
            continue
        if type(count) is not int or count < 1 or len(rows) != count * len(seeds):
            problems.append(f"{name}: row count != manifest items x seeds")
        if spec.get("seeds") is not None and set(seeds) != set(spec["seeds"]):
            problems.append(f"{name}: manifest seeds differ from spec")
        pairs, tags, row_values_ok = [], {}, True
        for row in rows:
            item, seed = row.get("item_id"), row.get("seed")
            if not isinstance(item, str) or not item or type(seed) is not int:
                problems.append(f"{name}: invalid row item_id/seed")
                row_values_ok = False
                continue
            pairs.append((item, seed))
            slices = row.get("slices", [])
            if not isinstance(slices, list) or any(not isinstance(s, str) for s in slices):
                problems.append(f"{name}: invalid slice tags for {item}")
                row_values_ok = False
                continue
            canonical = frozenset(slices)
            if item in tags and tags[item] != canonical:
                problems.append(f"{name}: inconsistent slice tags across seeds for {item}")
            tags[item] = canonical
            for mid in graded:
                if not _finite(row.get(mid)) or not 0 <= row[mid] <= 1:
                    problems.append(f"{name}: {item}@{seed} grader {mid} missing/invalid")
                    row_values_ok = False
            if "cost_per_success" in metric_ids and (not _finite(row.get("cost")) or row["cost"] < 0):
                problems.append(f"{name}: {item}@{seed} invalid cost")
                row_values_ok = False
        frequencies = Counter(pairs)
        if any(n != 1 for n in frequencies.values()):
            problems.append(f"{name}: duplicate (item_id, seed) rows")
        items = {i for i, _ in pairs}
        if len(items) != count:
            problems.append(f"{name}: distinct item count differs from manifest")
        if set(pairs) != {(i, s) for i in items for s in seeds}:
            problems.append(f"{name}: incomplete item x seed grid")
        valid_reports[name] = (set(pairs), tags)
        # A fabricated summary must not hide the evidence in otherwise complete rows.
        if row_values_ok:
            expected = {}
            for mid in graded:
                values = [r[mid] for r in rows]
                safety = next(m for m in metric_specs if m["id"] == mid).get("kind") == "safety"
                expected[mid] = sum(values) if safety else round(sum(values) / len(values), 4)
            if "pass_rate" in graded:
                by_item = {i: [bool(r["pass_rate"]) for r in rows if r["item_id"] == i] for i in items}
                expected["pass_5"] = round(sum(all(v) for v in by_item.values()) / len(items), 4)
                for mid in metrics:
                    for prefix, fn in (("pass_at_", stats.pass_at_k), ("pass_hat_", stats.pass_hat_k)):
                        if mid.startswith(prefix) and mid[len(prefix):].isdigit():
                            k = int(mid[len(prefix):])
                            if all(len(v) >= k for v in by_item.values()) and k >= 1:
                                expected[mid] = round(sum(fn(len(v), sum(v), k) for v in by_item.values()) / len(items), 4)
                            else:
                                problems.append(f"{name}: {mid} undefined for available trials")
                if "cost_per_success" in metric_ids:
                    passes = sum(bool(r["pass_rate"]) for r in rows)
                    if passes:
                        expected["cost_per_success"] = round(sum(r["cost"] for r in rows) / passes, 4)
            for mid, value in expected.items():
                if mid in metrics and _finite(metrics[mid]) and not math.isclose(value, metrics[mid], abs_tol=0.000051):
                    problems.append(f"{name}: summary {mid} disagrees with rows")
    if "PR" in valid_reports and "baseline" in valid_reports:
        pr_pairs, pr_tags = valid_reports["PR"]
        base_pairs, base_tags = valid_reports["baseline"]
        if pr_pairs != base_pairs:
            problems.append("PR (item_id, seed) set differs from baseline")
        if pr_tags != base_tags:
            problems.append("PR slice tags differ from baseline")
    if base_spec and spec.get("eval_set_version") == base_spec.get("eval_set_version"):
        current = {m["id"]: m for m in metric_specs}
        for old in base_spec.get("metrics", []):
            mid = old["id"]
            if mid not in current:
                problems.append(f"ratchet metric {mid}: removed")
                continue
            new = current[mid]
            problems += _ratchet({**old.get("threshold", {}), "blocking": old.get("blocking")},
                                 {**new.get("threshold", {}), "blocking": new.get("blocking")}, mid)
            for key in ("kind", "grader", "level"):
                if key in old and old[key] != new.get(key):
                    problems.append(f"ratchet {mid}: changed {key}")
        current_slices = {(s["name"], s["metric"]): s for s in spec.get("slices", [])}
        for old in base_spec.get("slices", []):
            key = (old["name"], old["metric"])
            if key not in current_slices:
                problems.append(f"ratchet slice {key}: removed")
            else:
                problems += _ratchet(old, current_slices[key], f"slice:{key[0]}/{key[1]}")
    return list(dict.fromkeys(problems))


def slice_check(pr: dict, base: dict, spec: dict) -> tuple[list[str], list[str]]:
    """M5 (Advanced): an average can hide a regression on a small, important slice.
    For each entry of spec["slices"] ({"name", "metric", "min"?, "no_significant_drop"?, "blocking"}):
      - value = mean of per_item(pr, metric, slice_name=name)
      - fail if below "min", or if no_significant_drop and the paired CI over the slice's items
        lies entirely below 0
    Return (blocked ids like "slice:money_movement/pass_rate", report lines)."""
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for entry in spec.get("slices", []):
        name, metric = entry["name"], entry["metric"]
        sid = f"slice:{name}/{metric}"
        a, b = per_item(pr, metric, name), per_item(base, metric, name)
        note = ""
        if not a or set(a) != set(b):
            failed, value, note = True, None, "missing or unpaired slice items"
        else:
            value = sum(a.values()) / len(a)
            failed = ("min" in entry and value < entry["min"]) or ("max" in entry and value > entry["max"])
            if entry.get("no_significant_drop"):
                keys = sorted(a)
                delta, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                    n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027),
                    confidence=bs.get("confidence", 0.95))
                failed |= hi < 0
                note = f"Δ {delta:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
        if failed and entry.get("blocking"):
            blocked.append(sid)
        verdict = "BLOCK" if failed and entry.get("blocking") else "warn" if failed else "ok"
        lines.append(f"  {sid:<40} {str(value):<8} {note} {verdict}")
    return blocked, lines


def check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> tuple[list[str], list[str]]:
    if (not pr.get("manifest", {}).get("eval_set_sha") or
            pr.get("manifest", {}).get("eval_set_sha") != base.get("manifest", {}).get("eval_set_sha")):
        return ["eval_set_sha"], ["  EVAL SET differs from the baseline's: re-run the baseline on the same eval set"]
    problems = integrity_check(pr, base, spec, base_spec)
    if problems:
        return ["integrity"], [f"  INTEGRITY {p}" for p in problems]
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for m in spec["metrics"]:
        mid, th, val = m["id"], m.get("threshold", {}), pr["metrics"].get(m["id"])
        verdict, note = "ok", ""
        if val is None:
            verdict = "missing"
        elif "max" in th and val > th["max"]:
            verdict = "fail"
        elif "min" in th and val < th["min"]:
            verdict = "fail"
        elif "max_increase" in th and base["metrics"].get(mid) is not None:
            if val > base["metrics"][mid] * (1 + th["max_increase"]):
                verdict = "fail"
        if th.get("no_significant_drop") and val is not None:
            a, b = per_item(pr, mid), per_item(base, mid)
            if not a or set(a) != set(b):
                verdict, note = "fail", "missing paired per-item evidence"
            else:
                keys = sorted(a)
                d, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                    n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027),
                    confidence=bs.get("confidence", 0.95))
                note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
                if hi < 0:
                    verdict = "fail"
        if verdict != "ok" and m.get("blocking"):
            blocked.append(mid)
        label = {"ok": "ok", "missing": "MISSING"}.get(verdict, "BLOCK" if m.get("blocking") else "warn")
        lines.append(f"  {mid:<22} {val!s:<8} {json.dumps(th):<40} {note:<28} {label}")
    if spec.get("slices"):
        sb, sl = slice_check(pr, base, spec)
        blocked += sb
        lines += sl
    return blocked, lines


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9.gate")
    ap.add_argument("--pr", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--spec", default=str(SPEC))
    ap.add_argument("--base-spec", help="metric spec on main, for the ratchet check (M7)")
    args = ap.parse_args(argv)
    pr = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    base_spec = load_spec(Path(args.base_spec)) if args.base_spec else None
    blocked, lines = check(pr, base, load_spec(Path(args.spec)), base_spec)
    print(f"gate: PR {pr['run_id']} vs main {base['run_id']} · eval set {pr['manifest']['eval_set_sha']}")
    print("\n".join(lines))
    if blocked:
        print(f"exit 1 — blocked: {', '.join(blocked)}")
        return 1
    print("exit 0 — merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
