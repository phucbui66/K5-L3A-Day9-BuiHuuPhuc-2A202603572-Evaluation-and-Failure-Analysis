# Judge audit

Các số dưới đây lấy từ `python -m lab9.judge --csv ... --audit 10`; output trong [biên bản kiểm tra](verification.md).
FAIL là lớp dương: precision đo tỉ lệ cảnh báo lỗi đúng, recall đo phần lỗi thật được phát hiện.

| Tiêu chí | n | TP/FP/FN/TN | κ | Precision | Recall | Rogan–Gladen: quan sát → hiệu chỉnh | Quyết định |
|---|---|---|---|---|---|---|---|
| tone_ok | 100 | 24 / 4 / 6 / 66 | 0.757 | 0.857 | 0.800 | 0.280 → 0.300 | Đạt κ≥0.6, P≥0.8, R≥0.7; đủ điều kiện dùng cho tone trong pilot replay. |
| helpful | 100 | 9 / 0 / 21 / 70 | 0.375 | 1.000 | 0.300 | 0.090 → 0.300 | Loại khỏi gate: bỏ sót 21/30 lỗi, κ và recall dưới sàn. |

Rogan–Gladen dùng sensitivity=recall, specificity=TN/(TN+FP), rồi clip về [0,1].
Tỉ lệ hiệu chỉnh không sửa từng verdict và không thay thế calibration.
κ không xác định được coi là FAIL; không cho judge hằng số qua bằng cách trả κ=1.

## Audit bất đồng

Đây là đánh giá lại từ reply và ghi chú CSV public, không phải vòng gán nhãn độc lập mới.

| Case | Judge | Người | Ai đúng theo bằng chứng replay? | Sửa rubric / hành động |
|---|---|---|---|---|
| H-008 | PASS | FAIL | Người: “em”, “nha”, “anh check” quá suồng sã theo quy chuẩn CS. | Thêm ví dụ FAIL cho xưng hô suồng sã; lịch sự không chỉ là câu chào. |
| H-017 | PASS | FAIL | Người: “bạn ơi”, “nha” không phù hợp ngữ cảnh khách trong ghi chú. | Quy định “anh/chị”; không suy ra tuổi từ văn bản ngoài dữ liệu được cung cấp. |
| H-029 | PASS | FAIL | Người: “không cần nhắn thêm” có giọng ra lệnh. | Chấm toàn câu; thêm ví dụ có “Dạ, vui lòng” nhưng vẫn FAIL. |
| H-042 | FAIL | PASS | Người: trả lời ngắn nhưng đủ thông tin và lịch sự. | Không bắt buộc xin lỗi trong mọi câu; bỏ thiên lệch thích câu dài. |
| H-051 | FAIL | PASS | Người: từ “refund” được quy chuẩn CS cho phép. | Liệt kê thuật ngữ hợp lệ; không phạt mọi từ tiếng Anh. |
| H-063 | PASS | FAIL | Người: hứa “sẽ hoàn thêm” ngoài kết quả hệ thống. | Cấm hứa khoản chưa được host xác nhận; chuyển kiểm tra tiền sang code. |
| H-070 | PASS | FAIL | Người: emoji cười không phù hợp khiếu nại. | Thêm ví dụ emoji thiếu tôn trọng; không chỉ kiểm tra đại từ. |
| H-081 | FAIL | PASS | Ghi chú bộ dữ liệu nêu nhãn người sai và judge đúng do đọc nhầm ticket. Chỉ reply không đủ xác minh toàn bộ ngữ cảnh. | Đưa vào hàng chờ adjudication cùng ticket; không sửa CSV public để tăng điểm. Calibration vẫn dùng nhãn replay nguyên bản. |
| HL-015 | PASS | FAIL | Người: nói 55.000đ, ghi chú ledger 40.000đ. | Helpful phải kiểm tra tính đúng; dùng grader code so reply với ledger. |
| HL-016 | PASS | FAIL | Người: xin lỗi dài nhưng nói 55.000đ, ledger 35.000đ. | Nội dung đúng là bắt buộc; không cộng điểm vì độ dài hoặc số lần xin lỗi. |

## Quyết định sử dụng

tone_ok chỉ đủ điều kiện cho tone; gate tiền và approval hiện dùng code.
helpful không được làm gate dù precision=1: judge chỉ báo các lỗi dễ, cho quá nhiều lỗi thật qua.
Không đổi nhãn hoặc CSV để làm đẹp calibration. Sửa rubric ở trên là đề xuất cho vòng kế tiếp, cần tập held-out có người gán nhãn mới.
CSV có thể có nhãn sai và chưa đại diện production; tỉ lệ FAIL trong pilot thay đổi cũng có thể làm precision thay đổi.
