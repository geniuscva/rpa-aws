# Hướng dẫn build — Ứng dụng quản lý vận hành robot

## Cài đặt phụ thuộc

```
python -m pip install -r requirements.txt
```

Yêu cầu Python 3.10 trở lên (đã chạy với Python 3.14.6).

## Thiết lập môi trường

Tất cả biến môi trường đều tuỳ chọn; mặc định chạy được ngay:

| Biến | Ý nghĩa | Mặc định |
|---|---|---|
| `ROBOT_OPS_DATA_DIR` | thư mục dữ liệu gốc | `data` |
| `ROBOT_OPS_DB` | đường dẫn file SQLite | `data/robot_ops.db` |
| `ROBOT_OPS_LOG_DIR` | thư mục log ứng dụng và log từng lần chạy | `data/logs` |
| `ROBOT_OPS_HOST` | địa chỉ lắng nghe | `127.0.0.1` |
| `ROBOT_OPS_PORT` | cổng | `8000` |

## Build

Ứng dụng Python không cần biên dịch. Kiểm tra chất lượng mã (bước "build" thực tế):

```
python -m ruff check .
```

## Xác nhận build

```
python -m pytest tests -q
```

Kỳ vọng: toàn bộ test pass (24 test). Chạy thử ứng dụng bằng `run_app.bat` rồi mở `http://127.0.0.1:8000`; `GET /health` phải trả `status: ok`.

## Xử lý sự cố thường gặp

- `ModuleNotFoundError: fastapi` — chưa cài phụ thuộc, chạy lại lệnh cài đặt ở trên.
- Cổng 8000 đang bận — đặt `ROBOT_OPS_PORT` sang cổng khác.
- Robot báo lỗi ngay khi bấm Chạy — kiểm tra thư mục làm việc và lệnh đã khai báo có tồn tại không (xem cảnh báo và log của lần chạy).
