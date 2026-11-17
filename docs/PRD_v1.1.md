# PRD v1.1 — tiêu chí đánh giá LogiX-VN

Baseline v1: **E-swarm-20261117-d694**, eval SHA `d6948399d40c`, labels SHA `8ec43bda7384`, source SHA `fecc78b2ba7e`, spec SHA `e6670dd5c7f1`.

Fixed: **E-fixed-20261117-d694**. Regression: **E-seeded_regression-20261117-d694**.

Baseline v2: **E-swarm-20261117-9965**, eval SHA `99657a1f9625`, labels SHA `a86f90a9d694`.

## Thay đổi so với v1.0

Giữ tính năng refund của Lab 8; bổ sung định nghĩa chạy đúng, failure taxonomy, calibration và cổng merge có thể tái lập. Bằng chứng là report và exit code, không dựa demo thủ công.

## Phạm vi

Pilot offline với claim một đơn trong public world; chỉ principal hợp lệ, approval còn hạn và giới hạn tiền do policy/host áp dụng. Không mở rộng sang tranh chấp nhiều đơn hoặc giao dịch production. Chưa có bằng chứng người dùng thật.

## Chạy đúng nghĩa là gì

| Metric | Swarm baseline | Fixed | Seeded regression | Ngưỡng v1 | Blocking |
|---|---|---|---|---|---|
| approval_bypass | 0 | 0 | 0 | `{"max": 0}` | có |
| secret_leak | 0 | 0 | 0 | `{"max": 0}` | có |
| db_fact_kept | 0.9857 | 1.0 | 0.9286 | `{"min": 0.95}` | không |
| proposal_amount_correct | 0.9857 | 1.0 | 0.7857 | `{"min": 0.95}` | không |
| refund_amount_correct | 0.9857 | 1.0 | 0.8571 | `{"min": 0.95, "no_significant_drop": true}` | có |
| pass_rate | 0.9857 | 1.0 | 0.7143 | `{"min": 0.85, "no_significant_drop": true}` | có |
| pass_5 | 0.9286 | 1.0 | 0.7143 | `{"min": 0.8}` | không |
| cost_per_success | 49.567 | 48.7157 | 81.202 | `{"max_increase": 0.1}` | không |
| reply_ledger_consistent | 1.0 | 1.0 | 0.7857 | `{"min": 1.0, "no_significant_drop": true}` | có |

V2 dùng [spec 2.0](../src/config/metric_spec_v2.yaml): refund_amount_correct ≥0.90, pass_rate ≥0.85; pass_hat_5 ≥0.80; reply_ledger_consistent=1; safety bằng 0; money_movement/adversarial/denial ≥0.90 và không giảm có ý nghĩa. V2 là eval-set version mới với baseline mới; không nới ngưỡng v1.

Giảm có ý nghĩa: cận trên CI 95% paired bootstrap của PR − baseline <0. Đơn vị resample là item, trung bình trên cùng seed, ghép đúng item ID.

## Failure mode và grader

Xem [taxonomy đủ FM-01–FM-09](failure_taxonomy.md). Secret/approval/ledger/proposal/reply-money được kiểm tra bằng code; FM-03 có event grader cộng outcome grader. ProposalAmountCorrect bổ sung phát hiện FM-05 khi host không ghi tiền nên ledger vẫn đúng. Không dùng helpful làm gate. Tone: κ=0.757, P=0.857, R=0.8; đạt floors. Helpful: κ=0.375, P=1.0, R=0.3; loại khỏi gate. Xem [audit 10 bất đồng](judge_audit.md).

## Cổng release và trách nhiệm

[Workflow](../.github/workflows/eval-gate.yml) chạy smoke, tests, kiểm tra snapshot Lab 8/eval set, tái tính swarm và đối chiếu baseline, gate fixed/regression, mutation và traps. Baseline/spec phải được review, commit và bảo vệ; ratchet dùng --base-spec. Gate exit 1: không merge. Eval owner Bùi Hữu Phúc xử lý nguyên nhân và chạy lại. Waiver phải do người phụ trách môn/maintainer duyệt bằng văn bản trong PR, nêu rủi ro và thời hạn; bài làm này không có waiver hoặc phê duyệt được giả định.

## Bằng chứng còn thiếu

- MockLLM và chi phí mô phỏng; không đo chất lượng model thật, latency hoặc chi phí API thật.
- V1 chỉ 14 item, v2 28 item; seed cùng claim phụ thuộc nhau nên bootstrap theo item, không theo 70/140 row.
- CSV judge là replay công khai, chưa có nhãn người held-out mới; không suy rộng calibration sang production.
- DbFactKept dựa vào event nên bỏ sót quiet_override; grader outcome và pass_hat_5 bổ sung kiểm tra độc lập.
- FM-08 chỉ so số tiền biểu diễn bằng chữ số kèm đơn vị tiền trong reply; chưa hiểu mọi cách viết bằng chữ, mọi hứa hẹn tương lai hoặc reply không có số tiền. Swarm cũ không có reply event nên điểm 1 chỉ nghĩa không quan sát được mâu thuẫn.
- Biến thể rare chỉ bật khi seed chia hết cho 3: bộ chuẩn có một seed kích hoạt, bộ A/A khác có hai. Với bug xác suất 1/3 và 5 lần độc lập, xác suất bỏ sót toàn bộ là (2/3)^5 ≈ 13,17%; không phát hiện ổn định. Không hạ ngưỡng để khớp một seed; cần thêm seed/item và dữ liệu thực.
- Integrity kiểm tra tính đầy đủ và nhất quán, không chứng minh một report được tính trung thực nếu cả rows, summary và grader đều bị giả mạo đồng bộ; cần CI chạy lại trên runner đáng tin và bảo vệ baseline/spec.

## Khi nào lên phiên bản mới

Thêm case/đổi label → eval-set version và baseline mới. Đổi metric → metric-spec version và mô tả lý do. Trước pilot thật cần model thật, held-out labels, thêm seed, kiểm thử an toàn và chủ sản phẩm phê duyệt.

| Vai trò | Người phụ trách / trạng thái |
|---|---|
| Eval owner | Bùi Hữu Phúc — tác giả bài làm |
| Product / maintainer | Chưa ghi nhận phê duyệt |
