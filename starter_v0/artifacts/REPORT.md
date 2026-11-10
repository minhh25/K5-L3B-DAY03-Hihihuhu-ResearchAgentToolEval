# Báo cáo kỹ thuật — Day03

Báo cáo chính thức theo cấu trúc Phần A/B của đề bài:
[report/team/group_report.md](../../report/team/group_report.md).

## Trạng thái

- v0 giữ nguyên: 13/20, case 0.65, routing 0.75, argument 0.65, multiturn 0.6667.
- v1 đo đủ: 14/20, case 0.70, routing 0.95, argument 0.70, multiturn 0.6667.
- v2 hoàn tất bằng resume: 16/20, case 0.80, routing 0.95, argument 0.80, multiturn 0.50.
- v3 đo đủ: 15/20, case 0.75, routing 0.85, argument 0.75, multiturn 0.6667.
  v3 giảm điểm tổng thể so với v2; không sửa prompt sau đo để che kết quả giảm.
- v3 group: 9/10, routing 1.00, argument 0.90, multiturn 0.80. Cả 2 case tool mới PASS.
- Các attempt quota cũ vẫn giữ với INVALID/metric_after trống; các run hợp lệ mới
  được thêm vào log. Không dùng 92.86% của phần v2 như điểm hợp lệ.
- Prompt/tools v0–v3 có snapshot riêng trong [versions](versions), hash và giả thuyết
  trong [version_log.csv](version_log.csv); baseline kiểm tra bằng
  [baseline_integrity.json](baseline_integrity.json).
- Tool mới, tests, UI đã triển khai. Xem A2/B5a/B5 của báo cáo chính thức.
- Live CLI: 6 lượt qua 2 phiên, gồm research, hỏi URL rồi đọc tài liệu công khai và
  xác nhận trước gửi. Có 1 lượt hỏi lại example.com vì coi là placeholder, được ghi rõ.
- Live UI: AppTest gọi provider thật, chọn filter_sources đúng, không nhấn gửi Telegram.
  [ui_live.json](../analysis/ui_live.json). Các transcript lỗi quota cũ vẫn giữ.
- Chưa public URL, danh tính/đóng góp thật, commit/push/LMS vẫn chờ người dùng.

## Chỉ mục bằng chứng và tái lập

- Failure analysis 7 case v0: bảng **B2** trong báo cáo chính thức, đối chiếu
  [baseline JSON](../runs/v0_B_base_openrouter_20261110T174805758386.json).
- So sánh v0–v3 và hạn chế model: **B1**.
- 10 case nhóm: **B3**, [eval_group.json](../data/eval_group.json).
- Chat: **B4**, [transcripts](../transcripts).
- Kiểm thử thực: [pytest.txt](../analysis/pytest.txt), [verification.json](../analysis/verification.json).
- UI startup: [ui_startup.json](../analysis/ui_startup.json).
- [RUNBOOK](../RUNBOOK.md): preflight/eval/resume/chat/UI/tests/deploy.
- [all_runs.csv](../analysis/all_runs.csv): dữ liệu phẳng, bao gồm cả attempt lỗi;
  phải lọc provider_error trước khi diễn giải điểm.
- [results_summary.json](../analysis/results_summary.json): chỉ mục run hợp lệ mới nhất.
