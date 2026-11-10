# Đưa bản Minh lên GitHub và tạo PR nộp bài

Bản được nhóm chọn đang ở nhánh local `nguyendinhminh`. Các lệnh dưới đây dành
cho Minh tự chạy; chưa có lệnh commit, push hoặc merge nào được thực hiện thay.

## 1. Kiểm tra ở root repo

```bash
cd "/Users/minh25/Documents/AI Thuc chien Vin/LAB/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval"
source .venv/bin/activate

git branch --show-current
git status --short

python -m pytest -q starter_v0/tests
python starter_v0/scripts/validate_submission.py
```

Nhánh hiện tại cần là `nguyendinhminh`. Kết quả suite gần nhất là **122 passed,
0 failed, 0 skipped**. Script kiểm tra submission đối chiếu hash baseline,
schema/registry, evidence và giá trị credential đã cấu hình; danh sách `pending`
vẫn nhắc các phần chưa xong như demo public và thông tin nộp bài.

Nếu Git chưa có đúng danh tính của Minh cho repo này, đặt cấu hình local:

```bash
git config user.name "Nguyễn Đình Minh"
git config user.email "nguyenminh25112k4@gmail.com"
```

## 2. Chọn file để commit

```bash
git check-ignore -v starter_v0/.env .venv/

git add .gitignore TEAM.md report/team starter_v0

git diff --cached --stat
git diff --cached --name-only
```

Kiểm tra danh sách staged trước khi commit. `.env`, `.venv/`, API key và cache
không được đưa vào commit. `.env.example` là file cấu hình mẫu và được giữ lại.
Lệnh `git add` trên sẽ lấy cả code, báo cáo, run JSON, transcript và evidence của
bản Minh; các file đang bị ignore sẽ không được thêm mới.

Bản mẫu `report/team/MSSV_HoTen.md` đang được thay bằng báo cáo đã đổi tên
`report/team/2A202603867_NguyenDinhMinh.md`, nên việc thấy xóa tên mẫu và thêm tên
mới là đúng với thay đổi hiện tại.

## 3. Commit và push nhánh Minh

```bash
git commit -m "feat: complete Day03 lab with filter_sources and team evidence"
git push -u origin nguyendinhminh
```

Lệnh push này tạo/cập nhật nhánh `nguyendinhminh` trên repo nhóm. Nó chưa tự merge
vào `main`. Không cần đổi sang `main` trong lúc working tree còn các thay đổi
chưa commit.

Nếu GitHub yêu cầu xác thực, dùng tài khoản GitHub `minhh25` qua cơ chế đăng nhập
Git đang có trên máy. Không đưa token vào file báo cáo hoặc câu lệnh được chia sẻ.

## 4. Tạo PR vào main

Sau khi push thành công, mở:

[So sánh main với nguyendinhminh](https://github.com/minhh25/K5-L3B-DAY03-Hihihuhu-ResearchAgentToolEval/compare/main...nguyendinhminh?expand=1)

Chọn **base: main**, **compare: nguyendinhminh**, rồi **Create pull request**.

Tiêu đề gợi ý:

```text
Hoàn thiện Day03: filter_sources, tool challenge và bản nộp nhóm
```

Nội dung PR có thể dùng:

```markdown
Bổ sung tool filter_sources, xử lý hỏi lại/xác nhận, bộ test, 10 case eval nhóm
và UI Streamlit cho research agent. TEAM.md ghi nhận đóng góp từ các nhánh/PR
của bốn thành viên; bản Minh được nhóm chọn làm bản nộp chính.

Validation:
- Pytest: 122 passed, 0 failed, 0 skipped.
- Base eval v0–v3: 65%, 70%, 80%, 75%; v2 là run resume.
- Group eval v3: 9/10, không có provider error.
- Có transcript CLI/UI thật, ảnh kiểm tra desktop/mobile và demo local.
- Giữ nguyên baseline v0 và các attempt quota cũ.

Còn cần hoàn tất: URL demo public, đủ báo cáo cá nhân trên nhánh nộp và xác nhận
lịch sử commit kỹ thuật của từng thành viên. Chi tiết trong TEAM.md.
```

Trong **Files changed**, kiểm tra đúng bản Minh và các bằng chứng dự định nộp.
Khi các kiểm tra/quyền của repo cho phép, Minh chọn **Merge pull request** với
phương thức tạo merge commit và **Confirm merge**.

Sau khi merge, có thể xem commit thực tế trên `main` bằng:

```bash
git fetch origin
git log -1 origin/main --format="%H %s"
```

Dùng SHA/link PR thật để cập nhật thông tin chốt bài trong `TEAM.md`, rồi commit
phần cập nhật tài liệu nếu cần. Không ghi trước một SHA hoặc số PR chưa tồn tại.

## 5. Lưu ý về commit của các thành viên

[SUBMISSION.md](../../SUBMISSION.md) yêu cầu:

> Mỗi thành viên có commit kỹ thuật trong lịch sử branch nộp bài.

Nếu chỉ merge PR Minh, các commit của Hải trên `nguyendinhvuhai` và commit trong
PR #1/#2 chưa tự xuất hiện trong lịch sử `main`. Việc dẫn link các commit đó trong
`TEAM.md` giúp chứng minh quá trình làm bài, nhưng chưa thay thế yêu cầu về lịch
sử nhánh nộp.

Để giữ bản Minh làm bản chính và vẫn có đóng góp thật của từng người, các thành
viên có thể tạo PR nhỏ từ `main` mới, bổ sung code/test phù hợp với bản đã chọn và
báo cáo cá nhân của mình. Minh review và merge các thay đổi này. Các PR thử nghiệm
lớn vẫn được giữ làm bằng chứng; không cần gộp toàn bộ các phiên bản prompt/UI
khác nhau vào cùng một bản.

Trước khi nộp, cần có báo cáo cá nhân đủ bốn thành viên trong nhánh nộp. Hiện
working tree này có báo cáo Minh; báo cáo Bảo/Hùng đã thấy trong PR riêng, còn báo
cáo Hải chưa thấy trên nhánh được đối chiếu. Mỗi người cần tự xác nhận nội dung
và phần AI/công cụ đã dùng trong báo cáo của mình.
