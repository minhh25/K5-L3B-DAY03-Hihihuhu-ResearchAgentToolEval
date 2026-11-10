# Báo cáo cá nhân — Nguyễn Đình Minh - 2A202603867

## 1. Thông tin thành viên

- Họ tên: Nguyễn Đình Minh
- MSSV: 2A202603867
- Email: nguyenminh25112k4@gmail.com

## 2. Phần việc phụ trách

Ở bài này, nhóm Hihihuhu cùng làm toàn bộ các phần, từ cấu hình môi trường,
chỉnh prompt, bổ sung tool, viết test đến chạy eval, làm giao diện và hoàn thiện
báo cáo. Em cùng các bạn tham gia các bước đó, không chia theo kiểu mỗi người chỉ
làm một phần riêng.

Phần em chọn để trình bày kỹ trong báo cáo cá nhân là **Tool Unit Test Challenge,
tập trung vào tool mới `filter_sources`**. Em đã tự chạy lại các lệnh kiểm thử
trên terminal để kiểm tra tool, đăng ký tool và toàn bộ suite.

## 3. Đóng góp cụ thể

Với phần agent, em cùng nhóm thực hiện các vòng sửa prompt và tool declaration.
v1 tập trung vào hỏi lại khi thiếu thông tin và xác nhận trước khi gửi; v2 làm rõ
cách chọn tool và cách điền arguments; v3 bổ sung quy tắc giữ ngữ cảnh và ưu tiên
thông tin người dùng sửa ở lượt sau. Nhóm giữ nguyên bộ case base để so sánh kết quả,
không sửa đáp án theo những gì model trả về.

Với tool challenge, nhóm bổ sung `filter_sources` để xử lý danh sách nguồn đã có.
Khi tìm từ nhiều nơi, một bài có thể xuất hiện với vài URL khác nhau do có thêm
tham số theo dõi hoặc fragment. Tool này giúp lọc danh sách trước khi tổng hợp,
không cần gọi thêm API. Phần xử lý gồm:

- Nhận danh sách `items` cùng các điều kiện `include_domains`, `exclude_domains`,
  `min_score` và `limit`.
- Chuẩn hóa URL, bỏ `utm_*`, `fbclid`, `gclid` và fragment, sau đó loại nguồn trùng.
  Tool giữ thứ tự ban đầu và không sửa danh sách đầu vào.
- Lọc theo domain, gồm cả subdomain; điều kiện loại trừ được ưu tiên. Ví dụ,
  `evilexample.com` không được coi là thuộc `example.com`.
- Trả về các nguồn giữ lại và số lượng nguồn đã loại. Nếu collection hoặc tiêu chí
  sai kiểu, tool trả error dict để agent xử lý tiếp.

Một trường hợp kiểm tra cụ thể là URL `https://example.com/a`.
Sau khi chuẩn hóa, cả hai cùng trỏ tới một URL nên chỉ giữ lại một nguồn.
Tool chỉ lọc theo điều kiện được đưa vào, không tự đánh giá bài viết đáng tin hay không.

Phần test em chọn kiểm tra có ba nhóm chính: đầu vào bình thường, đầu vào sai và
nhánh xảy ra lỗi. Ngoài ra còn có dữ liệu rỗng, `limit=0`, URL không hợp lệ và việc
giữ nguyên query có ý nghĩa như `q=agent`. Test nhánh lỗi chủ động làm hàm chuẩn hóa
phát sinh `OSError`, rồi kiểm tra tool trả error dict thay vì làm dừng chương trình.

Em cũng cùng nhóm hoàn thiện bộ 10 case eval gồm 5 single-turn và 5 multi-turn,
kiểm tra luồng chat và giao diện Streamlit. Hai case G01 và G07 kiểm tra model có
chọn đúng `filter_sources` và giữ đúng các điều kiện lọc hay không; cả hai đều PASS.
Đây là phần kiểm tra riêng với unit test: code của tool chạy đúng chưa có nghĩa là
model sẽ luôn chọn đúng tool hoặc truyền đúng arguments.

## 4. Bằng chứng

Các file liên quan đến phần em chọn:

| Nội dung | Bằng chứng |
|---|---|
| Logic và hợp đồng của tool mới | [tool.py](../../starter_v0/tools/filter_sources/tool.py), [TOOL.md](../../starter_v0/tools/filter_sources/TOOL.md) |
| Đăng ký tool và schema model sử dụng | [tools/__init__.py](../../starter_v0/tools/__init__.py), [tools.yaml](../../starter_v0/artifacts/tools.yaml) |
| Unit tests cho tool challenge | [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py) |
| Output em tự chạy trên terminal | [minh_tool_test_terminal.txt](../../starter_v0/analysis/minh_tool_test_terminal.txt) |
| Case nhóm và kết quả chọn tool mới | [eval_group.json](../../starter_v0/data/eval_group.json), [run group v3](../../starter_v0/runs/v3_B_group_openrouter_20261110T184314570949.json) |
| Các vòng thử nghiệm và số đo | [version_log.csv](../../starter_v0/artifacts/version_log.csv), [báo cáo nhóm](group_report.md) |
| Giao diện và hướng dẫn chạy | [app.py](../../starter_v0/app.py), [RUNBOOK.md](../../starter_v0/RUNBOOK.md) |

Em tự chạy các lệnh sau trong thư mục `starter_v0` với virtualenv của bài:

| Lệnh | Kết quả ở lần em tự kiểm tra |
|---|---|
| `python -m pytest -v tests/test_tools_todo.py` | 38 passed |
| `python -m pytest -v tests/test_tools_todo.py -k filter_sources` | 15 passed, 23 deselected |
| `python -m pytest -q tests/test_tool_contract.py` | 60 passed |
| `python -m pytest -q` | 120 passed, không có failed hoặc skipped |

15 test của `filter_sources` nằm trong 38 test challenge. `23 deselected` ở lệnh
thứ hai là các test không được chọn bởi bộ lọc `-k`, không phải test bị lỗi hay skip.
Các test này chạy offline; HTTP được giả lập nên không tốn quota và không gửi
Telegram thật.

Sau lần em tự kiểm tra trên, phần giao diện được bổ sung hai test nữa. Vì vậy
[log toàn suite mới nhất](../../starter_v0/analysis/pytest.txt) là **122 passed**;
con số **120 passed** trong bảng là kết quả terminal em đã gửi, không thay bằng
kết quả của lần chạy sau.

Nhóm có dùng **Codex** để hỗ trợ viết và sửa code, gợi ý test, phân tích log và
rà soát tài liệu. Báo cáo này cũng có hỗ trợ biên tập. Phần em tự kiểm tra trực tiếp
là chạy lại các lệnh ở trên và đối chiếu output, không chỉ dựa vào thông báo của AI.

Commit/PR kỹ thuật cá nhân hiện chưa được chốt; em cần bổ sung mã commit thật trước
khi nộp bài.

## 5. Tự đánh giá

Phần tool challenge có code, test và output cụ thể để đối chiếu. Ở lần em tự chạy,
cả 38 test challenge và 15 test riêng của tool mới đều đạt, toàn suite không còn
test bị skip. Đây là phần em đã kiểm tra trực tiếp trên máy.

Tuy vậy, em không xem việc unit test đều xanh là agent đã làm đúng mọi yêu cầu.
Kết quả base của nhóm lần lượt là v0 65%, v1 70%, v2 80% và v3 75%; bộ nhóm đạt 90%.
v3 vẫn có lỗi thiếu `topic=news`, gọi thừa tool và hỏi lại số lượng đã có trong ngữ
cảnh. Vì vậy, phần prompt còn cần cải thiện dù code của tool đã qua kiểm thử.

Phần cần làm tiếp trước khi nộp là bổ sung commit kỹ thuật cá nhân và cùng nhóm
hoàn tất demo public. Giao diện hiện đã có bản local, còn việc người ngoài nhóm
dùng thử và URL public chưa có bằng chứng để ghi là hoàn thành.
