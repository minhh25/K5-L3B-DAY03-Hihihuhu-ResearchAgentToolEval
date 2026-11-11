# Báo cáo cá nhân — Nguyễn Đình Vũ Hải - 2A202603820

## 1. Thông tin thành viên

- Họ tên: Nguyễn Đình Vũ Hải    
- MSSV: 2A202603820
- Email: nguyendinhvuhai1234@gmail.com

## 2. Phần việc phụ trách

- **Cải thiện Prompt & Tool Configurations (CP2):** Sửa lỗi định tuyến (routing) của Agent thông qua việc tinh chỉnh `system_prompt.md` và định nghĩa lại tham số trong `tools.yaml`.
- **Thiết kế bộ Test Cases (Eval Group):** Viết 10 test cases (5 single-turn, 5 multi-turn) vào file `data/eval_group.json` để đánh giá năng lực của Model.
- **Phát triển công cụ mới (Custom Tool):** Phân tích nhu cầu, khai báo và lập trình Tool tính toán (`calculate`) tích hợp vào hệ thống.
- **Kiểm thử mã nguồn (Unit Test - CP3):** Giải quyết thử thách viết code kiểm thử cho 17 hàm (stub TODO), bao gồm giả lập API (mocking) và xử lý lỗi framework.

## 3. Đóng góp cụ thể

- **Tối ưu hóa Tool Routing (Accuracy từ 70% lên 100%):**
  - Xóa bỏ chỉ thị "ép chạy single-step" trong System Prompt, thiết lập quy tắc "Zero Guessing" để ngăn model tự bịa tham số.
  - Viết lại phần mô tả của tool `send` trong `tools.yaml` để thêm ranh giới bắt buộc xác nhận (Explicit Confirmation Boundary), giúp giải quyết triệt để lỗi `wrong_boundary`.
  - Cập nhật quy ước tham số (Arg Conventions) cho `lookup` (chỉ định rõ `news` vs `general`) và `social_search` (`Top` vs `Latest`), khắc phục các lỗi `wrong_arg_value`.
- **Hoàn thiện Eval Data:**
  - Viết 10 kịch bản test chất lượng cao phủ các trường hợp logic như: happy path, out_of_scope, missing_info (ép dùng clarify) và luồng gọi tool mới. Sửa lỗi cú pháp file (chuyển từ Mảng sang JSON Object có key `cases`) giúp `run_eval.py` chạy mượt mà.
  - Theo dõi và điền đầy đủ nhật ký thay đổi phiên bản vào `artifacts/version_log.csv`.
- **Tạo Custom Tool (`calculate`):** 
  - Khai báo logic tool tính toán để ngăn chặn tình trạng "hallucination" số liệu của LLM.
  - Code trực tiếp hàm `calculate_math` (có cơ chế bắt lỗi an toàn) và đăng ký vào `TOOL_FUNCTIONS` trong `tools/__init__.py`.
- **Vượt qua Thử thách Unit Test (0 Failed, 0 Skipped):**
  - Viết đầy đủ 17 hàm test trong `tests/test_tools_todo.py`.
  - Xử lý các tình huống phức tạp: sử dụng `monkeypatch` để thao tác biến môi trường.
  - Chủ động phát hiện cấu trúc `fake_http` / `FakeResponse` không tương thích (gây lỗi `AttributeError` / `TypeError`), sau đó tự xây dựng class `MockResponse` nội bộ để giả lập requests HTTP, giúp toàn bộ bộ test PASSED.

## 4. Bằng chứng

- **File/commit/PR:** 
  - `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv`.
  - `data/eval_group.json` (chứa 10 test cases chuẩn).
  - `tools/__init__.py` (chứa logic và đăng ký tool `calculate_math`).
  - `tests/test_tools_todo.py` (chứa 17 đoạn code unit test đã pass).
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - **Công cụ AI:** Sử dụng LLM như một "Pair Programmer" để phân tích file log đầu ra của `run_eval.py` và `pytest`, phát hiện nguyên nhân gây lỗi (như mâu thuẫn system prompt, lỗi JSON parsing, thiếu key trong framework mock) và refactor code.
  - **Tự kiểm tra:** Chạy lệnh `python run_eval.py` lặp lại qua các version (v1, v2, v3) cho đến khi đạt Tool Routing Accuracy 100%. Chạy lệnh `pytest tests/test_tools_todo.py -v` liên tục, sửa từng bug một cho đến khi thanh kết quả báo "17 passed, 0 failed, 0 skipped".

## 5. Tự đánh giá

- Hoàn thành đầy đủ các yêu cầu cơ bản (cải tiến tool, eval, tạo tool mới và viết 3 test cho tool mới).
- Đạt điểm Challenge: Điền và code chạy thành công toàn bộ các `pytest.skip(TODO)` trong bài.
- Đạt điểm Challenge+: Phát hiện lỗi và giới hạn của bộ mock test ban đầu, tự fix bằng phương pháp Mocking hướng đối tượng (tạo MockResponse riêng). Mức độ đóng góp và nắm bắt logic kiến trúc của Agent (phân biệt giữa khai báo yaml cho model đọc và code python thực thi local) là rất tốt. Đánh giá hoàn thành
