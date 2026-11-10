# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: openrouter / openai/gpt-4o-mini

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (chưa sửa) | n/a — baseline gốc của starter | n/a | case_accuracy=0.65, tool_routing=0.75, argument=0.65, multiturn=1.0 | `runs/v0_B_base_openrouter_20261110T173654082508.json` |
| v1 | system_prompt.md | Bỏ chỉ dẫn xấu cố ý của starter (đoán thay vì hỏi, gửi không cần xác nhận, ép 1 bước); thêm rule từ chối câu hỏi ngoài phạm vi | case_accuracy=0.65, tool_routing=0.75, argument=0.65, multiturn=1.0 | case_accuracy=0.8, tool_routing=0.95, argument=0.8, multiturn=0.8333 | `runs/v1_B_base_openrouter_20261110T180546988890.json` |
| v2 | tools.yaml | Mô tả rõ `response_type` của `clarify` (text khi thiếu info / yes_no khi xác nhận hành động), bắt buộc truyền tường minh | case_accuracy=0.8, tool_routing=0.95, argument=0.8, multiturn=0.8333 | case_accuracy=0.85, tool_routing=0.95, argument=0.85, multiturn=0.8333 | `runs/v2_B_base_openrouter_20261110T181930034875.json` |
| v3 | tools.yaml | Convention args cho `lookup`/`social_search`: query chỉ giữ từ khóa cốt lõi (không thêm "news"/"tweet"); phân biệt rõ khi nào dùng tool nào; giữ ngữ cảnh topic/timeframe qua nhiều lượt | case_accuracy=0.85, tool_routing=0.95, argument=0.85, multiturn=0.8333 | case_accuracy=0.95, tool_routing=1.0, argument=0.95, multiturn=1.0 | `runs/v3_B_base_openrouter_20261110T182203917895.json` |
| v4 (thử đầu) | system_prompt.md | Rule: yêu cầu gửi/đăng phải xin xác nhận yes_no trước, kể cả khi thiếu nội dung — mục tiêu fix R12 | case_accuracy=0.95 | case_accuracy=0.9 (R12 PASS nhưng R01/R05 **regression** vì câu lệnh quá rộng, ảnh hưởng cả tool đọc dữ liệu) | `runs/v4_B_base_openrouter_20261110T182956350018.json` |
| v4c (final) | system_prompt.md | Thu hẹp phạm vi rule v4: chỉ áp dụng khi dùng đúng động từ gửi/đăng, không ảnh hưởng tool đọc dữ liệu; thêm ví dụ cụ thể | case_accuracy=0.9 | case_accuracy=0.95 (R12 PASS, không còn regression, nhưng R10 FAIL trở lại — model dao động ở case ranh giới) | `runs/v4c_B_base_openrouter_20261110T183354095364.json` |
| v5 (thí nghiệm bị bác bỏ) | system_prompt.md + tools.yaml (dịch toàn bộ sang tiếng Anh) | Giả thuyết: mô tả tiếng Việt trong `tools.yaml` gây nhiễu/khó hiểu hơn tiếng Anh | case_accuracy=0.95 | case_accuracy=0.9 (**kém hơn v4c**; R12 PASS nhưng R01+R10 FAIL) — **giả thuyết bị bác bỏ**, ngôn ngữ không phải nguyên nhân gốc, đây là dao động/instability của model ở các case ranh giới mơ hồ | `runs/v5_B_base_openrouter_20261110T183624271897.json` — sau thí nghiệm này đã revert `system_prompt.md`/`tools.yaml` về đúng bản v4c (tốt nhất hiện có) |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

> Bảng dưới liệt kê theo version đã phát hiện/khắc phục. Case nào vẫn còn FAIL sau v3 được đánh dấu "CHƯA SỬA — còn tồn đọng".

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_tool (wrong_arg_value) | (v0) `lookup(query="AI news", ...)` | Model tự thêm chữ vào `query` thay vì giữ nguyên từ khóa gốc | Đã sửa ở **v1** (bỏ chỉ dẫn xấu "ép 1 bước, đoán bừa") → PASS từ v1 |
| R08_out_of_scope | out_of_scope (unexpected_tool_call) | (v0) `send(text="Nguyên hàm của x^2 là...")` | Câu hỏi toán ngoài phạm vi, model tự trả lời rồi gọi `send` | Đã sửa ở **v1** (thêm rule từ chối câu hỏi ngoài phạm vi trong system prompt) → PASS từ v1 |
| R10_missing_handle | missing_info (missing_tool_call → wrong_arg_value) | (v0) `timeline(screenname="sama")` bịa; (v1) `clarify` nhưng thiếu `response_type` | User không nói rõ tài khoản, model bịa (v0) rồi gọi đúng `clarify` nhưng sai args (v1) | Đã sửa ở **v2** (mô tả rõ `response_type` trong `tools.yaml`, bắt buộc truyền tường minh) → PASS từ v2 |
| R11_missing_url | missing_info (tương tự R10) | (v0) `fetch(url=bịa)`; (v1) `clarify` thiếu `response_type` | User không đưa URL | Đã sửa ở **v2**, cùng nguyên nhân R10 → PASS từ v2 |
| **R12_confirm_before_send** | **wrong_boundary** | (v3) `clarify(question="...nội dung bản tin...", response_type="text")` | Model nhầm giữa "thiếu nội dung" và "cần xin xác nhận hành động gửi" — luôn trả lời `response_type="text"` thay vì `"yes_no"` | **Đã sửa ở v4c** (`system_prompt.md`: rule rõ ràng, thu hẹp đúng phạm vi "dùng đúng động từ gửi/đăng" + ví dụ cụ thể) → PASS từ v4c. Lưu ý: khi thử v5 (dịch sang tiếng Anh) R12 vẫn PASS nhưng R10 FAIL lại — cho thấy đây là vùng quyết định ranh giới mà model còn dao động nhẹ giữa các lần chạy khác nhau, không phải do 1 câu prompt riêng lẻ gây ra hoàn toàn |
| R13_parallel_web_and_tweets | wrong_tool (wrong_arg_value) | (v0/v2) tự thêm chữ vào `query`, thiếu `topic="news"` | Chọn đúng 2 tool nhưng sai args | Đã sửa ở **v3** (convention args rõ ràng cho `lookup`/`social_search`) → PASS từ v3 |
| R14_out_of_scope_coding | out_of_scope (unexpected_tool_call) | (v0) `send(text="Dưới đây là hàm Python...")` | Yêu cầu code ngoài phạm vi, model trả lời rồi gọi `send` | Đã sửa ở **v1**, cùng nguyên nhân R08 → PASS từ v1 |
| M02_carryover_timeframe | wrong_arg_value | (v1/v2) `social_search(query="robotics",...)` thay vì `lookup` | Hội thoại 3 lượt vẫn đang nói về tin tức, model chuyển nhầm sang `social_search` | Đã sửa ở **v3** (carry-over ngữ cảnh + ranh giới `lookup` vs `social_search`) → PASS từ v3 |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
