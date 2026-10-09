# Robot Ops — Ứng dụng quản lý vận hành robot

Ứng dụng web chạy cục bộ (FastAPI + SQLite + một trang HTML) để khai báo robot RPA, bấm Chạy/Dừng,
theo dõi trạng thái, xem lịch sử chạy, log và cảnh báo. Dùng cho bộ robot mẫu
`D:/Code/RPA_Python/RPA_NHAPBAOCAO_STR` (mỗi process trong `processes/<tên>/` có `run.bat`).

> **Cảnh báo bảo mật:** ứng dụng **không có đăng nhập**. Mặc định chỉ lắng nghe trên `127.0.0.1`
> (chỉ truy cập được từ chính máy này). Không đặt `ROBOT_OPS_HOST` thành `0.0.0.0` hay địa chỉ mạng
> nếu chưa bổ sung xác thực — bất kỳ ai truy cập được sẽ chạy được các lệnh đã khai báo.

## Cài đặt

Yêu cầu Python 3.10 trở lên (đã thử trên 3.14).

```
python -m pip install -r requirements.txt
```

## Chạy ứng dụng

```
run_app.bat
```

hoặc `python -m robot_ops`, rồi mở <http://127.0.0.1:8000>.

Biến môi trường (tuỳ chọn):

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `ROBOT_OPS_DATA_DIR` | `data` | Thư mục dữ liệu |
| `ROBOT_OPS_DB` | `<data>/robot_ops.db` | File SQLite |
| `ROBOT_OPS_LOG_DIR` | `<data>/logs` | Log ứng dụng (`app.log`) và log từng lần chạy (`runs/run_<id>.log`) |
| `ROBOT_OPS_HOST` | `127.0.0.1` | Địa chỉ lắng nghe |
| `ROBOT_OPS_PORT` | `8000` | Cổng |

## Khai báo robot từ folder `RPA_NHAPBAOCAO_STR`

Trong mục "Khai báo robot" nhập:

- **Tên robot**: ví dụ tên process.
- **Thư mục làm việc**: ví dụ `D:/Code/RPA_Python/RPA_NHAPBAOCAO_STR/processes/<tên process>`.
- **Lệnh khởi động**: ví dụ `run.bat`.
- **Lịch chạy** (tuỳ chọn): giờ cố định mỗi ngày dạng `HH:MM`, ví dụ `08:00`. Nếu robot không bắt đầu
  chạy trong vòng 5 phút sau giờ này, hệ thống tạo cảnh báo "Không chạy đúng lịch".

Ứng dụng không sửa gì trong folder nguồn; lệnh chỉ lấy từ robot đã khai báo, không nhận lệnh tuỳ ý
từ yêu cầu chạy.

## Tính năng

- Danh sách robot với trạng thái `Đang chạy` / `Dừng` / `Lỗi`, tự làm mới mỗi 3 giây.
- Chạy (chặn chạy trùng) và Dừng (kết thúc cả cây tiến trình, dùng `taskkill /T /F` trên Windows).
- Lịch sử chạy phân trang (mới nhất trước) và xem log stdout/stderr của từng lần chạy.
- Cảnh báo khi robot kết thúc với mã thoát khác 0 hoặc không chạy đúng lịch; nút "Đã xử lý".
- Khi ứng dụng khởi động lại, các lần chạy đang dở được đánh dấu `Bị dừng`.
- `GET /health` trả về tình trạng ứng dụng và số lỗi khởi động robot.

## API chính

`GET/POST /api/robots`, `GET/PUT/DELETE /api/robots/{id}`, `POST /api/robots/{id}/start|stop`,
`GET /api/robots/{id}/runs?page=&page_size=`, `GET /api/runs/{id}/log`, `GET /api/alerts`,
`POST /api/alerts/{id}/resolve`, `GET /health`. Tài liệu tương tác tại `/docs`.

## Kiểm thử và kiểm tra mã

```
python -m pytest tests -q
python -m ruff check .
```

## Cấu trúc

```
robot_ops/   config.py, db.py, repository.py, runner.py, scheduler.py, main.py, static/index.html
tests/       test_db, test_repository, test_runner, test_scheduler, test_api, test_ui
run_app.bat  khởi động ứng dụng
```
