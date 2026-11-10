# Vũ Tiến Hùng - 2A202603882

### Phần việc phụ trách

- Setup môi trường chạy (venv, dependency, `.env`, preflight) — CP1
- Chạy baseline v0 và phân tích lỗi (failure analysis) — CP1
- Tối ưu `system_prompt.md` và `tools.yaml` qua các vòng v1 → v4c — CP2

### Đóng góp cụ thể

- Cấu hình đủ 4 API key bắt buộc (OpenRouter, Tavily, Firecrawl, RapidAPI) + bonus Telegram, xác minh từng key bằng lệnh test thật.
- Chạy base eval v0 (baseline chưa sửa gì), `case_accuracy=0.65`, gán loại lỗi cho 7/20 case FAIL (wrong_tool, out_of_scope, missing_info, wrong_boundary).
- v1: bỏ 3 chỉ dẫn xấu cố ý trong `system_prompt.md` (đoán bừa khi thiếu info, gửi không xác nhận, ép 1 bước) → `case_accuracy` 0.65 → 0.8.
- v2: viết lại mô tả tool `clarify` trong `tools.yaml`, làm rõ convention `response_type` (text/yes_no/choice) → `case_accuracy` 0.8 → 0.85.
- v3: viết lại convention args cho `lookup`/`social_search` (giữ `query` chỉ chứa từ khóa cốt lõi, phân biệt rõ khi nào dùng tool nào, giữ ngữ cảnh qua nhiều lượt hội thoại) → `case_accuracy` 0.85 → 0.95, `tool_routing_accuracy` đạt 1.0.
- v4/v4c: thử fix case R12 còn lại (nhầm giữa "thiếu nội dung" và "cần xác nhận gửi"); v4 đầu tiên gây regression (R01/R05), v4c thu hẹp phạm vi rule mới đúng và đạt `case_accuracy=0.95` không regression.
- v5: thử giả thuyết dịch toàn bộ prompt/tools sang tiếng Anh để ổn định hơn — kết quả `case_accuracy=0.9` (kém hơn v4c), giả thuyết bị bác bỏ bằng bằng chứng thật, đã revert về bản v4c.
- Ghi đầy đủ version_log.csv (v0–v5, bao gồm cả thử nghiệm thất bại) và bảng B1/B2 trong `group_report.md`.

### Bằng chứng

- `starter_v0/runs/v0_B_base_openrouter_20261110T173654082508.json` đến `v5_B_base_openrouter_20261110T183624271897.json`
- `starter_v0/artifacts/version_log.csv` (dòng v0–v5)
- `report/team/group_report.md` mục B1 (Version Evidence) và B2 (Failure Analysis)
