---
name: sentiment
track: core
kind: local_formatter
provider: none
requires_env: []
inputs: [text]
outputs: [label, positive_hits, negative_hits]
side_effect: false
---

# sentiment

Phân tích cảm xúc đơn giản (tích cực / tiêu cực / trung lập) của một đoạn
văn bản, dựa trên đếm từ khóa tích cực/tiêu cực (tiếng Việt không dấu +
tiếng Anh) sau khi tách từ qua `tools/_shared.py:terms()`.

**Khi nào dùng:** sau khi agent đã có nội dung text cụ thể (từ `lookup`,
`fetch`, `timeline`, `social_search`) và người dùng muốn biết cảm xúc/thái
độ chung của nội dung đó.

**Khi nào KHÔNG dùng:** không dùng để tìm kiếm hay lấy dữ liệu — đây không
phải tool tra cứu.

**Giới hạn đã biết:** đây là heuristic đếm từ khóa đơn giản (không dùng
model/API), dễ bị sai với câu phủ định ("không tốt") hoặc mỉa mai — phù hợp
cho mục đích học tập, không phải production-grade sentiment analysis.

**Input xấu:** nếu `text` không phải string (vd model truyền số/None/list),
tool bắt `TypeError` và trả về error dict thay vì raise.
