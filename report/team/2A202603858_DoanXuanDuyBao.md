# Báo cáo cá nhân — Đoàn Xuân Duy Bảo-2A202603858

## 1. Thông tin thành viên

- Họ tên: Đoàn Xuân Duy Bảo
- MSSV: 2A202603858
- Email: doanxuanduybao96@gmail.com

## 2. Phần việc phụ trách

Toàn bộ pipeline: baseline v0, tối ưu v1–v7, tool mới, unit test, eval nhóm, UI, transcript, báo cáo.

## 3. Đóng góp cụ thể

- Sửa provider Gemini để đọc `GEMINI_BASE_URL`; cài `google-genai` để hết `provider_error`.
- Chạy v0 (0.65), sau đó mỗi version một giả thuyết: v1 prompt (0.85), v2 tool description (0.85), v3 prompt (0.85), v4 thêm tool (1.00); ghi `version_log.csv`.
- Viết 4 tool: `hackernews`, `wikipedia`, `github_repo`, `dedupe`; thay 17 stub test bằng test thật, thêm test cho tool mới (`pytest`: 108 passed, 0 skipped).
- Viết 10 case `data/eval_group.json` (5 single + 5 multi), chạy `--suite group` (10/10).
- Viết UI Streamlit `app.py`; chạy `chat.py` 4 lượt (hỏi lại → bổ sung → xác nhận trước khi đăng).

## 4. Bằng chứng

- File/commit/PR: nhánh `doanxuanduybao`; `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/*.json`, `starter_v0/transcripts/*.json`, `starter_v0/tests/test_tools_todo.py`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: dùng Claude Code để viết code/báo cáo; kiểm tra bằng cách chạy `pytest`, `run_eval.py` và đối chiếu metric trong run JSON.

## 5. Tự đánh giá

Đạt: base 1.00, group 10/10, 4 tool mới, test 0 skipped. Hạn chế: v2/v3 không tăng metric; v4 tăng, v5–v7 không vượt v4 và model biến thiên giữa các lần chạy nên không chắc do tool mới (model có biến thiên); live chat còn một lỗi suy chủ đề từ lượt trước thay vì hỏi lại; chưa làm gửi Telegram thật.
