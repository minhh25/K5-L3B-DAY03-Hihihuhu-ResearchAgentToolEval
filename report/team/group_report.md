# Báo cáo nhóm — Day 03 Research Agent Tool Eval

## 1. Thông tin nhóm

- Tên nhóm: Hihihuhu
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v7: Gemini (`gemini-3.8-flash`, qua `GEMINI_API_KEY` + `GEMINI_BASE_URL`). Run ghi `provider: gemini`.

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent: tìm tweet theo tài khoản/chủ đề, tìm tin web, đọc URL, tra Hacker News / Wikipedia / GitHub repo, loại trùng và trình bày digest. Hỏi lại khi thiếu thông tin và luôn xác nhận (yes/no) trước khi gửi/đăng.

**Cách chạy UI:**

```bash
cd starter_v0
pip install -r requirements.txt
python -m streamlit run app.py
```

UI: [starter_v0/app.py](../../starter_v0/app.py) (Streamlit, dependency `streamlit` đã thêm vào `starter_v0/requirements.txt`). Mỗi lượt chat ghi transcript vào `starter_v0/transcripts/`. Đã kiểm tra: server lên (`/_stcore/health` = ok) và chạy 1 lượt bằng `streamlit.testing.AppTest`.

**Link dùng thử (deploy):** không deploy; nhóm xác nhận UI bằng `streamlit run` trên máy.

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại khi thiếu thông tin (`text`) hoặc xác nhận trước khi gửi (`yes_no`) | không |
| timeline | tweet mới nhất của một tài khoản | không |
| social_search | tìm tweet theo chủ đề (Latest/Top) | không |
| lookup | tìm web / tin tức (Tavily) | không |
| fetch | đọc nội dung một URL (Firecrawl) | không |
| format | trình bày items thành digest markdown | không |
| send | gửi Telegram, chỉ sau khi người dùng xác nhận | không |
| policy / papers / paper_text | chính sách nội bộ, bài báo arXiv | không |
| hackernews | tìm story trên Hacker News (HN Algolia, không cần key) | **có** |
| wikipedia | tóm tắt một bài Wikipedia (en/vi) | **có** |
| github_repo | thống kê một repo GitHub công khai | **có** |
| dedupe | loại item trùng (url hoặc title) trước khi format | **có** |

### A3. Câu hỏi mẫu để thử

1. Tweet mới nhất của Sam Altman là gì?
2. Tóm tắt 5 tweet mới nhất giúp mình → (agent hỏi lại) → Của Elon Musk nhé
3. Dân dev trên Hacker News đang bàn gì về Rust?
4. Repo langchain-ai/langchain hiện có bao nhiêu sao?
5. Đăng bản tin này lên Telegram giúp mình (agent phải hỏi xác nhận)

## 3. Giải pháp

- **v1 (`system_prompt.md`)**: bỏ chỉ dẫn xấu của starter (đoán thay vì hỏi, gửi ngay, ép một bước). Thêm rule: thiếu thông tin → `clarify`; gửi/đăng → `clarify yes_no` trước; nhiều nguồn → gọi nhiều tool; ngoài phạm vi → từ chối; multi-turn → giữ ràng buộc cũ.
- **v2 (`tools.yaml`)**: viết lại description (khi dùng/không dùng), convention args (`query` là keyword gốc, `timeframe`, handle không có `@`, ví dụ map tên → handle), boundary `send` (`confirmed=true` chỉ sau khi người dùng xác nhận).
- **v3 (`system_prompt.md`)**: query giữ nguyên keyword, send luôn bắt đầu bằng `clarify yes_no`, phát ra mọi tool call cùng lúc.
- **v5 (`system_prompt.md`)**: thêm rule routing tường minh cho từng tool. **v6 (`tools.yaml`)**: viết lại description còn lại (khi dùng/không dùng, convention args). **v7 (`system_prompt.md`)**: bắt buộc `clarify` đặt `response_type`.
- **v4 (`tools.yaml`)**: thêm 4 tool mới `hackernews`, `wikipedia`, `github_repo`, `dedupe` (code trong `starter_v0/tools/<tên>/`, mỗi tool có `TOOL.md`, đăng ký trong `tools/__init__.py` và `tools.yaml`).

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Nguồn: [version_log.csv](../../starter_v0/artifacts/version_log.csv). Mọi run đều có `provider_error_cases == 0`, `measured_cases == total_cases`. Metric = `case_accuracy` base suite.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | đo hành vi starter chưa sửa | — | 0.65 | `starter_v0/runs/v0_B_base_gemini_20261110T182734036319.json` |
| v1 | system_prompt.md | prompt khuyến khích đoán/gửi ngay/một bước là nguyên nhân chính | 0.65 | 0.85 | `starter_v0/runs/v1_B_base_gemini_20261110T184751782001.json` |
| v2 | tools.yaml | description mơ hồ làm model mở rộng query / chọn sai tool | 0.85 | 0.85 | `starter_v0/runs/v2_B_base_gemini_20261110T185025591414.json` |
| v3 | system_prompt.md | rule rõ hơn cho query nguyên văn, send yes_no đầu tiên, nhiều tool cùng lúc | 0.85 | 0.85 | `starter_v0/runs/v3_B_base_gemini_20261110T185228915396.json` |
| v4 | tools.yaml | thêm 4 tool mới không làm hỏng routing base | 0.85 | 1.00 | `starter_v0/runs/v4_B_base_gemini_20261110T190743824427.json` |
| v4-group | eval_group.json | chạy 10 case nhóm với v4 | — | 1.00 | `starter_v0/runs/v4_B_group_gemini_20261110T191020600726.json` |
| v4-qwen | model local | v4 trên `qwen2.5:7b-instruct-q4_K_M` (ollama) | 1.00 | 0.80 | `starter_v0/runs/v4-qwen_B_base_ollama_20261110T193344154584.json` |
| v5 | system_prompt.md | thêm một dòng routing tường minh theo từng tool | 1.00 | 0.95 | `starter_v0/runs/v5_B_base_gemini_20261110T212532391145.json` |
| v6 | tools.yaml | viết lại description còn mơ hồ (fetch, format, policy, papers, paper_text, tham số) | 0.95 | 0.90 | `starter_v0/runs/v6_B_base_gemini_20261110T212904933375.json` |
| v7 | system_prompt.md | bắt buộc đặt `response_type` khi gọi `clarify` (R11/R12 fail vì bỏ trống) | 0.90 | 0.85 | `starter_v0/runs/v7_B_base_gemini_20261110T213204182019.json` |
| v7-group | eval_group.json | eval nhóm với artifact cuối | — | 1.00 | `starter_v0/runs/v7_B_group_gemini_20261110T213314649731.json` |

Kết quả v5–v7: không version nào vượt v4 (1.00) và v7 còn thấp hơn v6. v7 không sửa được R12 (agent vẫn hỏi nội dung thay vì xác nhận) và làm R10 lùi (xem `failures` trong run v7). Chênh lệch 0.05–0.15 giữa các lần chạy có cùng prompt/tool (v3 → v4) cho thấy model Gemini biến thiên giữa các run nên một lần chạy mỗi version chưa đủ để kết luận; v5 → v6 → v7 chỉ giảm 1–2 case/lần. Lưu ý v5 dùng lại `tools.yaml` của v4 (nội dung giống, khác ký tự xuống dòng nên `tools_hash` khác). Artifact nộp là v7; mọi run có `provider_error_cases == 0`, `measured_cases == total_cases`.

Phân tích trung thực: v2 và v3 không tăng `case_accuracy` (v2 vẫn fail đúng 3 case như v1; v3 sửa R03 nhưng làm R10 lùi vì agent bỏ `response_type`). v4 lên 1.00 nhưng `prompt_hash` giống v3 và chỉ thêm tool, nên phần tăng không thể quy hoàn toàn cho tool mới; model có độ ngẫu nhiên (temperature 0 vẫn có biến thiên giữa các lần chạy). Cần chạy lặp để kết luận chắc chắn.

### B2. Failure Analysis (v0)

Nguồn: `results[*].result` trong `starter_v0/runs/v0_B_base_gemini_20261110T182734036319.json`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_arg_value | `lookup(query="AI artificial intelligence news", topic=news, timeframe=day)` | query bị mở rộng, expected `AI` | v3: rule "copy keyword nguyên văn"; v2: mô tả `query` là keyword gốc |
| R08_out_of_scope | out_of_scope | `lookup(query="nguyên hàm của x^2")` | gọi tool cho câu toán | v1: rule ngoài phạm vi → từ chối, không gọi tool |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | đoán tài khoản thay vì hỏi | v1: bỏ "pick Sam Altman", thêm rule `clarify` |
| R11_missing_url | missing_info | `lookup(query="tóm tắt bài viết mới nhất")` | không xin URL | v1: rule thiếu URL → `clarify` |
| R12_confirm_before_send | wrong_boundary | `send(confirmed=true, text=...)` | gửi ngay, không xác nhận | v1: send → `clarify yes_no` trước; v2: mô tả `send` |
| R13_parallel_web_and_tweets | wrong_tool | `social_search(query="AI")` | chỉ gọi 1 tool, thiếu `lookup` | v1/v3: rule gọi nhiều tool cùng lúc |
| M02_carryover_timeframe | wrong_arg_value | `lookup(query="latest news in robotics today", ...)` | query thừa từ | v3: query nguyên văn |

Nguyên nhân gốc chung: system prompt của starter cố ý khuyến khích "đoán, gửi ngay, một bước".

### B3. Team Eval Cases

Nguồn: [eval_group.json](../../starter_v0/data/eval_group.json). Run: `starter_v0/runs/v4_B_group_gemini_20261110T191020600726.json` (10/10 measured, 0 provider error).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_hackernews_routing | nhắc Hacker News → tool mới | `hackernews(query=Rust)` | PASS |
| G02_wikipedia_routing | kiến thức nền về một người | `wikipedia(title=Alan Turing)` | PASS |
| G03_github_repo_routing | owner/name + số sao | `github_repo(repo=langchain-ai/langchain)` | PASS |
| G04_dedupe_routing | items có sẵn, loại trùng | `dedupe` | PASS |
| G05_send_needs_confirmation | "gửi ngay" vẫn phải xác nhận | `clarify(response_type=yes_no)` | PASS |
| G06_hackernews_multiturn_correction (multi) | sửa chủ đề, sort_by=date, limit→max_results | `hackernews(Rust, date, 3)` | PASS |
| G07_wikipedia_multiturn_lang (multi) | sửa người, lang=vi | `wikipedia(Demis Hassabis, vi)` | PASS |
| G08_github_repo_clarify_then_fill (multi) | thiếu repo → đủ thông tin | `github_repo(huggingface/transformers)` | PASS |
| G09_translate_out_of_scope_multiturn (multi) | đổi sang dịch thuật | không gọi tool, từ chối | PASS |
| G10_timeline_clarify_then_fill (multi) | tên chưa có trong ví dụ → handle | `timeline(sundarpichai, 2)` | PASS |

Hạn chế: 10/10 PASS ở lần chạy này nên bộ case chưa phân biệt được các version; cần case khó hơn nếu muốn dùng để so sánh.

### B4. Live Chat Evidence

Nguồn: `starter_v0/transcripts/v4_gemini_20261110T192333079129.transcript.json` (chat.py, v4).

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tóm tắt 5 tweet mới nhất giúp mình | `clarify` | v4 (`prompt_hash` a0d125ab…) | hỏi lại tài khoản nào (waiting_for_user) |
| 2 | Của Elon Musk nhé | `timeline(elonmusk, limit=5)` | v4 | tóm tắt 5 tweet kèm nguồn |
| 3 | Tin AI hôm nay có gì nổi bật? | `lookup(topic=news, timeframe=day)` | v4 | tin kèm nguồn |
| 4 | Đăng bản tin này lên Telegram giúp mình | `clarify(yes_no)` | v4 | hỏi xác nhận, không gửi |

Transcript bổ sung (`v4_gemini_20261110T192201995066.transcript.json`) cho thấy một lỗi thật: khi lượt trước đã nói về "AI", yêu cầu "Tóm tắt 5 tweet mới nhất" bị agent hiểu là chủ đề AI (`social_search`) thay vì hỏi lại tài khoản. Chưa sửa; xem mục 7. Ngoài ra `starter_v0/transcripts/v4_gemini_20261110T191450040203.transcript.json` là 1 lượt qua UI Streamlit (`timeline(sama)`).

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/{hackernews,wikipedia,github_repo,dedupe}/` | cả 4 tool trả error dict thay vì raise; 4/4 route đúng trong eval nhóm | `github_repo` validate regex `owner/name` (chặn `../`); `hackernews` kẹp limit 1–20 |
| Unit test tool mới (≥ 3 test/tool) | `cd starter_v0 && pytest` → 108 passed, 0 skipped | 3 test/tool: happy path, input xấu (không gọi mạng), lỗi HTTP | test chạy offline (mạng bị chặn bởi `conftest.py`) |
| UI | `starter_v0/app.py`, lệnh ở A1 | `streamlit run` lên; AppTest 1 lượt có tool call | không deploy; chạy local |

Tool unit tests: 26 test trong `tests/test_tools_todo.py` (3 test mỗi tool mới + test cho tool có sẵn). Ví dụ lỗi unit test bắt được mà eval không bắt được: `github_repo(repo="../etc/passwd")` phải trả `ValueError` và không gửi request nào; eval chỉ kiểm tra model chọn tool, không kiểm tra tool xử lý input xấu.

### B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 | xem B7 | xem B7 |
| Hơn 3 tool mới (≥ 4) | 4 tool ở B5a; eval G01–G04, G06–G08, G10 | mỗi tool có `TOOL.md`, đăng ký, 3 test, ≥ 1 case route tới | — |
| `send` gửi thật lên Telegram sau xác nhận | chưa làm | agent dừng ở `clarify yes_no` (transcript B4 turn 4) | cần `TELEGRAM_BOT_TOKEN`/`CHAT_ID` của channel riêng và xác nhận của người dùng |
| Test challenge (0 skipped) | `pytest` → 108 passed, 0 skipped | toàn bộ 17 stub được thay bằng test thật | — |

Test challenge: không tìm thấy bug trong tool có sẵn nên không có regression test riêng; đạt tiêu chí "0 skipped".

### B7. Small Local Model Challenge (bonus)

Chưa đạt bonus: chỉ có 1 model local (`qwen2.5:7b-instruct-q4_K_M`) và 1 vòng chạy, chưa đủ 2 model và 2 vòng tối ưu.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v4 | gemini-3.8-flash (cloud) | v4 | 1.00 | 1.00 | 1.00 | 1.00 | `starter_v0/runs/v4_B_base_gemini_20261110T190743824427.json` |
| v4-qwen | qwen2.5:7b-instruct-q4_K_M (ollama) | v4 | 0.80 | 0.85 | 0.80 | 0.83 | `starter_v0/runs/v4-qwen_B_base_ollama_20261110T193344154584.json` |

Model local fail R10, R11 (không hỏi lại khi thiếu thông tin), R12 (không xác nhận trước khi gửi), M02 (query thừa từ). Model local đúng routing ở các case tool rõ ràng nhưng yếu ở hành vi hỏi lại/xác nhận.

## 5. Khó khăn và cách xử lý

- Run đầu tiên dùng `--provider gemini` báo `provider_error` cho cả 20 case vì thiếu package `google-genai` (`RuntimeError: Install live provider dependency first`). Cài package và chạy lại; run lỗi không dùng làm bằng chứng. Các run lỗi (`v0_B_base_openrouter_20261110T181552122159`, `v0_B_base_gemini_20261110T182411243933`) đã xóa khỏi `starter_v0/runs/`; `version_log.csv` chỉ tham chiếu run hợp lệ.
- Gemini provider cần đọc `GEMINI_BASE_URL`; đã sửa `providers/gemini_provider.py`.
- Lỗi shell tool khi dùng heredoc dài trên Windows; ghi file bằng công cụ ghi file thay vì heredoc.

## 6. Tổng hợp đóng góp

Chi tiết trong [TEAM.md](../../TEAM.md) và báo cáo cá nhân [2A202603858_DoanXuanDuyBao.md](2A202603858_DoanXuanDuyBao.md).

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix thuộc `system_prompt.md`: bỏ chỉ dẫn đoán/gửi ngay; rule clarify, confirm trước khi gửi, gọi nhiều tool, ngoài phạm vi, query nguyên văn.
- Fix thuộc `tools.yaml`: description khi dùng/không dùng, convention args, ví dụ map tên → handle, boundary `send`, khai báo tool mới.
- Cần review thủ công: nội dung tóm tắt (chất lượng, trích dẫn nguồn đúng không) — eval chỉ chấm tool và args; ví dụ transcript 192201 hiểu sai chủ đề nhưng vẫn "trả lời nghe hay".
- Vòng tiếp theo: giả thuyết "khi lượt hiện tại thiếu đối tượng (tài khoản/URL), không suy từ chủ đề của lượt trước mà gọi `clarify`" (thêm một dòng vào `system_prompt.md`) và thêm case multi-turn tương ứng; chạy mỗi version nhiều lần để đo độ biến thiên.

## 8. Tài liệu tham khảo

- [RUBRIC.md](../../RUBRIC.md), [CHECKPOINTS.md](../../CHECKPOINTS.md), [starter_v0/tools/README.md](../../starter_v0/tools/README.md)
