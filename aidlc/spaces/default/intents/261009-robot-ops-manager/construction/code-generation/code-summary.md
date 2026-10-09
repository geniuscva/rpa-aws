# Tóm tắt Code Generation — Ứng dụng quản lý vận hành robot

## Tệp đã tạo

Mã nguồn (`robot_ops/`): `config.py`, `db.py`, `repository.py`, `runner.py`, `scheduler.py`, `main.py`, `__main__.py`, `static/index.html`, `__init__.py`.

Kiểm thử (`tests/`): `conftest.py`, `test_db.py`, `test_repository.py`, `test_runner.py`, `test_scheduler.py`, `test_api.py`, `test_ui.py`.

Gốc workspace: `requirements.txt`, `pyproject.toml`, `README.md`, `run_app.bat`; `.gitignore` được thêm dòng Python và `data/` (giữ nguyên khối AI-DLC).

## Quyết định triển khai chính

- Trạng thái robot lấy từ lần chạy gần nhất: `Đang chạy` / `Dừng` / `Lỗi`. Giao diện tự làm mới mỗi 3 giây (đáp ứng FR2.2, tối đa 5 giây).
- Lịch chạy là giờ cố định mỗi ngày dạng `HH:MM` (chốt câu hỏi mở trong requirements). Cảnh báo trễ lịch chỉ tạo một lần mỗi ngày cho mỗi robot.
- Dừng robot: `taskkill /PID <pid> /T /F` trên Windows, `killpg` ở nơi khác; dừng thủ công không tạo cảnh báo.
- Lỗi khởi động (sai thư mục/lệnh): API trả 400, ghi một run `error`, tạo cảnh báo, tăng `start_failures` hiển thị ở `/health`; ứng dụng không sập.
- Khi ứng dụng tắt, mọi robot đang chạy bị dừng; khi khởi động lại các run dở được đánh dấu `Bị dừng` (NFR3).
- Xoá robot đang chạy trả 409. Lệnh khởi động chỉ lấy từ robot đã khai báo (NFR2). Mặc định bind `127.0.0.1`.
- Giao diện dựng DOM bằng `textContent` để tránh XSS.

## Tóm tắt kiểm thử

`python -m pytest tests -q`: 23 passed, 1 warning (deprecation của Starlette/httpx, không ảnh hưởng). `ruff check .`: All checks passed. Đã chạy thử server thật: `/health` và `/` trả 200 và chỉ lắng nghe `127.0.0.1`. JavaScript của giao diện mới chỉ được kiểm tra qua test HTML tĩnh, chưa mở bằng trình duyệt.

## Sai lệch so với kế hoạch

- Có 23 test thay vì khoảng 14 (tách theo luồng và biên lỗi); mọi FR1-FR5 và NFR2-NFR5 đều có test.
- `pyproject.toml` đặt `target-version = "py310"` thay vì 3.13 (C5) để tương thích rộng; máy hiện dùng Python 3.14.
- Log robot đọc bằng UTF-8; output `run.bat` theo codepage OEM có thể sai dấu tiếng Việt.
- Developer từng ghi đè `.gitignore` do nhầm và đã khôi phục từ `git show HEAD:.gitignore` rồi thêm dòng mới (chỉ 7 dòng thêm).
- NFR1 (trang tải dưới 2 giây với 50 robot/10.000 bản ghi) chưa có phép đo riêng; phân trang lịch sử được kiểm thử, hiệu năng sẽ kiểm tra ở Build and Test.
