# Yêu cầu — Ứng dụng quản lý vận hành robot

## Phân tích ý định

Người dùng cần một ứng dụng đơn giản để quản lý vận hành các robot RPA, được sinh ra từ folder `D:/Code/RPA_Python/RPA_NHAPBAOCAO_STR` (bộ robot Python gồm 9 process trong `processes/`, mỗi process có `main.py`, `config/`, `run.bat`; dùng thư viện `rpa-framework` và `mb-minibot`). Mục tiêu: một người vận hành có thể khai báo robot, bấm chạy/dừng, xem trạng thái, lịch sử, log và nhận cảnh báo khi robot lỗi, tại một nơi duy nhất thay vì mở từng process bằng tay. [desc] [Q1]

Độ sâu: Minimal (phạm vi hẹp, yêu cầu đã rõ sau 5 câu hỏi).

## Yêu cầu chức năng

- **FR1 — Quản lý danh sách robot** [Q3]
  - FR1.1: Hệ thống cho phép người dùng khai báo một robot gồm: tên, đường dẫn thư mục làm việc, lệnh khởi động (ví dụ `run.bat` của process), lịch chạy dự kiến (tuỳ chọn).
  - FR1.2: Hệ thống cho phép sửa và xoá robot đã khai báo.
  - FR1.3: Dữ liệu robot được lưu bền vững (SQLite) và còn nguyên sau khi khởi động lại ứng dụng.
- **FR2 — Xem trạng thái** [Q1-A]
  - FR2.1: Trang danh sách hiển thị mỗi robot cùng trạng thái hiện tại: `Đang chạy`, `Dừng`, `Lỗi`.
  - FR2.2: Trạng thái được cập nhật tự động trên giao diện không cần tải lại trang thủ công, với độ trễ tối đa 5 giây.
- **FR3 — Chạy/dừng thủ công** [Q1-B, Q5-A]
  - FR3.1: Người dùng bấm "Chạy" để khởi động robot bằng lệnh đã khai báo, trên cùng máy Windows chạy ứng dụng.
  - FR3.2: Người dùng bấm "Dừng" để kết thúc tiến trình robot đang chạy (kể cả tiến trình con).
  - FR3.3: Hệ thống không cho chạy một robot đang ở trạng thái `Đang chạy` (hiển thị thông báo rõ ràng).
- **FR4 — Lịch sử chạy và log** [Q1-C]
  - FR4.1: Mỗi lần chạy được ghi lại: thời điểm bắt đầu, kết thúc, kết quả (thành công/lỗi/bị dừng), mã thoát.
  - FR4.2: Người dùng xem lịch sử các lần chạy của từng robot, mới nhất trước, có phân trang.
  - FR4.3: Người dùng xem nội dung log (stdout/stderr) của một lần chạy.
- **FR5 — Cảnh báo** [Q1-D]
  - FR5.1: Khi một lần chạy kết thúc với lỗi (mã thoát khác 0), hệ thống tạo cảnh báo hiển thị trên giao diện.
  - FR5.2: Khi robot có lịch chạy dự kiến mà không bắt đầu trong vòng 5 phút sau giờ lịch, hệ thống tạo cảnh báo "không chạy đúng lịch".
  - FR5.3: Người dùng đánh dấu một cảnh báo là đã xử lý.

## Yêu cầu phi chức năng

- **NFR1 — Hiệu năng:** Trang danh sách tải trong dưới 2 giây với tối đa 50 robot và 10.000 bản ghi lịch sử trên máy phát triển thông thường.
- **NFR2 — Bảo mật:** Ứng dụng không có đăng nhập (xem Ràng buộc), vì vậy chỉ lắng nghe trên `127.0.0.1` theo mặc định; lệnh khởi động chỉ lấy từ robot đã khai báo, không nhận lệnh tuỳ ý từ yêu cầu chạy; dữ liệu nhập được kiểm tra hợp lệ ở biên hệ thống; không lưu mật khẩu/khoá bí mật trong mã nguồn.
- **NFR3 — Độ tin cậy:** Khi ứng dụng khởi động lại, các lần chạy đang dở trước đó được đánh dấu là `Bị dừng` (không để trạng thái `Đang chạy` sai). Lỗi khởi động robot (sai đường dẫn, thiếu file) hiển thị thông báo, không làm sập ứng dụng.
- **NFR4 — Khả năng quan sát:** Ứng dụng ghi log của chính nó ra file, kèm ít nhất một chỉ số sức khoẻ (endpoint `/health`) và số lỗi khởi động robot.
- **NFR5 — Khả năng bảo trì/kiểm thử:** Có kiểm thử tự động cho mỗi yêu cầu chức năng (ít nhất một luồng thành công cho mỗi thành phần) và chạy được bằng `pytest` không cần cài đặt thủ công ngoài `requirements.txt`.

## Ràng buộc

- **C1:** Ứng dụng web chạy cục bộ, viết bằng Python, mở bằng trình duyệt. [Q2-A]
- **C2:** Không cần đăng nhập; một nhóm người dùng nội bộ truy cập như nhau. [Q4-A, theo chỉnh sửa của người dùng]
- **C3:** Chạy cùng máy Windows với robot; robot khởi động bằng lệnh như `run.bat`. [Q5-A]
- **C4:** Dữ liệu lưu bằng SQLite, không phụ thuộc hệ thống ngoài. [Q3-B]
- **C5:** Phong cách mã theo cấu hình của folder nguồn: Ruff, độ dài dòng 100, Python 3.13 (từ `pyproject.toml` của folder nguồn). [assumption]

## Giả định

- **A1:** "Sinh ra từ folder nguồn" nghĩa là dùng folder đó làm bộ robot mẫu và tham chiếu cấu trúc (thư mục `processes/<tên>/` có `run.bat`); ứng dụng mới là dự án độc lập, không sửa đổi folder nguồn. Cơ sở: người dùng chọn khai báo robot thủ công (Q3-B) thay vì tự quét. [assumption]
- **A2:** Một robot chạy tối đa một tiến trình tại một thời điểm. [assumption]
- **A3:** Người dùng chấp nhận rủi ro không có xác thực vì ứng dụng chỉ mở trên máy cục bộ (NFR2). Nếu cần truy cập từ máy khác, phải bổ sung xác thực trước. [assumption]
- **A4:** Tiến trình robot trạng thái `Lỗi` được xác định bằng mã thoát khác 0; robot không cần tích hợp thêm với `mb-minibot` hay Minibot Center ở bản đầu. [assumption]

## Ngoài phạm vi

- Đăng nhập, phân quyền, AD/SSO.
- Tự động quét folder `processes/` để phát hiện robot.
- Xem/chỉnh sửa file cấu hình `config/` của robot (không được chọn ở Q1).
- Điều khiển qua Minibot Center hoặc chạy robot trên máy từ xa.
- Gửi cảnh báo qua email/Teams (cảnh báo chỉ hiển thị trên giao diện).
- Triển khai lên AWS hoặc môi trường sản xuất.

## Câu hỏi mở

- Lịch chạy dự kiến (FR1.1) dùng định dạng nào (cron hay giờ cố định mỗi ngày)? Đề xuất: giờ cố định mỗi ngày ở bản đầu; chốt ở giai đoạn thiết kế.

## Sources

- [desc] Initial description: tôi cần xây 1 ứng dụng đơn giản quản lý vận hành robot, đc sinh ra từ folder D:/Code/RPA_Python/RPA_NHAPBAOCAO_STR
- [scope] Workflow-selected scope: express
- [Q1] Chức năng: A, B, C, D
- [Q2] Dạng ứng dụng: web cục bộ
- [Q3] Khai báo robot thủ công
- [Q4] Không cần đăng nhập (người dùng chỉnh lại sau câu trả lời đầu)
- [Q5] Khởi động bằng `run.bat` cục bộ

## Assumptions & Open Questions

- Xem mục Giả định (A1-A4) và Câu hỏi mở ở trên.
