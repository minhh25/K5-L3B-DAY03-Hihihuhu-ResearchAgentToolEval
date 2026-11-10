# Team

## Thông tin nhóm

- Tên nhóm: **Hihihuhu**.
- Lớp: **L3B**.
- Repo: [K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval).
- Bản nhóm chọn để nộp: bản của **Nguyễn Đình Minh**, đang làm trên nhánh `nguyendinhminh`.
- Người tổng hợp, push và thực hiện merge bản nộp: **Nguyễn Đình Minh**.
- Tool được chọn cho phần **Tool Unit Test Challenge**: **`filter_sources`**; Minh đại diện trình bày.
- Nhánh nộp dự kiến: `main`, sau khi PR của Minh được kiểm tra và merge.
- Commit chốt: **chưa có SHA chốt**. Cần ghi commit thực tế sau khi bản nộp được đưa lên GitHub; không dùng commit của starter làm commit hoàn thành bài.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò trong bài |
| --: | ------ | ---- | ----- | ------ | ----------------- |
| 1 | Nguyễn Đình Minh | 2A202603867 | nguyenminh25112k4@gmail.com | [minhh25](https://github.com/minhh25) | Cùng làm toàn bộ yêu cầu; đại diện tool challenge `filter_sources`, tổng hợp bản được chọn và thực hiện merge |
| 2 | Nguyễn Đình Vũ Hải | 2A202603820 | nguyendinhvuhai1234@gmail.com | [HaiVuuu](https://github.com/HaiVuuu) | Cùng làm toàn bộ yêu cầu; có bản thử nghiệm prompt/eval và tool `calculate` trên nhánh riêng |
| 3 | Đoàn Xuân Duy Bảo | 2A202603858 | doanxuanduybao96@gmail.com | [CapybaraSlayer96](https://github.com/CapybaraSlayer96) | Cùng làm toàn bộ yêu cầu; có bản thử nghiệm Gemini, các tool bổ sung và run model local trong PR #2 |
| 4 | Vũ Tiến Hùng | 2A202603882 | hungvu.education@gmail.com | [hungvueducation-hash](https://github.com/hungvueducation-hash) | Cùng làm toàn bộ yêu cầu; có bản thử nghiệm prompt, tool `sentiment`, UI và luồng xác nhận Telegram trong PR #1 |

## Cách nhóm thực hiện bài và chọn bản nộp

Cả bốn thành viên đều tham gia các phần của bài lab: cấu hình môi trường, chạy
baseline, chỉnh prompt và tool declaration, bổ sung tool, viết test, chạy eval,
làm UI, thử chat và viết báo cáo. Mỗi người có một bản triển khai ở nhánh riêng
để nhóm đối chiếu cách làm và kết quả. Các phần nổi bật ghi dưới đây là những gì
có thể trỏ tới bằng commit, PR hoặc file; đó không phải cách chia việc độc quyền
cho từng người.

Sau khi so sánh, nhóm thống nhất dùng bản của Minh làm bản nộp chính. Minh phụ
trách tổng hợp tài liệu và thực hiện push/merge. Phần Tool Unit Test Challenge
được chọn là `filter_sources`, với các test lọc nguồn, chuẩn hóa URL, loại trùng,
đầu vào sai và nhánh lỗi.

Các commit và PR của Hải, Bảo, Hùng được giữ để ghi nhận quá trình làm bài và các
hướng thử nghiệm của nhóm. Ở thời điểm đối chiếu GitHub ngày **10/11/2026**, PR
#1 và #2 vẫn đang mở; nhánh Hải đã có hai commit, chưa thấy PR của Hải trong danh
sách PR được đọc. Các bản này chưa được gộp vào working tree của Minh. Vì vậy,
registry và số liệu của bản chính vẫn là của bản Minh; tool ở các nhánh khác được
liệt kê như các thử nghiệm có bằng chứng riêng.

### Đối chiếu kết quả các bản triển khai

Bảng lấy số liệu từ run JSON, chọn các run đủ số case và không có provider error.
Đây là các thí nghiệm riêng: provider/model, prompt và bộ case nhóm khác nhau,
nên không coi điểm số là một phép xếp hạng trực tiếp giữa các thành viên.

| Bản triển khai | Provider/model của run được dẫn | Base | Group | Tool thử nghiệm |
|---|---|---|---|---|
| Minh — bản nộp được chọn | OpenRouter / `nvidia/nemotron-3.5-lightning:free` | [v3: 15/20, 75%](starter_v0/runs/v3_B_base_openrouter_20261110T184502669655.json) | [v3: 9/10, 90%](starter_v0/runs/v3_B_group_openrouter_20261110T184314570949.json) | `filter_sources` |
| Hải — `nguyendinhvuhai` | OpenRouter / `openai/gpt-4o-mini` | [v3: 15/20, 75%](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/d86c8c337e3001d6a9b1471c4428bb3996f6fca3/starter_v0/runs/v3_B_base_openrouter_20261110T181843630923.json) | [v3: 9/10, 90%](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/d86c8c337e3001d6a9b1471c4428bb3996f6fca3/starter_v0/runs/v3_B_group_openrouter_20261110T191101668964.json) | `calculate` |
| Bảo — `doanxuanduybao` | Gemini / `gemini-3.8-flash` | [v7: 17/20, 85%](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/2b39c22da839beca9c392173628475a72b3d2329/starter_v0/runs/v7_B_base_gemini_20261110T213204182019.json) | [v7: 10/10, 100%](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/2b39c22da839beca9c392173628475a72b3d2329/starter_v0/runs/v7_B_group_gemini_20261110T213314649731.json) | `hackernews`, `wikipedia`, `github_repo`, `dedupe` |
| Hùng — `vutienhung` | OpenRouter / `openai/gpt-4o-mini` | [v4d: 19/20, 95%](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/7291b98d19fbcb44d0dcc6611f2ebc60c0626ad7/starter_v0/runs/v4d_B_base_openrouter_20261110T194355154509.json) | [v4c: 7/10, 70%](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/7291b98d19fbcb44d0dcc6611f2ebc60c0626ad7/starter_v0/runs/v4c_B_group_openrouter_20261110T190545487755.json) | `sentiment` |

Bản Minh có kết quả base v0–v3 lần lượt là **65% → 70% → 80% → 75%**. v2 là run
resume sau khi hết quota; v3 giảm điểm so với v2 và đã được phân tích trong báo cáo
nhóm. Ở nhánh Bảo, v4 từng đạt 20/20, còn v7 đạt 17/20; các run đều được giữ. Nhóm
không thay số liệu của bản được chọn bằng điểm cao hơn của một nhánh khác.

Metadata của bảy commit và summary của các run được đối chiếu nằm trong
[team_github_evidence_20261110.json](starter_v0/analysis/team_github_evidence_20261110.json).
Việc đối chiếu chỉ đọc code và bằng chứng đã lưu trên GitHub; không chạy lại
pytest hoặc các model của ba nhánh khác trong môi trường của Minh.

## Cá nhân

## Nguyễn Đình Minh — 2A202603867

### Phần việc phụ trách

Cùng nhóm thực hiện toàn bộ bài lab. Đại diện trình bày Tool Unit Test Challenge
với `filter_sources`, tổng hợp bản nộp và thực hiện push/merge sau khi kiểm tra.

### Đóng góp cụ thể

- Tham gia hoàn thiện các vòng prompt/tool declaration v1–v3, lưu baseline và phân tích lỗi theo run thật.
- Cùng nhóm bổ sung `filter_sources`: lọc domain/score, chuẩn hóa URL và loại nguồn trùng; tool có 15 test riêng trong challenge.
- Tự chạy lại các lệnh kiểm thử trên terminal: 38 test challenge, 15 test riêng của tool, 60 contract test và 120 test toàn suite ở thời điểm kiểm tra đó.
- Hoàn thiện bản local với 10 case nhóm, transcript chat, UI Streamlit và tài liệu. Sau khi thêm hai test UI, log mới nhất của bản này là 122 passed, 0 failed, 0 skipped.
- Tổng hợp đóng góp của các thành viên từ commit và PR, giữ bản Minh làm bản chính theo thống nhất của nhóm.

### Bằng chứng

- [Báo cáo cá nhân](report/team/2A202603867_NguyenDinhMinh.md).
- [Tool và hợp đồng](starter_v0/tools/filter_sources/TOOL.md), [unit tests](starter_v0/tests/test_tools_todo.py).
- [Output terminal Minh tự chạy](starter_v0/analysis/minh_tool_test_terminal.txt), [log suite hiện tại](starter_v0/analysis/pytest.txt).
- [Version log](starter_v0/artifacts/version_log.csv), [báo cáo nhóm](report/team/group_report.md), [kiểm thử UI](starter_v0/analysis/ui_redesign_verification.json).
- Commit/PR của bản chính: **đang chờ Minh commit và push nhánh `nguyendinhminh`**. Chưa có link PR hoặc SHA kỹ thuật của bản này để ghi.
- AI hỗ trợ: Codex; phần tự kiểm tra và phạm vi hỗ trợ được ghi trong báo cáo cá nhân.

## Nguyễn Đình Vũ Hải — 2A202603820

### Phần việc phụ trách

Cùng nhóm thực hiện toàn bộ yêu cầu. Bản đã đẩy lên GitHub nằm ở nhánh
`nguyendinhvuhai`, với các thử nghiệm prompt/eval và tool tính toán.

### Đóng góp cụ thể

- Commit `a5aae71` cập nhật prompt, tool declaration, version log, case nhóm và tests; bổ sung run v0–v3 base cùng run group v3.
- Commit `d86c8c3` bổ sung logic `calculate_math`, cập nhật registry và các test cho tool `calculate`.
- Ba tình huống test của tool gồm biểu thức `1500 + 2500`, chuỗi rỗng và phép chia cho 0.
- Các run JSON được đọc ghi nhận base v0 70%, v1 75%, v2 75%, v3 75%; group v3 đạt 9/10.

### Bằng chứng

- [Nhánh nguyendinhvuhai](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/tree/nguyendinhvuhai).
- [a5aae71 — Initial commit](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/commit/a5aae7189923acb2a793515ae709c41c70922301).
- [d86c8c3 — Updated](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/commit/d86c8c337e3001d6a9b1471c4428bb3996f6fca3).
- [Code tool](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/d86c8c337e3001d6a9b1471c4428bb3996f6fca3/starter_v0/tools/calculate_math/tool.py), [test file](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/d86c8c337e3001d6a9b1471c4428bb3996f6fca3/starter_v0/tests/test_tools_todo.py).
- Chưa thấy báo cáo cá nhân, UI hoặc transcript được bổ sung trong diff của nhánh Hải so với `main` ở thời điểm đối chiếu; cần bổ sung bằng chứng thực tế nếu muốn ghi nhận các phần này riêng cho nhánh.

## Đoàn Xuân Duy Bảo — 2A202603858

### Phần việc phụ trách

Cùng nhóm thực hiện toàn bộ yêu cầu. Bản thử nghiệm riêng nằm ở nhánh
`doanxuanduybao`, được gửi qua PR #2.

### Đóng góp cụ thể

- Commit `f297b27` bổ sung các vòng prompt/tool v1–v4, bốn tool `hackernews`, `wikipedia`, `github_repo`, `dedupe`, tests, eval nhóm, UI Streamlit và báo cáo.
- Sửa provider Gemini để nhận `GEMINI_BASE_URL`; lưu các run base và group bằng Gemini.
- Commit `2b39c22` bổ sung v5–v7 về routing/description/response_type và một run local Qwen qua Ollama.
- Test file có ba hàm test cho mỗi tool mới; các stub đã được thay bằng code kiểm thử. Báo cáo cá nhân của Bảo ghi kết quả tự chạy là 108 passed, 0 skipped.
- Run Gemini v4 đạt 20/20 base; run v7 đạt 17/20 base và 10/10 group. Run local Qwen được lưu riêng, không dùng làm điểm của bản Minh.

### Bằng chứng

- [PR #2 — Doanxuanduybao](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/pull/2), đang mở tại thời điểm đối chiếu.
- [f297b27](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/commit/f297b27d0724db111fda4cc512ec3a01d758ee0d), [2b39c22](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/commit/2b39c22da839beca9c392173628475a72b3d2329).
- [Báo cáo cá nhân trên PR](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/2b39c22da839beca9c392173628475a72b3d2329/report/team/2A202603858_DoanXuanDuyBao.md).
- [Các tool](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/tree/2b39c22da839beca9c392173628475a72b3d2329/starter_v0/tools), [tests](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/2b39c22da839beca9c392173628475a72b3d2329/starter_v0/tests/test_tools_todo.py).
- Báo cáo cá nhân nêu việc dùng Claude Code và tự kiểm tra bằng pytest, eval và run JSON.

## Vũ Tiến Hùng — 2A202603882

### Phần việc phụ trách

Cùng nhóm thực hiện toàn bộ yêu cầu. Bản thử nghiệm riêng nằm ở nhánh `vutienhung`,
được gửi qua PR #1.

### Đóng góp cụ thể

- Commit `313a64a` lưu baseline, các vòng tối ưu prompt/tool declaration và phân tích lỗi; có cả thử nghiệm giảm điểm để đối chiếu giả thuyết.
- Commit `d0bbdb2` bổ sung tool `sentiment`, ba test riêng, 10 case nhóm, UI Streamlit và transcript; có sửa phần xuất console UTF-8 trong `chat.py`.
- Tool `sentiment` dùng tập từ tích cực/tiêu cực để phân loại văn bản và trả các từ khớp; xử lý kiểu đầu vào sai bằng error dict.
- Commit `7291b98` tiếp tục sửa luồng xác nhận gửi Telegram ở v4d, đồng thời bổ sung run và transcript tương ứng.
- Run base v4d đạt 19/20; run group v4c đủ 10 case đạt 7/10. Test plan trong PR ghi 70 passed, 14 skipped; không dùng con số này thay cho kết quả 122 passed của bản chính.

### Bằng chứng

- [PR #1 — CP1–CP5](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/pull/1), đang mở tại thời điểm đối chiếu.
- [313a64a](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/commit/313a64a8456cff0373be7a8719d1dd896aa527cd), [d0bbdb2](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/commit/d0bbdb21674addf6a62837335cbf6c7bd98a5ad3), [7291b98](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/commit/7291b98d19fbcb44d0dcc6611f2ebc60c0626ad7).
- [Báo cáo cá nhân trên PR](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/7291b98d19fbcb44d0dcc6611f2ebc60c0626ad7/report/team/2A202603882_VuTienHung.md).
- [Tool sentiment](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/blob/7291b98d19fbcb44d0dcc6611f2ebc60c0626ad7/starter_v0/tools/sentiment/tool.py), [transcripts](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/tree/7291b98d19fbcb44d0dcc6611f2ebc60c0626ad7/starter_v0/transcripts).
- PR và commit có ghi việc dùng Claude Code hỗ trợ; kết quả thử nghiệm được dẫn về run JSON của nhánh.

## Việc cần hoàn tất trước khi nộp

- Minh commit/push bản được chọn và mở PR từ `nguyendinhminh` vào `main`; kiểm tra trước khi merge và ghi commit chốt thực tế.
- Đưa đủ báo cáo cá nhân của bốn thành viên vào nhánh nộp. Hiện working tree của Minh mới có báo cáo cá nhân của Minh; báo cáo Bảo/Hùng còn nằm trong PR, và chưa thấy báo cáo Hải trên nhánh đã đọc.
- Đối chiếu yêu cầu mỗi thành viên có commit kỹ thuật trong lịch sử nhánh nộp theo [SUBMISSION.md](SUBMISSION.md). Link tới PR đang mở là bằng chứng quá trình làm, chưa đồng nghĩa commit đã vào `main`.
- Hoàn tất URL demo public nếu dùng để nộp/dùng thử; bản UI hiện có demo local và bằng chứng kiểm thử.
- Từng thành viên tự kiểm tra báo cáo của mình, ghi công cụ AI đã dùng và tự nộp cùng link repo trên LMS.

Hướng dẫn các lệnh kiểm tra, commit, push và mở PR cho bản Minh:
[PUSH_GUIDE.md](report/team/PUSH_GUIDE.md).
