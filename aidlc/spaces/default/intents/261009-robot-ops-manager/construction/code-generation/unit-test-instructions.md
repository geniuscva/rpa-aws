# Hướng dẫn kiểm thử — Ứng dụng quản lý vận hành robot

## Khung kiểm thử

- Framework: `pytest` (cấu hình trong `pyproject.toml`), API được kiểm thử bằng `fastapi.testclient.TestClient` (cần `httpx`).
- Cài đặt phụ thuộc: `python -m pip install -r requirements.txt`.
- Mỗi test dùng DB SQLite và thư mục log tạm (fixture trong `tests/conftest.py`), không đụng dữ liệu thật.

## Lệnh chạy (đúng phạm vi dự án này)

```
python -m pytest tests -q
```

Lệnh này chỉ chạy các test của ứng dụng trong thư mục `tests/` của workspace; chạy được ngay sau Step 2 của kế hoạch (trước khi có test đầu tiên sẽ báo "no tests ran", đó là trạng thái hợp lệ).

## Phạm vi kiểm thử (chiến lược Minimal)

Khoảng 14 test, mỗi yêu cầu có ít nhất một test và mỗi thành phần có test luồng thành công:

| File | Nội dung | Yêu cầu |
|---|---|---|
| `tests/test_db.py` | dữ liệu bền vững sau khi mở lại; run dở bị đánh dấu `stopped` khi khởi động lại | FR1.3, NFR3 |
| `tests/test_repository.py` | CRUD robot; trạng thái suy ra; phân trang lịch sử; xử lý cảnh báo | FR1, FR2.1, FR4.2, FR5.3 |
| `tests/test_runner.py` | chạy lệnh thành công và lỗi (`python -c`); chặn chạy trùng; dừng tiến trình; sai đường dẫn không làm sập ứng dụng; ghi log | FR3, FR4.1, FR4.3, FR5.1, NFR3 |
| `tests/test_scheduler.py` | robot trễ lịch > 5 phút tạo cảnh báo, không tạo trùng | FR5.2 |
| `tests/test_api.py` | luồng khai báo → chạy → lịch sử/log → cảnh báo → xử lý; dữ liệu sai trả 422; `/health`; mặc định bind `127.0.0.1` | FR1-FR5, NFR2, NFR4 |
| `tests/test_ui.py` | trang chủ phục vụ đúng, có bảng robot, nút Chạy/Dừng, khu cảnh báo, chu kỳ làm mới ≤ 5 giây | FR2.2 |

## Mục tiêu độ phủ

Không có ngưỡng độ phủ dòng cho phạm vi `express`; mục tiêu là mọi yêu cầu FR1-FR5 và NFR2-NFR5 có ít nhất một test đi qua.

## Mock/stub

- Robot giả là lệnh `python -c "..."` (thoát 0, thoát 1, ngủ dài để thử dừng); không chạy `run.bat` thật của folder nguồn.
- Thời gian (giờ lịch, "bây giờ") truyền vào hàm qua tham số để test không phụ thuộc đồng hồ.

## Dữ liệu kiểm thử

Tạo bằng fixture trong `conftest.py`; không dùng file dữ liệu cố định, không cần thiết lập thủ công.
