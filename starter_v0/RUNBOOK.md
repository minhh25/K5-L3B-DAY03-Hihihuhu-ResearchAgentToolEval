# Chạy và kiểm chứng Day03

Chạy từ root repo bằng virtualenv đã có (không cần tạo lại):

```bash
source .venv/bin/activate
cd starter_v0
python -m pip install -r requirements.txt
```

API key đặt trong `.env` hoặc biến môi trường. Không đưa key vào lệnh hoặc báo cáo.
Nếu dùng file ngoài repo, đặt biến `DAY03_ENV_FILE` tới đường dẫn file đó.
Đối với key đã cấu hình, không cần sửa lại `.env`.

Hiện đã hoàn tất run hợp lệ v0–v3 và group sau khi người dùng cập nhật `.env`:
base 65% → 70% → 80% (v2 resume) → 75%; group v3 90%.
[results_summary.json](analysis/results_summary.json) trỏ tới các run thật.
Phần resume bên dưới được giữ để tái lập cách khôi phục attempt quota cũ;
không cần chạy lại để lấp dữ liệu còn thiếu trong phiên đã hoàn tất.

## Preflight

```bash
python scripts/preflight_provider.py --provider openrouter --model nvidia/nemotron-3.5-lightning:free
```

Model cố định đã preflight thành công. `openrouter/free` ở v0 là router nên model thực
có thể khác giữa các case. Tài liệu [OpenRouter](https://openrouter.ai/discover).
Không tự chuyển sang model tính phí khi hết quota miễn phí.

## Tiếp tục các phép đo bị quota chặn

Giữ nguyên snapshots để mỗi version vẫn có giả thuyết riêng. Các run cũ không bị ghi đè.
Khi có quota, resume v2 chỉ đo lại 6 case provider error; 14 case đã đo được giữ nguyên
và ghi `reused_from` ở từng case trong run mới. Run tổng hợp có `resumed_from`; nó trải
qua hai thời điểm, cần nêu giới hạn này khi so sánh. Để đo một phiên mới hoàn toàn,
bỏ `--resume-from` (20 API calls thay vì 6). Không resume giữa hai model khác nhau.

```bash
python run_eval.py --provider openrouter --model nvidia/nemotron-3.5-lightning:free --version v2 --suite base --eval-cases data/eval_base.json --system-prompt artifacts/versions/v2_system_prompt.md --tools artifacts/versions/v2_tools.yaml --resume-from runs/v2_B_base_openrouter_20261110T181712260298.json
python run_eval.py --provider openrouter --model nvidia/nemotron-3.5-lightning:free --version v3 --suite base --eval-cases data/eval_base.json --system-prompt artifacts/versions/v3_system_prompt.md --tools artifacts/versions/v3_tools.yaml
python run_eval.py --provider openrouter --model nvidia/nemotron-3.5-lightning:free --version v3 --suite group --eval-cases data/eval_group.json --system-prompt artifacts/versions/v3_system_prompt.md --tools artifacts/versions/v3_tools.yaml
```

`run_eval.py` luôn chặn thực thi `send`; vẫn chấm tool call model đề xuất.
Nếu gặp `free-models-per-day`, case đó có `execution_status=provider_call_failed`,
các case sau có `not_executed_quota`; chúng không được tính là đã đo.
Run hợp lệ cần `provider_error_cases=0`, `measured_cases=total_cases`.
Điểm trong run thiếu case không dùng để so sánh, kể cả JSON có `case_accuracy`.

Sau run hợp lệ, ghi log với tên run thực tế mà chương trình vừa in ra:

```bash
python scripts/record_version.py runs/<ten-run-v2-moi>.json --changed tools.yaml --hypothesis 'Description rõ routing và convention arguments' --before 0.7 --reason 'Hoàn tất sau khi có quota'
python scripts/record_version.py runs/<ten-run-v3-moi>.json --changed system_prompt.md --hypothesis 'Giữ trạng thái và áp dụng sửa đổi mới nhất' --reason 'Đo v3 sau khi có quota'
python scripts/record_version.py runs/<ten-run-group-moi>.json --changed data/eval_group.json --hypothesis 'Tổng quát hóa trên 10 case mới' --reason 'Suite group'
python scripts/parse_runs.py runs --output analysis/all_runs.csv
```

Không thay `<ten-run...>` bằng đường dẫn run lỗi. Helper mặc định từ chối run lỗi;
`--record-incomplete` chỉ ghi audit với `metric_after` trống, reason `INVALID`.
Bảng điểm trong báo cáo phải được cập nhật từ run hợp lệ mới, không xóa audit cũ.

## Chat nhiều lượt

```bash
python chat.py --provider openrouter --model nvidia/nemotron-3.5-lightning:free --version v3
```

Kịch bản chạy lại sau khi có quota, không có lệnh xác nhận gửi:

```bash
python chat.py --provider openrouter --model nvidia/nemotron-3.5-lightning:free --version v3 < data/chat_smoke_inputs.txt
```

Đã có live CLI đủ tình huống trong B4 báo cáo: phiên chính dùng
`data/chat_smoke_inputs_resumed_initial.txt`; một lượt không đọc example.com vì model
coi là placeholder. Phiên bổ sung dùng `data/chat_context_followup.txt` đã hỏi URL,
nhận URL tài liệu Streamlit thật rồi fetch/format thành công. Kịch bản
`chat_smoke_inputs.txt` hiện dùng URL thật cho lần kế tiếp và chưa chạy lại nguyên phiên.
Transcript/console của các phiên đã chạy vẫn giữ nguyên, không thay bằng dữ liệu giả.

Lịch sử giữ 5 cặp user/assistant gần nhất cùng kết quả tool để tái sử dụng nguồn.
`clarify` dừng cả batch. Lệnh `/send <nội dung>` tạo bản xem trước cục bộ;
`/confirm` duyệt và gửi chính xác bản đó, `/cancel` hủy, `/exit` thoát.
Tool call `send(confirmed=true)` do model tự sinh chỉ tạo preview, không tự gửi.
Mọi yêu cầu mới làm hết hiệu lực preview cũ. Transcript ghi rõ nguồn approval.
Các smoke test đã chạy không có `/confirm` và không gửi Telegram thật.

## Streamlit UI

```bash
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

Mở http://127.0.0.1:8501. Giao diện local có 3 gợi ý bấm để bắt đầu: tìm tin mới,
tóm tắt bài viết và sắp xếp nguồn. Câu hỏi mẫu gọi agent thật.
Sidebar mở **Cài đặt kết nối** để chọn provider/model; có thể xóa lịch sử, tải cuộc trò chuyện,
và mở **Gửi bản tin Telegram** để soạn bản gửi. Nút **Xác nhận gửi** xuất hiện sau khi có bản xem trước; nội dung
không qua model chỉnh sửa lúc gửi. Kết quả và lỗi tool hiển thị trong cuộc trò chuyện.
UI dùng đúng `run_model_tool_loop` của CLI; các lựa chọn model khác dùng mặc định có
sẵn trong provider adapter và chưa được live-verify trong phiên này.

Đã kiểm thử UI với model thật bằng `scripts/smoke_ui_live.py`: nguồn mẫu được đưa qua
chat input của AppTest, không fake provider/mạng, tool filter_sources chạy thật và
trả đúng URL. Bằng chứng `analysis/ui_live.json` cùng transcript Streamlit. Script
này dùng quota thật; không nằm trong pytest offline. Chỉ chạy lại nếu cần xác minh
tích hợp khi cấu hình/backend thay đổi:

```bash
python scripts/smoke_ui_live.py
```

Kiểm tra server khi đang chạy:

```bash
curl --fail http://127.0.0.1:8501/_stcore/health
```

URL trên là local. Chưa có URL demo public. Sites chạy server Cloudflare Worker,
không host trực tiếp tiến trình Streamlit/Python; giữ đúng stack Python của bài lab.
Máy chưa có `cloudflared`; không tạo tunnel hoặc đăng ký tài khoản trong phiên này.

Để deploy qua Streamlit Community Cloud khi người dùng có tài khoản và đã tự push:

1. Mở https://share.streamlit.io, chọn **Create app** và repo/branch muốn nộp.
2. Entrypoint: `starter_v0/app.py`. Dependency: `starter_v0/requirements.txt`.
3. Advanced settings: Python 3.11, khai báo các key cần dùng ở cấp gốc trong Secrets,
   ví dụ `OPENROUTER_API_KEY = "<key đặt trong giao diện Secrets>"`; không lưu key vào Git.
4. Deploy, thiết lập quyền truy cập phù hợp nhóm, thử lại các tình huống trong A3.
5. Ghi URL thực do nền tảng trả về vào A1. Tải transcript cần nộp về repo trước khi
   máy chủ cloud khởi động lại (filesystem cloud không phải lưu trữ bền vững).

Theo [hướng dẫn deploy](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
và [Secrets management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

## Unit tests và QA offline

```bash
python -m pytest -q
python -m compileall -q agent.py chat.py app.py run_eval.py tools providers scripts
python scripts/validate_submission.py
```

AppTest trong `tests/test_ui.py` dùng fake provider/HTTP và chạy thật vòng tool/UI,
không dùng API. Đây là kiểm thử offline; phân biệt với `scripts/smoke_ui_live.py`
đã chạy provider thật và có transcript live riêng. Tham khảo
[Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).
`validate_submission.py` kiểm tra baseline/base/extension không đổi, tool registry,
10 case, hash từng snapshot, CSV, cấu trúc báo cáo, và giá trị credential đã cấu hình
trong các file Git sẽ nhìn thấy. Không xuất key. Nó báo riêng các deliverable chờ.
