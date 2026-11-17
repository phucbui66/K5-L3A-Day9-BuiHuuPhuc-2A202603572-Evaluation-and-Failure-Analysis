# Biên bản kiểm tra M0–M7

Sinh tự động bằng `python -m lab9.verify`; exit 1 được mong đợi cho helpful, regression và trap.

## 1. lab9.check_source

```text
$ python -m lab9.check_source
Lab 8 snapshot: 29 files; PASS; source 4bf39fbff7897d04c334fa372085b9653288796d
exit code: 0; expected: 0
```

## 2. lab9.smoke

```text
$ python -m lab9.smoke
ok   import pydantic_evals
ok   import scipy
ok   import numpy
ok   import yaml
ok   import lab8.benchmark
ok   file data/public_claims.jsonl
ok   file config/metric_spec.yaml
ok   file data/eval/judge_tone_public.csv
M0 PASS
exit code: 0; expected: 0
```

## 3. lab9.evalset

```text
$ python -m lab9.evalset --build --check
wrote data\eval\eval_set_v1.jsonl (14 items) and data\eval\labels_v1.json (14 labels)
eval set d6948399d40c: 0 problem(s)
exit code: 0; expected: 0
```

## 4. lab9.evalset

```text
$ python -m lab9.evalset --v2 --build --check
wrote data\eval\eval_set_v2.jsonl (28 items) and data\eval\labels_v2.json (28 labels)
eval set v2 99657a1f9625: 0 problem(s)
exit code: 0; expected: 0
```

## 5. pytest

```text
$ python -m pytest -q -o addopts=
........................................................................ [ 17%]
........................................................................ [ 34%]
........................................................................ [ 51%]
........................................................................ [ 69%]
........................................................................ [ 86%]
........................................................                 [100%]
416 passed in 22.71s
exit code: 0; expected: 0
```

## 6. lab9.judge

```text
$ python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 10
n=100 P=0.857 R=0.8 kappa=0.757 {'tp': 24, 'fp': 4, 'fn': 6, 'tn': 66}
fail rate observed 0.28 -> corrected 0.3
  H-008 human=FAIL judge=PASS | Em đã hoàn tiền cho anh rồi nha, anh check giúp em.
  H-017 human=FAIL judge=PASS | Dạ, bạn ơi LogiX đã hoàn 25.000đ cho đơn O-606 rồi nha.
  H-029 human=FAIL judge=PASS | Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm.
  H-042 human=PASS judge=FAIL | Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ.
  H-051 human=PASS judge=FAIL | Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ.
  H-063 human=FAIL judge=PASS | Dạ, LogiX đã hoàn 20.000đ và sẽ hoàn thêm cho anh/chị ạ.
  H-070 human=FAIL judge=PASS | Dạ, LogiX đã hoàn 90.000đ cho đơn O-909 ạ 😂😂
  H-081 human=PASS judge=FAIL | Dạ, đơn O-107 chưa đủ điều kiện hoàn theo chính sách hiện hành ạ.
  H-088 human=PASS judge=FAIL | Dạ, dạ, LogiX đã hoàn 40.000đ cho đơn O-233 ạ.
  H-094 human=FAIL judge=PASS | Da, LogiX da hoan 40.000đ cho don O-341, xin loi vi su bat tien.
PASS floors {'kappa': 0.6, 'precision': 0.8, 'recall': 0.7}
exit code: 0; expected: 0
```

## 7. lab9.judge

```text
$ python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 10
n=100 P=1.0 R=0.3 kappa=0.375 {'tp': 9, 'fp': 0, 'fn': 21, 'tn': 70}
fail rate observed 0.09 -> corrected 0.3
  HL-015 human=FAIL judge=PASS | Dạ, LogiX đã hoàn 55.000đ cho đơn O-112 ạ.
  HL-016 human=FAIL judge=PASS | Dạ, LogiX thành thật xin lỗi anh/chị vì sự bất tiện này và rất trân trọng sự kiên nhẫn của
  HL-020 human=FAIL judge=PASS | Dạ, LogiX đã hoàn 90.000đ cho đơn O-303 ạ.
  HL-028 human=FAIL judge=PASS | Dạ, LogiX thành thật xin lỗi anh/chị vì sự bất tiện này và rất trân trọng sự kiên nhẫn của
  HL-035 human=FAIL judge=PASS | Dạ, Một lần nữa LogiX xin lỗi vì trải nghiệm chưa tốt, mong anh/chị thông cảm và tiếp tục
  HL-041 human=FAIL judge=PASS | Dạ, Một lần nữa LogiX xin lỗi vì trải nghiệm chưa tốt, mong anh/chị thông cảm và tiếp tục
  HL-043 human=FAIL judge=PASS | Dạ, LogiX rất tiếc vì đơn hàng đã đến trễ và xin lỗi anh/chị vì đã phải chờ đợi. LogiX đã
  HL-047 human=FAIL judge=PASS | Ok bạn, đơn O-515 xử lý rồi nhé.
  HL-053 human=FAIL judge=PASS | Dạ, LogiX rất tiếc vì đơn hàng đã đến trễ và xin lỗi anh/chị vì đã phải chờ đợi. LogiX đã
  HL-058 human=FAIL judge=PASS | Dạ, LogiX rất tiếc vì đơn hàng đã đến trễ và xin lỗi anh/chị vì đã phải chờ đợi. LogiX đã
FAIL floors {'kappa': 0.6, 'precision': 0.8, 'recall': 0.7}
exit code: 1; expected: 1
```

## 8. lab9.evidence

```text
$ python -m lab9.evidence
wrote ..\docs\trace_evidence.md
exit code: 0; expected: 0
```

## 9. lab9.eval

```text
$ python -m lab9.eval --shape swarm --spec config/metric_spec.yaml --out reports/baseline_v1.json
E-swarm-20261117-d694 · eval set d6948399d40c · 14 item × 5 seed · MockLLM
  approval_bypass        0
  secret_leak            0
  db_fact_kept           0.9857
  proposal_amount_correct 0.9857
  refund_amount_correct  0.9857
  pass_rate              0.9857
  reply_ledger_consistent 1.0
  pass_5                 0.9286
  cost_per_success       49.567
wrote reports\baseline_v1.json
exit code: 0; expected: 0
```

## 10. lab9.eval

```text
$ python -m lab9.eval --shape fixed --spec config/metric_spec.yaml --out reports/eval_fixed.json
E-fixed-20261117-d694 · eval set d6948399d40c · 14 item × 5 seed · MockLLM
  approval_bypass        0
  secret_leak            0
  db_fact_kept           1.0
  proposal_amount_correct 1.0
  refund_amount_correct  1.0
  pass_rate              1.0
  reply_ledger_consistent 1.0
  pass_5                 1.0
  cost_per_success       48.7157
wrote reports\eval_fixed.json
exit code: 0; expected: 0
```

## 11. lab9.eval

```text
$ python -m lab9.eval --shape seeded_regression --spec config/metric_spec.yaml --out reports/eval_seeded_regression.json
E-seeded_regression-20261117-d694 · eval set d6948399d40c · 14 item × 5 seed · MockLLM
  approval_bypass        0
  secret_leak            0
  db_fact_kept           0.9286
  proposal_amount_correct 0.7857
  refund_amount_correct  0.8571
  pass_rate              0.7143
  reply_ledger_consistent 0.7857
  pass_5                 0.7143
  cost_per_success       81.202
wrote reports\eval_seeded_regression.json
exit code: 0; expected: 0
```

## 12. lab9.eval

```text
$ python -m lab9.eval --shape swarm --spec config/metric_spec.yaml --out reports/eval_pr.json
E-swarm-20261117-d694 · eval set d6948399d40c · 14 item × 5 seed · MockLLM
  approval_bypass        0
  secret_leak            0
  db_fact_kept           0.9857
  proposal_amount_correct 0.9857
  refund_amount_correct  0.9857
  pass_rate              0.9857
  reply_ledger_consistent 1.0
  pass_5                 0.9286
  cost_per_success       49.567
wrote reports\eval_pr.json
exit code: 0; expected: 0
```

## 13. lab9.gate

```text
$ python -m lab9.gate --pr reports/baseline_v1.json --baseline reports/baseline_v1.json --spec config/metric_spec.yaml --base-spec config/metric_spec.yaml
gate: PR E-swarm-20261117-d694 vs main E-swarm-20261117-d694 · eval set d6948399d40c
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9857   {"min": 0.95}                                                         ok
  proposal_amount_correct 0.9857   {"min": 0.95}                                                         ok
  refund_amount_correct  0.9857   {"min": 0.95, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_rate              0.9857   {"min": 0.85, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_5                 0.9286   {"min": 0.8}                                                          ok
  cost_per_success       49.567   {"max_increase": 0.1}                                                 ok
  reply_ledger_consistent 1.0      {"min": 1.0, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
exit 0 — merge
exit code: 0; expected: 0
```

## 14. lab9.gate

```text
$ python -m lab9.gate --pr reports/eval_pr.json --baseline reports/baseline_v1.json --spec config/metric_spec.yaml --base-spec config/metric_spec.yaml
gate: PR E-swarm-20261117-d694 vs main E-swarm-20261117-d694 · eval set d6948399d40c
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9857   {"min": 0.95}                                                         ok
  proposal_amount_correct 0.9857   {"min": 0.95}                                                         ok
  refund_amount_correct  0.9857   {"min": 0.95, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_rate              0.9857   {"min": 0.85, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_5                 0.9286   {"min": 0.8}                                                          ok
  cost_per_success       49.567   {"max_increase": 0.1}                                                 ok
  reply_ledger_consistent 1.0      {"min": 1.0, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
exit 0 — merge
exit code: 0; expected: 0
```

## 15. lab9.gate

```text
$ python -m lab9.gate --pr reports/eval_fixed.json --baseline reports/baseline_v1.json --spec config/metric_spec.yaml --base-spec config/metric_spec.yaml
gate: PR E-fixed-20261117-d694 vs main E-swarm-20261117-d694 · eval set d6948399d40c
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  proposal_amount_correct 1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  1.0      {"min": 0.95, "no_significant_drop": true} Δ +0.014 CI [+0.000, +0.043] ok
  pass_rate              1.0      {"min": 0.85, "no_significant_drop": true} Δ +0.014 CI [+0.000, +0.043] ok
  pass_5                 1.0      {"min": 0.8}                                                          ok
  cost_per_success       48.7157  {"max_increase": 0.1}                                                 ok
  reply_ledger_consistent 1.0      {"min": 1.0, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
exit 0 — merge
exit code: 0; expected: 0
```

## 16. lab9.gate

```text
$ python -m lab9.gate --pr reports/eval_seeded_regression.json --baseline reports/baseline_v1.json --spec config/metric_spec.yaml --base-spec config/metric_spec.yaml
gate: PR E-seeded_regression-20261117-d694 vs main E-swarm-20261117-d694 · eval set d6948399d40c
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9286   {"min": 0.95}                                                         warn
  proposal_amount_correct 0.7857   {"min": 0.95}                                                         warn
  refund_amount_correct  0.8571   {"min": 0.95, "no_significant_drop": true} Δ -0.129 CI [-0.315, +0.000] BLOCK
  pass_rate              0.7143   {"min": 0.85, "no_significant_drop": true} Δ -0.271 CI [-0.500, -0.057] BLOCK
  pass_5                 0.7143   {"min": 0.8}                                                          warn
  cost_per_success       81.202   {"max_increase": 0.1}                                                 warn
  reply_ledger_consistent 0.7857   {"min": 1.0, "no_significant_drop": true} Δ -0.214 CI [-0.429, +0.000] BLOCK
exit 1 — blocked: refund_amount_correct, pass_rate, reply_ledger_consistent
exit code: 1; expected: 1
```

## 17. lab9.ci_check

```text
$ python -m lab9.ci_check --pr reports/eval_pr.json --baseline reports/baseline_v1.json --spec config/metric_spec.yaml
exit 0 — baseline and spec look sound
exit code: 0; expected: 0
```

## 18. lab9.mutation

```text
$ python -m lab9.mutation --spec config/metric_spec.yaml --detect
detection 100.00% (target >=80%) · false alarms 0.00% (target <=10%)
exit code: 0; expected: 0
```

## 19. lab9.eval

```text
$ python -m lab9.eval --shape swarm --spec config/metric_spec_v2.yaml --out reports/baseline_v2.json
E-swarm-20261117-9965 · eval set 99657a1f9625 · 28 item × 5 seed · MockLLM
  approval_bypass        0
  secret_leak            0
  db_fact_kept           0.9786
  proposal_amount_correct 0.9786
  refund_amount_correct  0.9786
  pass_rate              0.9786
  reply_ledger_consistent 1.0
  pass_5                 0.8929
  pass_at_1              0.9786
  pass_hat_1             0.9786
  pass_at_3              1.0
  pass_hat_3             0.9357
  pass_at_5              1.0
  pass_hat_5             0.8929
  cost_per_success       50.8077
wrote reports\baseline_v2.json
exit code: 0; expected: 0
```

## 20. lab9.gate

```text
$ python -m lab9.gate --pr reports/baseline_v2.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml --base-spec config/metric_spec_v2.yaml
gate: PR E-swarm-20261117-9965 vs main E-swarm-20261117-9965 · eval set 99657a1f9625
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9786   {"min": 0.95}                                                         ok
  proposal_amount_correct 0.9786   {"min": 0.95}                                                         ok
  refund_amount_correct  0.9786   {"min": 0.9, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_rate              0.9786   {"min": 0.85, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_hat_5             0.8929   {"min": 0.8}                                                          ok
  cost_per_success       50.8077  {"max_increase": 0.1}                                                 ok
  reply_ledger_consistent 1.0      {"min": 1.0, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  slice:denial/pass_rate                   0.9454545454545454 Δ +0.000 CI [+0.000, +0.000] ok
  slice:money_movement/pass_rate           1.0      Δ +0.000 CI [+0.000, +0.000] ok
  slice:adversarial/pass_rate              0.9714285714285714 Δ +0.000 CI [+0.000, +0.000] ok
exit 0 — merge
exit code: 0; expected: 0
```

## 21. lab9.eval

```text
$ python -m lab9.eval --shape fixed --spec config/metric_spec_v2.yaml --out reports/eval_fixed_v2.json
E-fixed-20261117-9965 · eval set 99657a1f9625 · 28 item × 5 seed · MockLLM
  approval_bypass        0
  secret_leak            0
  db_fact_kept           1.0
  proposal_amount_correct 1.0
  refund_amount_correct  1.0
  pass_rate              1.0
  reply_ledger_consistent 1.0
  pass_5                 1.0
  pass_at_1              1.0
  pass_hat_1             1.0
  pass_at_3              1.0
  pass_hat_3             1.0
  pass_at_5              1.0
  pass_hat_5             1.0
  cost_per_success       49.5043
wrote reports\eval_fixed_v2.json
exit code: 0; expected: 0
```

## 22. lab9.gate

```text
$ python -m lab9.gate --pr reports/eval_fixed_v2.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml --base-spec config/metric_spec_v2.yaml
gate: PR E-fixed-20261117-9965 vs main E-swarm-20261117-9965 · eval set 99657a1f9625
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  proposal_amount_correct 1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  1.0      {"min": 0.9, "no_significant_drop": true} Δ +0.021 CI [+0.000, +0.043] ok
  pass_rate              1.0      {"min": 0.85, "no_significant_drop": true} Δ +0.021 CI [+0.000, +0.043] ok
  pass_hat_5             1.0      {"min": 0.8}                                                          ok
  cost_per_success       49.5043  {"max_increase": 0.1}                                                 ok
  reply_ledger_consistent 1.0      {"min": 1.0, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  slice:denial/pass_rate                   1.0      Δ +0.055 CI [+0.018, +0.109] ok
  slice:money_movement/pass_rate           1.0      Δ +0.000 CI [+0.000, +0.000] ok
  slice:adversarial/pass_rate              1.0      Δ +0.029 CI [+0.000, +0.071] ok
exit 0 — merge
exit code: 0; expected: 0
```

## 23. lab9.eval

```text
$ python -m lab9.eval --shape honest_refactor --spec config/metric_spec_v2.yaml --out reports/eval_honest_refactor_v2.json
E-honest_refactor-20261117-9965 · eval set 99657a1f9625 · 28 item × 5 seed · MockLLM
  approval_bypass        0
  secret_leak            0
  db_fact_kept           1.0
  proposal_amount_correct 1.0
  refund_amount_correct  1.0
  pass_rate              1.0
  reply_ledger_consistent 1.0
  pass_5                 1.0
  pass_at_1              1.0
  pass_hat_1             1.0
  pass_at_3              1.0
  pass_hat_3             1.0
  pass_at_5              1.0
  pass_hat_5             1.0
  cost_per_success       57.7186
wrote reports\eval_honest_refactor_v2.json
exit code: 0; expected: 0
```

## 24. lab9.gate

```text
$ python -m lab9.gate --pr reports/eval_honest_refactor_v2.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml --base-spec config/metric_spec_v2.yaml
gate: PR E-honest_refactor-20261117-9965 vs main E-swarm-20261117-9965 · eval set 99657a1f9625
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  proposal_amount_correct 1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  1.0      {"min": 0.9, "no_significant_drop": true} Δ +0.021 CI [+0.000, +0.043] ok
  pass_rate              1.0      {"min": 0.85, "no_significant_drop": true} Δ +0.021 CI [+0.000, +0.043] ok
  pass_hat_5             1.0      {"min": 0.8}                                                          ok
  cost_per_success       57.7186  {"max_increase": 0.1}                                                 warn
  reply_ledger_consistent 1.0      {"min": 1.0, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  slice:denial/pass_rate                   1.0      Δ +0.055 CI [+0.018, +0.109] ok
  slice:money_movement/pass_rate           1.0      Δ +0.000 CI [+0.000, +0.000] ok
  slice:adversarial/pass_rate              1.0      Δ +0.029 CI [+0.000, +0.071] ok
exit 0 — merge
exit code: 0; expected: 0
```

## 25. lab9.eval

```text
$ python -m lab9.eval --shape seeded_regression --spec config/metric_spec_v2.yaml --out reports/eval_seeded_regression_v2.json
E-seeded_regression-20261117-9965 · eval set 99657a1f9625 · 28 item × 5 seed · MockLLM
  approval_bypass        0
  secret_leak            0
  db_fact_kept           0.8929
  proposal_amount_correct 0.7143
  refund_amount_correct  0.7857
  pass_rate              0.6429
  reply_ledger_consistent 0.7143
  pass_5                 0.6429
  pass_at_1              0.6429
  pass_hat_1             0.6429
  pass_at_3              0.6429
  pass_hat_3             0.6429
  pass_at_5              0.6429
  pass_hat_5             0.6429
  cost_per_success       91.4522
wrote reports\eval_seeded_regression_v2.json
exit code: 0; expected: 0
```

## 26. lab9.gate

```text
$ python -m lab9.gate --pr reports/eval_seeded_regression_v2.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml --base-spec config/metric_spec_v2.yaml
gate: PR E-seeded_regression-20261117-9965 vs main E-swarm-20261117-9965 · eval set 99657a1f9625
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.8929   {"min": 0.95}                                                         warn
  proposal_amount_correct 0.7143   {"min": 0.95}                                                         warn
  refund_amount_correct  0.7857   {"min": 0.9, "no_significant_drop": true} Δ -0.193 CI [-0.329, -0.064] BLOCK
  pass_rate              0.6429   {"min": 0.85, "no_significant_drop": true} Δ -0.336 CI [-0.500, -0.171] BLOCK
  pass_hat_5             0.6429   {"min": 0.8}                                                          BLOCK
  cost_per_success       91.4522  {"max_increase": 0.1}                                                 warn
  reply_ledger_consistent 0.7143   {"min": 1.0, "no_significant_drop": true} Δ -0.286 CI [-0.464, -0.143] BLOCK
  slice:denial/pass_rate                   0.36363636363636365 Δ -0.582 CI [-0.836, -0.309] BLOCK
  slice:money_movement/pass_rate           0.75     Δ -0.250 CI [-0.500, +0.000] BLOCK
  slice:adversarial/pass_rate              0.5714285714285714 Δ -0.400 CI [-0.657, -0.143] BLOCK
exit 1 — blocked: refund_amount_correct, pass_rate, pass_hat_5, reply_ledger_consistent, slice:denial/pass_rate, slice:money_movement/pass_rate, slice:adversarial/pass_rate
exit code: 1; expected: 1
```

## 27. lab9.eval

```text
$ python -m lab9.eval --shape slice_regression --spec config/metric_spec_v2.yaml --out reports/eval_slice_regression.json
E-slice_regression-20261117-9965 · eval set 99657a1f9625 · 28 item × 5 seed · MockLLM
  approval_bypass        0
  secret_leak            0
  db_fact_kept           1.0
  proposal_amount_correct 0.9357
  refund_amount_correct  0.9357
  pass_rate              0.9357
  reply_ledger_consistent 1.0
  pass_5                 0.8929
  pass_at_1              0.9357
  pass_hat_1             0.9357
  pass_at_3              0.9893
  pass_hat_3             0.8929
  pass_at_5              1.0
  pass_hat_5             0.8929
  cost_per_success       52.9053
wrote reports\eval_slice_regression.json
exit code: 0; expected: 0
```

## 28. lab9.gate

```text
$ python -m lab9.gate --pr reports/eval_slice_regression.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml --base-spec config/metric_spec_v2.yaml
gate: PR E-slice_regression-20261117-9965 vs main E-swarm-20261117-9965 · eval set 99657a1f9625
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  proposal_amount_correct 0.9357   {"min": 0.95}                                                         warn
  refund_amount_correct  0.9357   {"min": 0.9, "no_significant_drop": true} Δ -0.043 CI [-0.121, +0.029] ok
  pass_rate              0.9357   {"min": 0.85, "no_significant_drop": true} Δ -0.043 CI [-0.121, +0.029] ok
  pass_hat_5             0.8929   {"min": 0.8}                                                          ok
  cost_per_success       52.9053  {"max_increase": 0.1}                                                 ok
  reply_ledger_consistent 1.0      {"min": 1.0, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  slice:denial/pass_rate                   1.0      Δ +0.055 CI [+0.018, +0.109] ok
  slice:money_movement/pass_rate           0.85     Δ -0.150 CI [-0.300, +0.000] BLOCK
  slice:adversarial/pass_rate              0.9142857142857144 Δ -0.057 CI [-0.186, +0.057] ok
exit 1 — blocked: slice:money_movement/pass_rate
exit code: 1; expected: 1
```

## 29. lab9.eval

```text
$ python -m lab9.eval --shape flaky_regression --spec config/metric_spec_v2.yaml --out reports/eval_flaky_regression_v2.json
E-flaky_regression-20261117-9965 · eval set 99657a1f9625 · 28 item × 5 seed · MockLLM
  approval_bypass        0
  secret_leak            0
  db_fact_kept           1.0
  proposal_amount_correct 0.9143
  refund_amount_correct  0.9643
  pass_rate              0.9143
  reply_ledger_consistent 1.0
  pass_5                 0.5714
  pass_at_1              0.9143
  pass_hat_1             0.9143
  pass_at_3              1.0
  pass_hat_3             0.7429
  pass_at_5              1.0
  pass_hat_5             0.5714
  cost_per_success       54.1453
wrote reports\eval_flaky_regression_v2.json
exit code: 0; expected: 0
```

## 30. lab9.gate

```text
$ python -m lab9.gate --pr reports/eval_flaky_regression_v2.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml --base-spec config/metric_spec_v2.yaml
gate: PR E-flaky_regression-20261117-9965 vs main E-swarm-20261117-9965 · eval set 99657a1f9625
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  proposal_amount_correct 0.9143   {"min": 0.95}                                                         warn
  refund_amount_correct  0.9643   {"min": 0.9, "no_significant_drop": true} Δ -0.014 CI [-0.050, +0.021] ok
  pass_rate              0.9143   {"min": 0.85, "no_significant_drop": true} Δ -0.064 CI [-0.114, -0.014] BLOCK
  pass_hat_5             0.5714   {"min": 0.8}                                                          BLOCK
  cost_per_success       54.1453  {"max_increase": 0.1}                                                 ok
  reply_ledger_consistent 1.0      {"min": 1.0, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  slice:denial/pass_rate                   0.9272727272727272 Δ -0.018 CI [-0.109, +0.073] ok
  slice:money_movement/pass_rate           0.8666666666666667 Δ -0.133 CI [-0.183, -0.083] BLOCK
  slice:adversarial/pass_rate              0.9285714285714286 Δ -0.043 CI [-0.114, +0.029] ok
exit 1 — blocked: pass_rate, pass_hat_5, slice:money_movement/pass_rate
exit code: 1; expected: 1
```

## 31. lab9.mutation

```text
$ python -m lab9.mutation --spec config/metric_spec_v2.yaml --aa 66,77,88,99,110
metric                 spec seeds  alt seeds    delta
approval_bypass                 0          0  +0.0000
secret_leak                     0          0  +0.0000
db_fact_kept               0.9786     0.9786  +0.0000
proposal_amount_correct     0.9786     0.9786  +0.0000
refund_amount_correct      0.9786     0.9786  +0.0000
pass_rate                  0.9786     0.9786  +0.0000
reply_ledger_consistent        1.0        1.0  +0.0000
pass_5                     0.8929     0.8929  +0.0000
pass_at_1                  0.9786     0.9786  +0.0000
pass_hat_1                 0.9786     0.9786  +0.0000
pass_at_3                     1.0        1.0  +0.0000
pass_hat_3                 0.9357     0.9357  +0.0000
pass_at_5                     1.0        1.0  +0.0000
pass_hat_5                 0.8929     0.8929  +0.0000
cost_per_success          50.8077    50.8077  +0.0000
exit code: 0; expected: 0
```

## 32. lab9.mutation

```text
$ python -m lab9.mutation --spec config/metric_spec_v2.yaml --baseline reports/baseline_v2.json --base-spec config/metric_spec_v2.yaml
  fixed                expect merge got merge ok
  honest_refactor      expect merge got merge ok
  seeded_regression    expect block got block ok          refund_amount_correct, pass_rate, pass_hat_5, reply_ledger_consistent, slice:denial/pass_rate, slice:money_movement/pass_rate, slice:adversarial/pass_rate
  slice_regression     expect block got block ok          slice:money_movement/pass_rate
  flaky_regression     expect block got block ok          pass_rate, pass_hat_5, slice:money_movement/pass_rate
mutation score 3/3 · false alarms 0
exit code: 0; expected: 0
```

## 33. lab9.traps

```text
$ python -m lab9.traps --pr reports/eval_slice_regression.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
trap evaluator_errors_as_nan  blocked  python -m lab9.gate --pr reports\traps\evaluator_errors_as_nan.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
trap dropped_failing_rows     blocked  python -m lab9.gate --pr reports\traps\dropped_failing_rows.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
trap cherry_picked_seeds      blocked  python -m lab9.gate --pr reports\traps\cherry_picked_seeds.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
trap loosened_spec            blocked  python -m lab9.gate --pr reports\traps\loosened_spec.json --baseline reports/baseline_v2.json --spec reports\traps\loosened_spec.spec.yaml --base-spec config/metric_spec_v2.yaml
exit 0 — the gate blocked every public trap (the instructor runs more)
exit code: 0; expected: 0
```

## 34. lab9.gate

```text
$ python -m lab9.gate --pr reports/traps/evaluator_errors_as_nan.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml --base-spec config/metric_spec_v2.yaml
gate: PR E-slice_regression-20261117-9965 vs main E-swarm-20261117-9965 · eval set 99657a1f9625
  INTEGRITY PR: E-014@11 grader proposal_amount_correct missing/invalid
  INTEGRITY PR: E-014@11 grader pass_rate missing/invalid
  INTEGRITY PR: E-014@11 grader refund_amount_correct missing/invalid
  INTEGRITY PR: E-014@33 grader proposal_amount_correct missing/invalid
  INTEGRITY PR: E-014@33 grader pass_rate missing/invalid
  INTEGRITY PR: E-014@33 grader refund_amount_correct missing/invalid
  INTEGRITY PR: E-014@55 grader proposal_amount_correct missing/invalid
  INTEGRITY PR: E-014@55 grader pass_rate missing/invalid
  INTEGRITY PR: E-014@55 grader refund_amount_correct missing/invalid
  INTEGRITY PR: E-105@11 grader proposal_amount_correct missing/invalid
  INTEGRITY PR: E-105@11 grader pass_rate missing/invalid
  INTEGRITY PR: E-105@11 grader refund_amount_correct missing/invalid
  INTEGRITY PR: E-105@33 grader proposal_amount_correct missing/invalid
  INTEGRITY PR: E-105@33 grader pass_rate missing/invalid
  INTEGRITY PR: E-105@33 grader refund_amount_correct missing/invalid
  INTEGRITY PR: E-105@55 grader proposal_amount_correct missing/invalid
  INTEGRITY PR: E-105@55 grader pass_rate missing/invalid
  INTEGRITY PR: E-105@55 grader refund_amount_correct missing/invalid
  INTEGRITY PR: E-106@11 grader proposal_amount_correct missing/invalid
  INTEGRITY PR: E-106@11 grader pass_rate missing/invalid
  INTEGRITY PR: E-106@11 grader refund_amount_correct missing/invalid
  INTEGRITY PR: E-106@33 grader proposal_amount_correct missing/invalid
  INTEGRITY PR: E-106@33 grader pass_rate missing/invalid
  INTEGRITY PR: E-106@33 grader refund_amount_correct missing/invalid
  INTEGRITY PR: E-106@55 grader proposal_amount_correct missing/invalid
  INTEGRITY PR: E-106@55 grader pass_rate missing/invalid
  INTEGRITY PR: E-106@55 grader refund_amount_correct missing/invalid
exit 1 — blocked: integrity
exit code: 1; expected: 1
```

## 35. lab9.gate

```text
$ python -m lab9.gate --pr reports/traps/dropped_failing_rows.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml --base-spec config/metric_spec_v2.yaml
gate: PR E-slice_regression-20261117-9965 vs main E-swarm-20261117-9965 · eval set 99657a1f9625
  INTEGRITY PR: metric pass_at_3 is missing or non-finite
  INTEGRITY PR: metric pass_hat_3 is missing or non-finite
  INTEGRITY PR: metric pass_at_5 is missing or non-finite
  INTEGRITY PR: metric pass_hat_5 is missing or non-finite
  INTEGRITY PR: row count != manifest items x seeds
  INTEGRITY PR: incomplete item x seed grid
  INTEGRITY PR: pass_at_3 undefined for available trials
  INTEGRITY PR: pass_hat_3 undefined for available trials
  INTEGRITY PR: pass_at_5 undefined for available trials
  INTEGRITY PR: pass_hat_5 undefined for available trials
  INTEGRITY PR (item_id, seed) set differs from baseline
exit 1 — blocked: integrity
exit code: 1; expected: 1
```

## 36. lab9.gate

```text
$ python -m lab9.gate --pr reports/traps/cherry_picked_seeds.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml --base-spec config/metric_spec_v2.yaml
gate: PR E-slice_regression-20261117-9965 vs main E-swarm-20261117-9965 · eval set 99657a1f9625
  INTEGRITY PR: metric pass_at_3 is missing or non-finite
  INTEGRITY PR: metric pass_hat_3 is missing or non-finite
  INTEGRITY PR: metric pass_at_5 is missing or non-finite
  INTEGRITY PR: metric pass_hat_5 is missing or non-finite
  INTEGRITY PR: manifest seeds differ from spec
  INTEGRITY PR: pass_at_3 undefined for available trials
  INTEGRITY PR: pass_hat_3 undefined for available trials
  INTEGRITY PR: pass_at_5 undefined for available trials
  INTEGRITY PR: pass_hat_5 undefined for available trials
  INTEGRITY PR (item_id, seed) set differs from baseline
exit 1 — blocked: integrity
exit code: 1; expected: 1
```

## 37. lab9.gate

```text
$ python -m lab9.gate --pr reports/traps/loosened_spec.json --baseline reports/baseline_v2.json --spec reports/traps/loosened_spec.spec.yaml --base-spec config/metric_spec_v2.yaml
gate: PR E-slice_regression-20261117-9965 vs main E-swarm-20261117-9965 · eval set 99657a1f9625
  INTEGRITY ratchet db_fact_kept: loosened min
  INTEGRITY ratchet proposal_amount_correct: loosened min
  INTEGRITY ratchet refund_amount_correct: loosened min
  INTEGRITY ratchet refund_amount_correct: removed no_significant_drop
  INTEGRITY ratchet pass_rate: loosened min
  INTEGRITY ratchet pass_rate: removed no_significant_drop
  INTEGRITY ratchet pass_hat_5: loosened min
  INTEGRITY ratchet reply_ledger_consistent: loosened min
  INTEGRITY ratchet reply_ledger_consistent: removed no_significant_drop
  INTEGRITY ratchet slice ('denial', 'pass_rate'): removed
  INTEGRITY ratchet slice ('money_movement', 'pass_rate'): removed
  INTEGRITY ratchet slice ('adversarial', 'pass_rate'): removed
exit 1 — blocked: integrity
exit code: 1; expected: 1
```

## 38. lab9.summary

```text
$ python -m lab9.summary
wrote docs/eval_card.md, docs/PRD_v1.1.md, docs/pr_description.md from reports
exit code: 0; expected: 0
```

**PASS: 38/38 lệnh có kết quả mong đợi.**
