# Source code

Toàn bộ source code của lab nằm trong folder này. Chạy mọi lệnh từ `starter_v0/`.

- File bắt đầu chạy: `run_eval.py` (chạy eval), `chat.py` (chat live), `scripts/preflight_provider.py` (kiểm tra provider).
- Cách chạy bản hiện tại: `python run_eval.py --provider openrouter --model nvidia/nemotron-3.5-lightning:free --version v3 --suite base --eval-cases data/eval_base.json`; `python chat.py --provider openrouter --model nvidia/nemotron-3.5-lightning:free --version v3`; `pytest`. Baseline v0 đã có, không chạy lại để thay bằng chứng cũ.
- Input: `artifacts/system_prompt.md`, `artifacts/tools.yaml`, bộ case `data/*.json`, API key trong `.env` (mẫu ở `.env.example`).
- Output: `runs/*.json` (kết quả eval), `transcripts/*.transcript.json` (chat live), `analysis/*.csv` (nếu chạy `scripts/parse_runs.py`).
- File học viên được sửa: `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv`, `data/eval_group.json`, `tools/` (thêm tool mới và đăng ký trong `tools/__init__.py`), `tests/test_tools_todo.py`, code UI và `requirements.txt`. Không sửa nội dung case trong `data/eval_base.json`.

Chi tiết từng bước xem [README.md](../README.md) ở root; cấu hình API key xem [docs/TOOL-SETUP.md](../docs/TOOL-SETUP.md).

## Bản triển khai của nhóm

- Hướng dẫn chạy, resume eval, chat, UI và deploy: [RUNBOOK.md](RUNBOOK.md).
- Báo cáo chính thức và giới hạn kết quả: [group_report.md](../report/team/group_report.md).
- UI: `python -m streamlit run app.py` (dùng chung backend live với CLI).
- Tool mới: [filter_sources](tools/filter_sources/TOOL.md), lọc nguồn cục bộ.
- `python scripts/validate_submission.py`: integrity/schema/evidence/secret checks offline.
- Baseline v0 được giữ nguyên; v1/v2/v3 đạt lần lượt 70%/80%/75% trên base;
  v2 là run resume. Group v3 đạt 90%; live CLI/UI có transcript thật.
  Các attempt quota cũ giữ nguyên, metric trống trong version log.
