# Hướng dẫn kiểm thử tích hợp

Chiến lược Minimal không yêu cầu bộ kiểm thử tích hợp riêng. Luồng tích hợp chính (khai báo robot → chạy → xem lịch sử/log → cảnh báo → xử lý) đã được kiểm thử bằng `tests/test_api.py` với robot giả `python -c`.

## Cách chạy

```
python -m pytest tests/test_api.py -q
```

## Kiểm thử thủ công với robot thật

1. Chạy `run_app.bat`, mở `http://127.0.0.1:8000`.
2. Khai báo một robot từ folder nguồn, ví dụ thư mục làm việc `D:/Code/RPA_Python/RPA_NHAPBAOCAO_STR/processes/<tên process>` và lệnh `run.bat`.
3. Bấm Chạy, xem trạng thái đổi sang `Đang chạy`, bấm Dừng và kiểm tra tiến trình con đã tắt (Task Manager).

Cảnh báo: robot thật có thể thao tác trên hệ thống nghiệp vụ; chỉ thử trên robot an toàn.
