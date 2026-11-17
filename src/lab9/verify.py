"""Reproduce M0-M7 and write command evidence: python -m lab9.verify (from src)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    from lab8.console import utf8_stdio
    utf8_stdio()
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    target = root.parent / "docs/verification.md"
    v1, v2 = "config/metric_spec.yaml", "config/metric_spec_v2.yaml"
    b1, b2 = "reports/baseline_v1.json", "reports/baseline_v2.json"
    commands = [
        ("lab9.check_source", [], 0), ("lab9.smoke", [], 0),
        ("lab9.evalset", ["--build", "--check"], 0),
        ("lab9.evalset", ["--v2", "--build", "--check"], 0),
        ("pytest", ["-q", "-o", "addopts="], 0),
        ("lab9.judge", ["--csv", "data/eval/judge_tone_public.csv", "--audit", "10"], 0),
        ("lab9.judge", ["--csv", "data/eval/judge_helpful_public.csv", "--audit", "10"], 1),
        ("lab9.evidence", [], 0),
    ]
    for shape, path in (("swarm", b1), ("fixed", "reports/eval_fixed.json"),
                        ("seeded_regression", "reports/eval_seeded_regression.json"),
                        ("swarm", "reports/eval_pr.json")):
        commands.append(("lab9.eval", ["--shape", shape, "--spec", v1, "--out", path], 0))
    for path, status in ((b1, 0), ("reports/eval_pr.json", 0), ("reports/eval_fixed.json", 0),
                         ("reports/eval_seeded_regression.json", 1)):
        commands.append(("lab9.gate", ["--pr", path, "--baseline", b1, "--spec", v1, "--base-spec", v1], status))
    commands += [
        ("lab9.ci_check", ["--pr", "reports/eval_pr.json", "--baseline", b1, "--spec", v1], 0),
        ("lab9.mutation", ["--spec", v1, "--detect"], 0),
        ("lab9.eval", ["--shape", "swarm", "--spec", v2, "--out", b2], 0),
        ("lab9.gate", ["--pr", b2, "--baseline", b2, "--spec", v2, "--base-spec", v2], 0),
    ]
    for shape in ("fixed", "honest_refactor", "seeded_regression", "slice_regression", "flaky_regression"):
        path = f"reports/eval_{shape}_v2.json" if shape != "slice_regression" else "reports/eval_slice_regression.json"
        commands.append(("lab9.eval", ["--shape", shape, "--spec", v2, "--out", path], 0))
        status = 0 if shape in ("fixed", "honest_refactor") else 1
        commands.append(("lab9.gate", ["--pr", path, "--baseline", b2, "--spec", v2, "--base-spec", v2], status))
    commands += [
        ("lab9.mutation", ["--spec", v2, "--aa", "66,77,88,99,110"], 0),
        ("lab9.mutation", ["--spec", v2, "--baseline", b2, "--base-spec", v2], 0),
        ("lab9.traps", ["--pr", "reports/eval_slice_regression.json", "--baseline", b2, "--spec", v2], 0),
    ]
    for trap in ("evaluator_errors_as_nan", "dropped_failing_rows", "cherry_picked_seeds", "loosened_spec"):
        args = ["--pr", f"reports/traps/{trap}.json", "--baseline", b2, "--spec",
                "reports/traps/loosened_spec.spec.yaml" if trap == "loosened_spec" else v2,
                "--base-spec", v2]
        commands.append(("lab9.gate", args, 1))
    commands.append(("lab9.summary", [], 0))
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    with target.open("w", encoding="utf-8") as log:
        log.write("# Biên bản kiểm tra M0–M7\n\nSinh tự động bằng `python -m lab9.verify`; "
                  "exit 1 được mong đợi cho helpful, regression và trap.\n\n")
        for i, (module, args, expected) in enumerate(commands, 1):
            display = f"python -m {module} {' '.join(args)}".rstrip()
            print(f"[{i}/{len(commands)}] {display}", flush=True)
            result = subprocess.run([sys.executable, "-m", module, *args], env=env,
                cwd=root, text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            print(result.stdout, end="", flush=True)
            log.write(f"## {i}. {module}\n\n```text\n$ {display}\n{result.stdout}"
                      f"exit code: {result.returncode}; expected: {expected}\n```\n\n")
            log.flush()
            good = result.returncode == expected
            if module == "lab9.gate" and expected == 1:
                good &= "exit 1 — blocked:" in result.stdout
                if "eval_seeded_regression.json" in args:
                    good &= "pass_rate" in result.stdout.split("exit 1 — blocked:")[-1]
            if not good:
                print(f"FAILED: {display}; see {target}")
                return 1
        log.write(f"**PASS: {len(commands)}/{len(commands)} lệnh có kết quả mong đợi.**\n")
    print(f"PASS: {len(commands)} commands; wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
