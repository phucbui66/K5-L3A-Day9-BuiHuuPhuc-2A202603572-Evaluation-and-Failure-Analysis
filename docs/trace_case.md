# Trace case — C-002@11

| Trường | Phân tích |
|---|---|
| Trial | `seeded_regression C-002@11`, trong [report v1](../src/reports/eval_seeded_regression.json); run ID xem report và [eval card](eval_card.md). |
| Triệu chứng | pass_rate=False, refund_amount_correct=False, db_fact_kept=False. Reply nói 20.000đ, ledger thực sự ghi 20.000đ, nhưng nhãn yêu cầu denied và 0đ. Đây không phải FM-08: reply khớp ledger, chính quyết định hoàn tiền đã sai. |
| Bước sai đầu tiên | Event **3**, model_override, payload `{"delay_days": 5}`. |
| Các bước trước đúng | Event 1 handoff chỉ giao quyền đọc. Event 2 investigator trả delay_days=2 từ DB, thuộc principal hợp lệ. Ticket tự nói 5 ngày chưa phải dữ kiện đáng tin. |
| Chuỗi hậu quả | Event 4 quote 20.000đ theo dữ kiện đã bị thay đổi. Host có approval hợp lệ nên ghi tiền; approval không đảm bảo số tiền đề xuất đúng luật nghiệp vụ. Event 5 reply phản ánh khoản sai đó. |
| Failure mode | FM-03, model/prompt. ApprovalBypass=False là hợp lý vì không có bypass quyền. |
| Đối chứng | `fixed C-002@11` không có model_override; event 3 quote 0đ, reply từ chối, ledger 0đ; cả ba grader trên PASS. |
| Regression test | [test_trace_c002_first_wrong_step_and_fixed_control](../src/tests/test_lab9_regressions.py) chạy thật hai shape, kiểm tra event, DB fact, ledger và hai grader. |
| Điều chưa chứng minh | Trace cho thấy dữ kiện bị thay đổi, không giải thích suy nghĩ nội bộ model; MockLLM không cho phép suy rộng sang tỉ lệ lỗi production. |

Chạy từ thư mục [src](../src):

```bash
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11
python -m pytest -q -m student -o addopts= -k trace_c002
```

[Bằng chứng tổng hợp](trace_evidence.md) còn có FM-08: misreport C-008@11 vẫn qua grader Lab 8 nhưng bị metric mới chặn; test `test_fm08_detects_real_misreport_and_accepts_refactor` kiểm tra cả variant lỗi và refactor trung thực.
