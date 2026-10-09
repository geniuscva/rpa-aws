# Hướng dẫn kiểm thử hiệu năng

Mục tiêu duy nhất: NFR1 — danh sách robot và lịch sử chạy tải trong dưới 2 giây với 50 robot và 10.000 bản ghi lịch sử.

## Cách chạy

```
python -m pytest tests/test_performance.py -q
```

Test nạp 50 robot × 200 lần chạy bằng chèn hàng loạt trong một transaction rồi đo thời gian `GET /api/robots` và `GET /api/robots/1/runs`. Ngưỡng 2 giây không được nới lỏng.

## Kết quả

Đã đạt (xem `build-and-test-summary.md`, ma trận mục tiêu).
