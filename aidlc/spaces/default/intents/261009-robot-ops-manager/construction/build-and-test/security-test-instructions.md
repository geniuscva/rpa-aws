# Hướng dẫn kiểm thử bảo mật

Ứng dụng không có đăng nhập (ràng buộc C2), nên kiểm tra bảo mật tập trung vào việc giữ ứng dụng ở mạng cục bộ và chặn đầu vào xấu.

## Danh mục kiểm tra

| Kiểm tra | Cách chạy | Kỳ vọng |
|---|---|---|
| Mặc định chỉ lắng nghe `127.0.0.1` | `python -m pytest tests/test_api.py -q` | cấu hình mặc định là `127.0.0.1` |
| Dữ liệu khai báo robot sai bị từ chối | `python -m pytest tests/test_api.py -q` | trả 422 |
| Lệnh khởi động chỉ lấy từ robot đã khai báo | rà soát `robot_ops/runner.py` và `robot_ops/main.py` | API start/stop chỉ nhận `robot_id`, không nhận lệnh |
| Giao diện không chèn HTML từ dữ liệu người dùng | rà soát `robot_ops/static/index.html` | dùng `textContent` |
| Không có bí mật trong mã nguồn | tìm kiếm khoá/mật khẩu trong `robot_ops/` | không có |

## Rủi ro còn lại

Ai truy cập được cổng ứng dụng đều chạy/dừng được robot. Không đặt `ROBOT_OPS_HOST` thành `0.0.0.0` khi chưa thêm xác thực.
