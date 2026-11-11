# Báo cáo cá nhân — Đoàn Xuân Duy Bảo - 2A202603858

## 1. Thông tin thành viên

- Họ tên: Đoàn Xuân Duy Bảo
- MSSV: 2A202603858
- Email: doanxuanduybao96@gmail.com

## 2. Phần việc phụ trách

Nhóm Hihihuhu cùng làm các phần của bài (xem [báo cáo nhóm](group_report.md)). Em chọn trình bày kỹ phần
**tối ưu prompt/tool v0 → v7 và đo lại bằng provider Gemini**, kèm 4 tool mới và bộ unit test.
Đây là một nhánh thử nghiệm riêng của em (nhánh `doanxuanduybao`), dùng để đối chiếu với
các run OpenRouter ở mục B1 của báo cáo nhóm. Em không dùng số của nhánh này để thay cho bảng B1 của nhóm.

Mã nguồn và run của phần này nằm ở nhánh `doanxuanduybao`, không nằm trong `main`. Các link ở mục 4 trỏ tới
commit `2b39c22` để người chấm mở được.

## 3. Đóng góp cụ thể

**Provider và baseline (CP1).** Sửa `providers/gemini_provider.py` để đọc `GEMINI_API_KEY` và `GEMINI_BASE_URL`.
Lần chạy `--provider gemini` đầu tiên báo `provider_error` cho cả 20 case vì thiếu package `google-genai`
(`RuntimeError: Install live provider dependency first`); em cài package rồi chạy lại, run lỗi không dùng làm bằng chứng.
Baseline v0 đạt `case_accuracy=0.65` (13/20), trùng con số v0 ở báo cáo nhóm. Em gán loại lỗi cho 7 case FAIL
(R03, R08, R10, R11, R12, R13, M02), giống nhóm lỗi trong bảng B2 của báo cáo nhóm; nguyên nhân gốc chung là
system prompt của starter khuyến khích đoán, gửi ngay và làm một bước.

**Vòng v1–v7 (CP2).** Mỗi version một giả thuyết, ghi trong `version_log.csv`:

| Version | Thay đổi | case_accuracy |
|---|---|---:|
| v0 | baseline | 0.65 |
| v1 | `system_prompt.md`: bỏ chỉ dẫn xấu, thêm hỏi lại/xác nhận trước khi gửi/gọi nhiều tool/từ chối ngoài phạm vi | 0.85 |
| v2 | `tools.yaml`: description (khi dùng/không dùng), convention args, boundary `send` | 0.85 |
| v3 | `system_prompt.md`: query nguyên văn, send luôn hỏi yes_no, gọi tool song song | 0.85 |
| v4 | `tools.yaml`: thêm 4 tool mới | 1.00 |
| v5 | `system_prompt.md`: rule routing tường minh | 0.95 |
| v6 | `tools.yaml`: viết lại description còn lại | 0.90 |
| v7 | `system_prompt.md`: `clarify` phải đặt `response_type` | 0.85 |

v2 và v3 không tăng metric; v5–v7 không vượt v4 và v7 giảm so với v6 (không sửa được R12, làm R10 và R13 fail).
Các lần chạy có cùng prompt/tool vẫn lệch 0.05–0.15, nên một lần chạy mỗi version chưa đủ để kết luận
mức tăng của v4 là do tool mới. Em ghi nhận điều này thay vì chọn run tốt nhất. Artifact cuối là v7 và
trên bộ base nhóm thấp hơn run v4.

**Tool mới và unit test (CP3).** Thêm 4 tool `hackernews`, `wikipedia`, `github_repo`, `dedupe`
(mỗi tool có `TOOL.md`, đăng ký trong `tools/__init__.py` và `tools.yaml`, trả error dict thay vì raise).
Viết 3 test mỗi tool (happy path, input xấu không gọi mạng, lỗi HTTP) và thay 17 stub bằng test thật; trên nhánh
này `pytest` cho 108 passed, 0 skipped. Ví dụ lỗi chỉ unit test bắt được: `github_repo(repo="../etc/passwd")`
phải trả `ValueError` và không gửi request.
Tool mới của nhóm trên `main` là `filter_sources` (bạn Minh trình bày); 4 tool của em là một nhánh thử riêng
và chưa nằm trong bảng A2 của báo cáo nhóm.

**Eval nhóm, UI và live chat (CP4, CP5).** Viết 10 case `eval_group.json` trên nhánh của em (5 single + 5 multi,
gồm case route tới tool mới); `--suite group` ở v4 và v7 đều 10/10. Làm UI Streamlit và chạy `chat.py` 4 lượt
(hỏi lại thiếu handle, bổ sung, tin AI, đăng Telegram thì agent hỏi xác nhận, không gửi).
Một lỗi live em tìm thấy và chưa sửa: khi lượt trước đã nói về "AI", yêu cầu "Tóm tắt 5 tweet mới nhất" bị hiểu
là chủ đề AI thay vì hỏi lại tài khoản. UI trên `main` là bản khác của nhóm (Research Desk), không phải `app.py` của em.

**Bonus.** Chạy base eval với `qwen2.5:7b-instruct-q4_K_M` (Ollama) trên prompt/tools v4: 0.80, run hợp lệ.
Chỉ có 1 model và 1 vòng nên **chưa đạt** bonus Small Local Model. Chưa gửi Telegram thật.

## 4. Bằng chứng

Link trỏ tới commit `2b39c22da839beca9c392173628475a72b3d2329` của nhánh `doanxuanduybao`
(`https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/<commit>/...`).

| Nội dung | Bằng chứng |
|---|---|
| Các vòng thử nghiệm và hash | [version_log.csv](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/2b39c22da839beca9c392173628475a72b3d2329/starter_v0/artifacts/version_log.csv) |
| Run v0 hợp lệ | [v0_B_base_gemini_20261110T182734036319.json](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/2b39c22da839beca9c392173628475a72b3d2329/starter_v0/runs/v0_B_base_gemini_20261110T182734036319.json) |
| Run v4 base / group | [v4 base](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/2b39c22da839beca9c392173628475a72b3d2329/starter_v0/runs/v4_B_base_gemini_20261110T190743824427.json), [v4 group](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/2b39c22da839beca9c392173628475a72b3d2329/starter_v0/runs/v4_B_group_gemini_20261110T191020600726.json) |
| Run local qwen | [v4-qwen](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/2b39c22da839beca9c392173628475a72b3d2329/starter_v0/runs/v4-qwen_B_base_ollama_20261110T193344154584.json) |
| 4 tool mới | `starter_v0/tools/{hackernews,wikipedia,github_repo,dedupe}/` trên nhánh `doanxuanduybao` |
| Unit test | `starter_v0/tests/test_tools_todo.py` trên nhánh `doanxuanduybao` |
| Transcript live | `starter_v0/transcripts/v4_gemini_20261110T192333079129.transcript.json` trên nhánh `doanxuanduybao` |

Các run v5, v6, v7 và `version_log.csv` đầy đủ nằm ở commit mới nhất của nhánh `doanxuanduybao`. Mọi run dùng làm
bằng chứng có `provider_error_cases == 0` và `measured_cases == total_cases`.

Lệnh em tự chạy trong `starter_v0` trên nhánh `doanxuanduybao`:

| Lệnh | Kết quả |
|---|---|
| `python -m pytest -q` | 108 passed, 0 skipped |
| `python run_eval.py --provider gemini --version v7 --suite base --eval-cases data/eval_base.json` | 0.85, 0 provider error |
| `python run_eval.py --provider gemini --version v7 --suite group --eval-cases data/eval_group.json` | 1.00, 10/10 |

Số test (108) khác con số 122 passed ở báo cáo nhóm vì hai bộ test thuộc hai nhánh khác nhau.

**AI/công cụ đã dùng.** Em dùng Claude Code để viết code, test và nháp báo cáo; em tự kiểm tra bằng cách chạy
`pytest`, `run_eval.py` và đối chiếu metric/hash trong run JSON, không chỉ dựa vào thông báo của AI.

Commit kỹ thuật cá nhân: nhánh `doanxuanduybao`, commit [`2b39c22`](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/commit/2b39c22da839beca9c392173628475a72b3d2329).

## 5. Tự đánh giá

Làm được: baseline hợp lệ, vòng v1–v7 có log và hash, 4 tool mới có test offline (0 skipped), eval nhóm 10/10 trên nhánh
của em, transcript có hỏi lại và xác nhận trước khi gửi. Em biết kết quả base 1.00 của v4 không chứng minh tool mới
là nguyên nhân, vì model biến thiên giữa các lần chạy.

Chưa làm hoặc yếu: v5–v7 không cải thiện; artifact cuối thấp hơn bản tốt nhất; còn lỗi suy chủ đề từ lượt trước;
bonus local model chưa đạt (1 model, 1 vòng); chưa gửi Telegram thật; không có người ngoài nhóm dùng thử UI.
Phần của em chạy trên Gemini nên không so sánh trực tiếp được với run OpenRouter của nhóm.
