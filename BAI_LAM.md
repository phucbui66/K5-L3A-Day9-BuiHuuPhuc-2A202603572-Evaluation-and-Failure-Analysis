# Bài làm Lab Day 9 — Bùi Hữu Phúc — 2A202603572

Đề gốc được giữ tại [README](README.md). Bài làm triển khai Core, Advanced và Expert (M0–M7), sử dụng snapshot Lab Day 8 của nhóm SaiGonBac.

## Đọc kết quả

| Nội dung | Tệp |
|---|---|
| Số liệu, run ID, ngưỡng, quyết định gate và giới hạn | [Eval card](docs/eval_card.md) |
| Định nghĩa chạy đúng và quy trình release | [PRD v1.1](docs/PRD_v1.1.md) |
| Chín failure mode, layer, bằng chứng, năm anchor | [Failure taxonomy](docs/failure_taxonomy.md) |
| Bước sai đầu tiên của C-002@11 và regression test | [Trace case](docs/trace_case.md) |
| Trace chẩn đoán đã lược secret | [Trace evidence](docs/trace_evidence.md) |
| Calibration và audit mười bất đồng | [Judge audit](docs/judge_audit.md) |
| Output kiểm tra, A/A, mutation và bốn trap | [Biên bản chạy](docs/verification.md) |
| Nội dung để mở PR | [Mô tả PR](docs/pr_description.md) |

## Chạy lại trên Windows

Python 3.11 trở lên; lần chạy này dùng Python 3.12. Mở PowerShell tại gốc repo:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r src\requirements.txt -r src\requirements-lab9.txt
cd src
..\.venv\Scripts\python.exe -m lab9.verify
```

Nếu môi trường đã có, chỉ chạy hai dòng cuối. Không cần kích hoạt PowerShell script, API key hoặc dịch vụ ngoài.
Lệnh verify chạy test, dựng lại eval set/report bằng script và sinh tài liệu số liệu. Một số gate **phải exit 1** để chứng minh regression/trap bị chặn; verify chỉ PASS khi các exit code đều đúng mong đợi.

## Phạm vi triển khai

- M0/M1: [eval set builder](src/lab9/evalset.py), nhãn tách riêng, provenance, FM v1 và [mapping v2](src/config/fm_map.yaml).
- M2/M4/M6: [thống kê](src/lab9/stats.py): confusion, P/R, κ, Rogan–Gladen, paired bootstrap, pass@k/pass^k và kiểm tra input.
- M3: [graders](src/lab9/graders.py): approval, ledger, số tiền đề xuất và reply so với ledger; grader code không gọi model.
- M5/M7: [gate](src/lab9/gate.py): slice, kiểm tra grid item×seed, row trùng/thiếu, None/NaN/inf, evaluator failure, summary sai, đổi slice/label và ratchet metric/slice.
- [Workflow](.github/workflows/eval-gate.yml) lấy spec của base branch để so ratchet, chạy lại swarm và kiểm tra baseline; giữ [CI Lab 8](.github/workflows/ci.yml).
- [Regression tests bổ sung](src/tests/test_lab9_regressions.py) kiểm tra trace thật, FM-08, quiet_override, test isolation và các trường hợp giả mạo báo cáo.

## Nguồn và bảo toàn Lab 8

Nguồn: repo local `K5-L3A-Day8-SaiGonBac-From-Workflows-to-Agents`, revision `4bf39fbff7897d04c334fa372085b9653288796d`.
Các thư viện, dữ liệu public, config nền, tests và CI cần thiết được chép vào repo Day 9 để repo này chạy độc lập.
Không ghi vào repo Day 8 gốc; 29 tệp Python trong [lab8](src/lab8) giữ nguyên từng byte so với bản nguồn lúc chép.
[Manifest SHA-256](src/config/lab8_snapshot.sha256.json) và `python -m lab9.check_source` cho phép kiểm chứng lại mà không cần repo nguồn.
Các variant và trap giảng viên cung cấp được giữ nguyên. JSON report được sinh bởi harness, không sửa tay.

## Nộp bài

Nhánh bài làm: `starter/d09`, PR đích: `main`. Hai baseline và các report kết quả chính được cho phép theo dõi trong Git;
trace, DB, môi trường ảo, secret và trap tạm vẫn bị loại trừ.
Dùng [mô tả PR](docs/pr_description.md) và bổ sung output trong [biên bản](docs/verification.md) khi mở PR.
Kết quả local không thay thế trạng thái GitHub Actions thực tế.

## Công cụ hỗ trợ

Bài làm có hỗ trợ AI (Codex) để triển khai code, viết test và phân tích trace; số liệu lấy từ lệnh chạy thật.
Phần cần đọc để giải thích khi bảo vệ: đơn vị bootstrap là item, FAIL là lớp dương của judge, proposal khác ledger sau cap/trừ khoản hoàn trước,
pass@k khác pass^k, và lý do gate phải từ chối báo cáo không đầy đủ trước khi so ngưỡng.
