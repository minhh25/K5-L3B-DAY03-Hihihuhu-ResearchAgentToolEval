---
name: filter_sources
track: core
kind: local_formatter
provider: local_python
requires_env: []
inputs: [items, include_domains, exclude_domains, min_score, limit]
outputs: [items, input_count, kept_count, removed_count, error, message]
side_effect: false
---
# filter_sources

Lọc nguồn đã có trong hội thoại/kết quả research. Không tìm kiếm hoặc truy cập URL.
`items` tối đa 1000 object, URL HTTP(S); URL thiếu/sai, credentials trong URL hoặc
score sai được loại. Chuẩn hóa hostname, cổng mặc định; bỏ fragment, utm_*, fbclid,
gclid; giữ query khác. Không gộp HTTP và HTTPS. Giữ thứ tự và bản đầu tiên sau lọc.

`include_domains` / `exclude_domains`: hostname, gồm cả subdomain, exclude ưu tiên.
Không match `evilexample.com` cho `example.com`. `min_score` [0,1], thiếu score = 0;
`limit` số nguyên [0,1000], 0 trả rỗng. Sai kiểu tiêu chí/collection trả error dict.
Không sửa input. `removed_count` gồm cả URL sai, lọc, trùng và vượt limit.
Không đánh giá độ tin cậy nội dung; hostname/score chỉ là tiêu chí người dùng chọn.
