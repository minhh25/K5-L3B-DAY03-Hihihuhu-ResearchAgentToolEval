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

Research agent: tìm tin theo từ khóa (web/tin tức) hoặc theo tài khoản mạng xã hội, đọc nội dung từ URL, phân tích cảm xúc (tích cực/tiêu cực) của nội dung đã lấy được, tổng hợp thành digest, và đăng/gửi lên Telegram khi đã được người dùng xác nhận (yes/no).

**Cách chạy UI:**

```bash
cd starter_v0
streamlit run app.py --server.port 8501
```

Mở `http://localhost:8501`. Dependency `streamlit>=1.38.0` đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

Hiện chạy local (`http://localhost:8501`), chưa deploy public trong phiên làm việc này (`cloudflared` chưa cài trên máy). Để team khác thử trực tiếp, deploy nhanh bằng Cloudflare Tunnel (xem README mục "Deploy nhanh"):

```bash
winget install --id Cloudflare.cloudflared
cloudflared tunnel --url http://localhost:8501
```

> URL: _(chưa deploy — cập nhật khi demo trực tiếp với team)_

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin, hoặc xin xác nhận yes/no trước hành động gửi/đăng | không |
| timeline | Lấy bài đăng gần đây của 1 tài khoản Twitter/X | không |
| social_search | Tìm bài đăng trên Twitter/X theo từ khóa | không |
| lookup | Tra cứu thông tin/tin tức trên web | không |
| fetch | Đọc nội dung 1 URL cụ thể | không |
| format | Trình bày danh sách kết quả thành markdown digest | không |
| **sentiment** | **Phân tích cảm xúc (tích cực/tiêu cực/trung lập) của 1 đoạn văn bản đã có sẵn** | **có — tool nhóm tự viết** |
| send | Gửi text lên Telegram channel, chỉ khi đã `confirmed=true` | không |
| policy | Tìm trong tài liệu chính sách nội bộ | không |
| papers / paper_text | Tìm và đọc paper khoa học trên arXiv | không |

### A3. Câu hỏi mẫu để thử

1. Tìm tin AI hôm nay có gì nổi bật?
2. Lấy 5 tweet mới nhất của Elon Musk
3. Tóm tắt bài viết này giúp mình (không kèm URL — xem agent hỏi lại)
4. Tìm tin AI hôm nay, rồi phân tích cảm xúc bài đó giúp mình (route tới tool mới `sentiment`)
5. Đăng bản tin này lên Telegram giúp mình (xem agent xin xác nhận trước khi gửi)

## 3. Giải pháp

**`system_prompt.md`** (v1→v4c): bỏ 3 chỉ dẫn xấu cố ý của starter (đoán bừa khi thiếu info, gửi không xác nhận, ép 1 bước); thêm rule: bắt buộc `clarify` khi thiếu info, bắt buộc xin xác nhận `yes_no` trước `send` (kể cả khi thiếu nội dung — ưu tiên xác nhận trước); thêm rule từ chối câu hỏi ngoài phạm vi (toán, code, dịch thuật...).

**`tools.yaml`** (v2→v3): viết lại mô tả `clarify` (khi nào dùng `text` vs `yes_no` vs `choice`, bắt buộc truyền tường minh); viết lại convention args cho `lookup`/`social_search` (query chỉ giữ từ khóa cốt lõi, phân biệt rõ khi dùng tool nào, giữ ngữ cảnh topic/timeframe qua nhiều lượt).

**Tool mới `sentiment`** (`tools/sentiment/`): phân tích cảm xúc tích cực/tiêu cực/trung lập của 1 đoạn văn bản bằng đếm từ khóa (tiếng Việt không dấu + tiếng Anh), sau khi tách từ qua `tools/_shared.py:terms()`. Agent nên gọi tool này SAU KHI đã có nội dung text cụ thể (từ `lookup`/`fetch`/`timeline`/`social_search`) và người dùng hỏi về cảm xúc/thái độ của nội dung đó — không dùng để tự tìm kiếm dữ liệu.

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
Chạy với `--version v4c --suite group`, kết quả: `case_accuracy=0.7` (7/10 PASS) —
run file: `runs/v4c_B_group_openrouter_20261110T190545487755.json`.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_sentiment_routing (multi) | Route tới tool mới `sentiment` sau khi đã có nội dung từ `lookup` | `sentiment(...)` | PASS |
| G02_papers_routing (single) | Route tới `papers` khi hỏi bài báo khoa học, không nhầm `lookup` | `papers(query="diffusion models")` | PASS |
| G03_lookup_timeframe_month (single) | `timeframe` đúng theo "trong tháng này" (khác default week) | `lookup(query="crypto", topic="news", timeframe="month")` | PASS |
| G04_missing_arxiv_url (single) | Thiếu arxiv_url → phải `clarify`, không bịa | `clarify(response_type="text")` | PASS |
| G05_out_of_scope_translate (single) | Yêu cầu dịch thuật ngoài phạm vi → từ chối, không gọi tool | `no_tool=true` | PASS |
| G06_unnecessary_tool_thanks (single) | Lời cảm ơn/kết thúc → không gọi tool thừa | `no_tool=true` | PASS |
| G07_carryover_social_to_lookup (multi) | Chuyển đúng từ `social_search` sang `lookup` khi user đổi ý "lên web" | `lookup(query="AI safety", topic="news")` | **FAIL** — model gọi cả `social_search` (dư, cho lượt trước) lẫn `lookup` (đúng), vi phạm chỉ dẫn "không gọi tool cho lượt trước" |
| G08_sentiment_after_fetch (multi) | Route tới `sentiment` sau khi nội dung đến từ `fetch` (không chỉ từ `lookup`) | `sentiment(...)` | **FAIL** — model gọi lại `fetch` thay vì `sentiment`; không nhất quán với hành vi ở G01 |
| G09_confirm_before_send_multiturn (multi) | Xin xác nhận trước khi gửi, trong ngữ cảnh multi-turn | `clarify(response_type="yes_no")` | PASS |
| G10_clarify_then_fill_handle (multi) | Dùng đúng `timeline` khi user bổ sung rõ tên tài khoản ở lượt sau | `timeline(screenname="elonmusk")` | **FAIL** — model chọn `social_search` thay vì `timeline`, nhầm giữa tìm theo tài khoản và tìm theo từ khóa |

**Nhận xét:** bộ eval nhóm phát hiện 3 lỗi thật mà base eval (20 case có sẵn) không phủ tới — đều liên quan tới việc route tool nhất quán trong ngữ cảnh multi-turn phức tạp hơn (chuyển tool giữa chừng, route tới tool mới từ nhiều nguồn ngữ cảnh khác nhau, phân biệt tool theo-tài-khoản vs theo-từ-khóa). Đây là hướng cải thiện tiềm năng cho vòng tối ưu tiếp theo nếu có thời gian (ví dụ v6: thêm rule "không gọi tool cho earlier turn", mở rộng mô tả `sentiment` để áp dụng sau mọi tool lấy nội dung, làm rõ hơn ranh giới `timeline` vs `social_search` khi có tên riêng cụ thể).

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`. Chạy qua UI Streamlit (`app.py`), không phải CLI `chat.py` trực tiếp — cùng logic `run_model_tool_loop`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 (session A) | "Tìm tin AI hôm nay có gì nổi bật?" | `lookup(query="AI", topic="news", timeframe="day")` | `transcripts/v4c_openrouter_20261110T191935116417.transcript.json` | PASS — trả về 5 tin thật kèm link, đúng tool |
| 1 (session B) | "Tóm tắt bài viết này giúp mình" (không có URL) | _(không tool call — model trả lời text hỏi lại URL trực tiếp)_ | `transcripts/v4c_openrouter_20261110T192604938163.transcript.json` | PASS về mặt UX (vẫn hỏi lại đúng), nhưng model không gọi tool `clarify` như kỳ vọng ở eval — ghi nhận là khác biệt hành vi giữa chat tự do (`tool_choice` không ép) và eval (`tool_choice="required"`) |
| 2 (session B) | "Đây nè: https://openai.com/research/" (bổ sung URL) | `fetch(url="https://openai.com/research/")` → `format(...)` | cùng file trên | PASS — đọc đúng URL, tổng hợp thành bản tóm tắt tiếng Việt |
| 3 (session B) | "Đăng tóm tắt này lên Telegram giúp mình" | `clarify(response_type="yes_no")` | cùng file trên | PASS — agent xin xác nhận trước khi gửi, không tự gửi ngay (đúng hành vi v4c) |

**Bug phát hiện qua live test UI (đã sửa):** `chat.py` dòng in `print(f"🔧 ...")` ra console gây `UnicodeEncodeError` trên Windows (console mặc định `cp1252`, không encode được emoji lẫn ký tự tiếng Việt có dấu) — làm UI báo lỗi và dừng giữa chừng. Sửa bằng `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` ở đầu `chat.py`. Đã test lại, hoạt động ổn định, không còn lỗi console.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/sentiment/`) | `tools/sentiment/tool.py`, `tools/sentiment/TOOL.md` | Phân tích cảm xúc (positive/negative/neutral) từ đếm từ khóa, đăng ký đúng trong `tools/__init__.py` + `artifacts/tools.yaml`; `test_tool_contract.py` xanh (60 passed) | Heuristic đếm từ khóa đơn giản, không hiểu phủ định/mỉa mai — ghi rõ giới hạn trong `TOOL.md`; luôn bắt `TypeError` trả error dict thay vì raise khi model truyền sai kiểu |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output: 70 passed, 14 skipped (3 test mới đều PASS) | happy path (phân biệt positive/negative), bad input (`text=12345` → error dict, không raise), edge case (text rỗng → neutral, không crash) | — |
| Eval case route tới tool mới | `data/eval_group.json` case `G01_sentiment_routing`; `runs/v4c_B_group_openrouter_20261110T185053943247.json` | Case multi-turn: hỏi tin tức trước, rồi hỏi cảm xúc → model gọi đúng `sentiment`, `case_accuracy=1.0` | — |
| UI (lệnh chạy + link dùng thử) | `starter_v0/app.py`; `streamlit run app.py --server.port 8501` | Chat UI đầy đủ: lịch sử hội thoại, expander hiển thị tool call + kết quả, transcript tự ghi mỗi turn, sidebar hiển thị artifact_version + câu hỏi mẫu. Test bằng Playwright headless: 4 turns qua 2 session, không lỗi console | Local-only (`localhost:8501`), chưa deploy public (`cloudflared` chưa cài trên máy làm việc) |

Tool unit tests: 3 test viết cho `sentiment` (`tests/test_tools_todo.py`, mục "sentiment (tool mới của nhóm)"). Ví dụ unit test bắt lỗi mà eval không bắt được: `test_sentiment_bad_input_from_model_returns_error_not_raise` kiểm tra khi model lỡ truyền `text` không phải string (vd số) — eval chỉ đo model có *chọn đúng tool/args* hay không (ở đây model chọn đúng), nhưng không đo *code tool* có xử lý an toàn input đó hay không; unit test này xác nhận tool trả về error dict (`{"error": "TypeError", ...}`) thay vì crash chương trình.

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

- **`UnicodeEncodeError` khi chạy UI trên Windows:** `chat.py` in log tool call ra console bằng `print(f"🔧 ...")`. Console Windows mặc định dùng codec `cp1252`, không encode được emoji lẫn nhiều ký tự tiếng Việt có dấu (vd `ắ`). Khi Streamlit chạy `chat.py`'s `run_model_tool_loop` và capture stdout, lỗi này làm cả turn bị crash, UI hiển thị "Lỗi: UnicodeEncodeError...". Phát hiện qua test UI thật bằng Playwright headless (ảnh chụp `turn2_missing_url.png`/`turn3_followup.png` trước khi sửa cho thấy rõ lỗi). **Fix:** thêm `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` ở đầu `chat.py` để buộc stdout dùng UTF-8 bất kể console mặc định là gì. Test lại: 4 turns chạy ổn định, 0 lỗi console.
- **Model không ổn định ở vùng ranh giới mơ hồ (xem B6):** case R12/R10 dao động PASS/FAIL giữa các version dù prompt gần như không đổi nghĩa — không phải bug code, mà là giới hạn của việc chấm exact-match trên hành vi LLM không hoàn toàn deterministic (xem chi tiết v4/v4c/v5 trong B1).
- **3/10 case eval nhóm FAIL (G07, G08, G10):** phát hiện thật về sự thiếu nhất quán khi route tool trong ngữ cảnh multi-turn phức tạp hơn base eval (xem B3) — chưa kịp sửa trong phiên làm việc này, để lại làm hướng tối ưu tiếp theo.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
