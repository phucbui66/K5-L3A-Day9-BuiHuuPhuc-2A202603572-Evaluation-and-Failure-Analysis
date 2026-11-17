"""Build numeric submission documents from generated reports, never edit the reports."""
from __future__ import annotations

import json
import re
from pathlib import Path

from lab9.eval import load_spec, per_item
from lab9.gate import check
from lab9.judge import calibrate
from lab9.stats import paired_bootstrap


def read(name: str) -> dict:
    return json.loads(Path("reports", name).read_text(encoding="utf-8"))


def main() -> int:
    docs = Path("../docs")
    spec1, spec2 = [load_spec(Path(f"config/{name}")) for name in ("metric_spec.yaml", "metric_spec_v2.yaml")]
    base, fixed, bad = [read(name) for name in ("baseline_v1.json", "eval_fixed.json", "eval_seeded_regression.json")]
    base2 = read("baseline_v2.json")
    tone, helpful = [calibrate(Path(f"data/eval/judge_{name}_public.csv")) for name in ("tone", "helpful")]
    table = ["| Metric | Swarm baseline | Fixed | Seeded regression | Ngưỡng v1 | Blocking |",
             "|---|---|---|---|---|---|"]
    for m in spec1["metrics"]:
        mid = m["id"]
        table.append(f"| {mid} | {base['metrics'][mid]} | {fixed['metrics'][mid]} | {bad['metrics'][mid]} | "
                     f"`{json.dumps(m.get('threshold', {}))}` | {'có' if m.get('blocking') else 'không'} |")
    ci = []
    for name, report in (("fixed", fixed), ("seeded_regression", bad)):
        a, b = per_item(report, "pass_rate"), per_item(base, "pass_rate")
        keys = sorted(a)
        delta, lo, hi = paired_bootstrap([a[k] for k in keys], [b[k] for k in keys])
        ci.append(f"- {name}: Δ pass_rate={delta:+.3f}, CI 95% [{lo:+.3f}, {hi:+.3f}].")
    v2table = ["| Shape | Run ID | pass_rate | pass_hat_5 | Quyết định và metric chặn |",
               "|---|---|---|---|---|"]
    for shape in ("fixed", "honest_refactor", "seeded_regression", "slice_regression", "flaky_regression"):
        name = f"eval_{shape}_v2.json" if shape != "slice_regression" else "eval_slice_regression.json"
        report = read(name)
        blocked, _ = check(report, base2, spec2, spec2)
        verdict = "BLOCK: " + ", ".join(blocked) if blocked else "merge"
        v2table.append(f"| {shape} | {report['run_id']} | {report['metrics']['pass_rate']} | "
                       f"{report['metrics']['pass_hat_5']} | {verdict} |")
    manifest = base["manifest"]
    identity = (f"Baseline v1: **{base['run_id']}**, eval SHA `{manifest['eval_set_sha']}`, "
                f"labels SHA `{manifest['labels_sha']}`, source SHA `{manifest['source_sha']}`, spec SHA `{manifest['spec_sha']}`.\n\n"
                f"Fixed: **{fixed['run_id']}**. Regression: **{bad['run_id']}**.\n\n"
                f"Baseline v2: **{base2['run_id']}**, eval SHA `{base2['manifest']['eval_set_sha']}`, "
                f"labels SHA `{base2['manifest']['labels_sha']}`.\n")
    limitations = (
        "- MockLLM và chi phí mô phỏng; không đo chất lượng model thật, latency hoặc chi phí API thật.\n"
        "- V1 chỉ 14 item, v2 28 item; seed cùng claim phụ thuộc nhau nên bootstrap theo item, không theo 70/140 row.\n"
        "- CSV judge là replay công khai, chưa có nhãn người held-out mới; không suy rộng calibration sang production.\n"
        "- DbFactKept dựa vào event nên bỏ sót quiet_override; grader outcome và pass_hat_5 bổ sung kiểm tra độc lập.\n"
        "- FM-08 chỉ so số tiền biểu diễn bằng chữ số kèm đơn vị tiền trong reply; chưa hiểu mọi cách viết bằng chữ, "
        "mọi hứa hẹn tương lai hoặc reply không có số tiền. Swarm cũ không có reply event nên điểm 1 chỉ nghĩa không quan sát được mâu thuẫn.\n"
        "- Biến thể rare chỉ bật khi seed chia hết cho 3: bộ chuẩn có một seed kích hoạt, bộ A/A khác có hai. "
        "Với bug xác suất 1/3 và 5 lần độc lập, xác suất bỏ sót toàn bộ là (2/3)^5 ≈ 13,17%; không phát hiện ổn định. "
        "Không hạ ngưỡng để khớp một seed; cần thêm seed/item và dữ liệu thực.\n"
        "- Integrity kiểm tra tính đầy đủ và nhất quán, không chứng minh một report được tính trung thực nếu cả rows, summary "
        "và grader đều bị giả mạo đồng bộ; cần CI chạy lại trên runner đáng tin và bảo vệ baseline/spec.\n")
    calibration = (f"Tone: κ={tone['kappa']}, P={tone['precision']}, R={tone['recall']}; đạt floors. "
                   f"Helpful: κ={helpful['kappa']}, P={helpful['precision']}, R={helpful['recall']}; loại khỏi gate. "
                   "Xem [audit 10 bất đồng](judge_audit.md).\n")
    card = ("# Eval card — LogiX-VN\n\nSinh từ report bằng `python -m lab9.summary`; "
            "không sửa JSON report. Bùi Hữu Phúc — 2A202603572.\n\n" + identity +
            "\nCode/grader được nhận diện bằng source SHA trên manifest; commit chứa chúng tra trong Git. "
            "Đây là snapshot đang làm bài, không tự nhận đã được review hoặc phê duyệt release.\n\n"
            "## V1: 14 item × 5 seed\n\nNguồn Lab 8 public; nhãn tách riêng; seeds 11/22/33/44/55. "
            "Metric spec 1.0; paired bootstrap percentile, 1.000 resample, RNG 2027, CI 95%.\n\n" +
            "\n".join(table) + "\n\n" + "\n".join(ci) + "\n\n" + calibration +
            "\n[Trace case](trace_case.md): C-002@11 sai đầu tiên tại event 3 model_override. "
            "Test tái hiện lỗi và đối chứng fixed trong [regression tests](../src/tests/test_lab9_regressions.py).\n\n"
            "## V2: slices, nhiễu, tính toàn vẹn\n\n" + "\n".join(v2table) +
            f"\n\nBaseline pass_hat_5={base2['metrics']['pass_hat_5']}. Hai bộ seed "
            "11/22/33/44/55 và 66/77/88/99/110 cho Δ A/A=0 trên mọi metric MockLLM. "
            "Sàn pass_hat_5=0.80 thấp hơn baseline và nằm dưới dải A/A suy biến, có khoảng đệm; "
            "giữ sàn ≥0.8 theo yêu cầu. Dữ liệu LLM thật có dải nhiễu rộng hơn: đo A/A lặp lại "
            "và chọn sàn dưới cận thấp của agent chấp nhận được, không chỉnh theo mutant.\n\n"
            "pass@k = 1 − C(n−c,k)/C(n,k); pass^k = C(c,k)/C(n,k). "
            "pass@5 có thể đạt 1 dù agent chập chờn; pass^5 yêu cầu mọi lượt thành công.\n\n"
            "money_movement và adversarial dùng sàn 0.90 cùng paired CI; denial cũng blocking. "
            "Slice regression bị chặn riêng tại money_movement; flaky bị chặn bởi pass_hat_5 và các điều kiện ghi trong bảng. "
            "Mutation 3/3, 0 báo nhầm; bốn trap đều exit 1; xem [output tái lập](verification.md).\n\n"
            "## Vận hành pilot\n\nEval owner: Bùi Hữu Phúc. Gate đỏ: dừng merge, đọc failure reason và trace, "
            "sửa agent hoặc grader theo bằng chứng, chạy lại; không sửa report hoặc nới sàn. "
            "Pilot chỉ offline, đơn thuộc principal và approval hợp lệ, tiền do host tính theo policy. "
            "Chưa phê duyệt pilot người dùng thật.\n\n## Giới hạn\n\n" + limitations +
            "\nThêm/sửa item hoặc nhãn → tăng eval-set version, review provenance và chạy lại baseline. "
            "Thay metric/ngưỡng → tăng metric-spec version, giữ ratchet trên cùng eval-set version.\n")
    (docs / "eval_card.md").write_text(card, encoding="utf-8")
    prd = ("# PRD v1.1 — tiêu chí đánh giá LogiX-VN\n\n" + identity +
           "\n## Thay đổi so với v1.0\n\nGiữ tính năng refund của Lab 8; bổ sung định nghĩa chạy đúng, "
           "failure taxonomy, calibration và cổng merge có thể tái lập. Bằng chứng là report và exit code, không dựa demo thủ công.\n\n"
           "## Phạm vi\n\nPilot offline với claim một đơn trong public world; chỉ principal hợp lệ, "
           "approval còn hạn và giới hạn tiền do policy/host áp dụng. Không mở rộng sang tranh chấp nhiều đơn "
           "hoặc giao dịch production. Chưa có bằng chứng người dùng thật.\n\n## Chạy đúng nghĩa là gì\n\n" +
           "\n".join(table) + "\n\nV2 dùng [spec 2.0](../src/config/metric_spec_v2.yaml): "
           "refund_amount_correct ≥0.90, pass_rate ≥0.85; pass_hat_5 ≥0.80; "
           "reply_ledger_consistent=1; safety bằng 0; money_movement/adversarial/denial ≥0.90 và không giảm có ý nghĩa. "
           "V2 là eval-set version mới với baseline mới; không nới ngưỡng v1.\n\n"
           "Giảm có ý nghĩa: cận trên CI 95% paired bootstrap của PR − baseline <0. "
           "Đơn vị resample là item, trung bình trên cùng seed, ghép đúng item ID.\n\n"
           "## Failure mode và grader\n\nXem [taxonomy đủ FM-01–FM-09](failure_taxonomy.md). "
           "Secret/approval/ledger/proposal/reply-money được kiểm tra bằng code; FM-03 có event grader cộng outcome grader. "
           "ProposalAmountCorrect bổ sung phát hiện FM-05 khi host không ghi tiền nên ledger vẫn đúng. "
           "Không dùng helpful làm gate. " + calibration +
           "\n## Cổng release và trách nhiệm\n\n[Workflow](../.github/workflows/eval-gate.yml) chạy smoke, tests, "
           "kiểm tra snapshot Lab 8/eval set, tái tính swarm và đối chiếu baseline, gate fixed/regression, mutation và traps. "
           "Baseline/spec phải được review, commit và bảo vệ; ratchet dùng --base-spec. "
           "Gate exit 1: không merge. Eval owner Bùi Hữu Phúc xử lý nguyên nhân và chạy lại. "
           "Waiver phải do người phụ trách môn/maintainer duyệt bằng văn bản trong PR, nêu rủi ro và thời hạn; "
           "bài làm này không có waiver hoặc phê duyệt được giả định.\n\n"
           "## Bằng chứng còn thiếu\n\n" + limitations +
           "\n## Khi nào lên phiên bản mới\n\nThêm case/đổi label → eval-set version và baseline mới. "
           "Đổi metric → metric-spec version và mô tả lý do. Trước pilot thật cần model thật, "
           "held-out labels, thêm seed, kiểm thử an toàn và chủ sản phẩm phê duyệt.\n\n"
           "| Vai trò | Người phụ trách / trạng thái |\n|---|---|\n"
           "| Eval owner | Bùi Hữu Phúc — tác giả bài làm |\n"
           "| Product / maintainer | Chưa ghi nhận phê duyệt |\n")
    (docs / "PRD_v1.1.md").write_text(prd, encoding="utf-8")
    pr = ("# Lab 9 — Evaluation & Failure Analysis (M0–M7)\n\n"
          "Hoàn thiện eval set, calibration, trajectory graders, paired gate, slice/reliability gate và integrity/ratchet. "
          "Giữ nguyên snapshot mã Lab 8; không sửa variants, traps hoặc test công khai.\n\n" + identity +
          "\n## Core\n\n" + "\n".join(ci) +
          "\n\n```text\nexit 0 — merge (fixed)\nexit 1 — blocked: " + ", ".join(check(bad, base, spec1)[0]) +
          "\n```\n\n## Advanced / Expert\n\n" + "\n".join(v2table) +
          "\n\nOutput mutation, A/A và bốn trap exit 1: [verification.md](verification.md). "
          "Tái lập toàn bộ: `cd src` rồi `python -m lab9.verify`. "
          "[Eval card](eval_card.md), [PRD](PRD_v1.1.md), [judge audit](judge_audit.md).\n\n"
          "Chưa khẳng định GitHub Actions xanh cho tới khi workflow thực sự chạy trên remote. "
          "Giới hạn: MockLLM, tập nhỏ, judge replay; không có phê duyệt production.\n")
    evidence_path = docs / "verification.md"
    if evidence_path.is_file():
        blocks = re.findall(r"```text\n(.*?)\n```", evidence_path.read_text(encoding="utf-8"), re.S)
        mutation_blocks = [b for b in blocks if b.startswith("$ python -m lab9.mutation")
                           and ("--aa " in b or "--baseline " in b)]
        trap_blocks = [b for b in blocks if b.startswith("$ python -m lab9.gate --pr reports/traps/")]
        pr += "\n## Output thực tế để đối chiếu\n\n"
        pr += "\n\n".join("```text\n" + b + "\n```" for b in mutation_blocks)
        if trap_blocks:
            verdicts = [b.splitlines()[0] + "\n" + next(line for line in reversed(b.splitlines())
                        if line.startswith("exit 1")) for b in trap_blocks]
            pr += "\n\n### Bốn trap đều trả exit 1\n\n```text\n" + "\n".join(verdicts) + "\n```\n"
    (docs / "pr_description.md").write_text(pr, encoding="utf-8")
    print("wrote docs/eval_card.md, docs/PRD_v1.1.md, docs/pr_description.md from reports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
