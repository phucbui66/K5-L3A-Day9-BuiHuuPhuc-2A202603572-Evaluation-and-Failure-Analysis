# Lab 9 — Evaluation & Failure Analysis (M0–M7)

Hoàn thiện eval set, calibration, trajectory graders, paired gate, slice/reliability gate và integrity/ratchet. Giữ nguyên snapshot mã Lab 8; không sửa variants, traps hoặc test công khai.

Baseline v1: **E-swarm-20261117-ec06**, eval SHA `ec06ea074f14`, labels SHA `5c39cb294873`, source SHA `6c3324ac3050`, spec SHA `e6670dd5c7f1`.

Fixed: **E-fixed-20261117-ec06**. Regression: **E-seeded_regression-20261117-ec06**.

Baseline v2: **E-swarm-20261117-16a0**, eval SHA `16a09d0c71c1`, labels SHA `e8b49b4ec49f`.

## Core

- fixed: Δ pass_rate=+0.014, CI 95% [+0.000, +0.043].
- seeded_regression: Δ pass_rate=-0.271, CI 95% [-0.500, -0.057].

```text
exit 0 — merge (fixed)
exit 1 — blocked: refund_amount_correct, pass_rate, reply_ledger_consistent
```

## Advanced / Expert

| Shape | Run ID | pass_rate | pass_hat_5 | Quyết định và metric chặn |
|---|---|---|---|---|
| fixed | E-fixed-20261117-16a0 | 1.0 | 1.0 | merge |
| honest_refactor | E-honest_refactor-20261117-16a0 | 1.0 | 1.0 | merge |
| seeded_regression | E-seeded_regression-20261117-16a0 | 0.6429 | 0.6429 | BLOCK: refund_amount_correct, pass_rate, pass_hat_5, reply_ledger_consistent, slice:denial/pass_rate, slice:money_movement/pass_rate, slice:adversarial/pass_rate |
| slice_regression | E-slice_regression-20261117-16a0 | 0.9357 | 0.8929 | BLOCK: slice:money_movement/pass_rate |
| flaky_regression | E-flaky_regression-20261117-16a0 | 0.9143 | 0.5714 | BLOCK: pass_rate, pass_hat_5, slice:money_movement/pass_rate |

Output mutation, A/A và bốn trap exit 1: [verification.md](verification.md). Tái lập toàn bộ: `cd src` rồi `python -m lab9.verify`. [Eval card](eval_card.md), [PRD](PRD_v1.1.md), [judge audit](judge_audit.md).

Chưa khẳng định GitHub Actions xanh cho tới khi workflow thực sự chạy trên remote. Giới hạn: MockLLM, tập nhỏ, judge replay; không có phê duyệt production.

## Output thực tế để đối chiếu

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

### Bốn trap đều trả exit 1

```text
$ python -m lab9.gate --pr reports/traps/evaluator_errors_as_nan.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml --base-spec config/metric_spec_v2.yaml
exit 1 — blocked: integrity
$ python -m lab9.gate --pr reports/traps/dropped_failing_rows.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml --base-spec config/metric_spec_v2.yaml
exit 1 — blocked: integrity
$ python -m lab9.gate --pr reports/traps/cherry_picked_seeds.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml --base-spec config/metric_spec_v2.yaml
exit 1 — blocked: integrity
$ python -m lab9.gate --pr reports/traps/loosened_spec.json --baseline reports/baseline_v2.json --spec reports/traps/loosened_spec.spec.yaml --base-spec config/metric_spec_v2.yaml
exit 1 — blocked: integrity
```
