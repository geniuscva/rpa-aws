# Câu hỏi làm rõ yêu cầu — Ứng dụng quản lý vận hành robot

Ngữ cảnh: folder nguồn `D:/Code/RPA_Python/RPA_NHAPBAOCAO_STR` là một bộ robot RPA viết bằng Python (9 process trong `processes/`, ví dụ `STR_NHNN_ConsumeData_Enqueue`, `STR_NHNN_DataEntry_Accuity`, `STR_NHNN_Consume_SendMail`; thư viện `rpa-framework` và `mb-minibot`; mỗi process có `main.py`, `config/`, `run.bat`, `build.ps1`). Các câu hỏi dưới đây chốt phạm vi cho ứng dụng quản lý vận hành robot cần xây.

## Q1. Ứng dụng cần làm những việc gì với robot? (chọn tất cả những mục phù hợp)

Lý do hỏi: quyết định các chức năng bắt buộc (Must) của bản đầu tiên.

- A. Xem danh sách robot/process và trạng thái hiện tại (đang chạy, dừng, lỗi)
- B. Chạy hoặc dừng robot thủ công từ giao diện
- C. Xem lịch sử các lần chạy và log của từng robot
- D. Cảnh báo khi robot lỗi hoặc không chạy đúng lịch
- E. Xem/chỉnh cấu hình (`config/`) của từng robot
- X. Other (please specify)

[Answer]: A, B, C, D

## Q2. Ứng dụng chạy dưới dạng nào?

Lý do hỏi: quyết định công nghệ giao diện và cách người vận hành truy cập.

- A. Ứng dụng web chạy cục bộ (Python, mở bằng trình duyệt)
- B. Ứng dụng desktop Windows
- C. Công cụ dòng lệnh (CLI)
- X. Other (please specify)

[Answer]: A

## Q3. Danh sách robot và trạng thái lấy từ đâu?

Lý do hỏi: "sinh ra từ folder" có thể hiểu là tự quét folder, hoặc chỉ tái dùng thư viện/cấu trúc của folder đó.

- A. Tự quét folder `processes/` để phát hiện robot (mỗi thư mục con là một robot), trạng thái đọc từ log/file kết quả của robot
- B. Người dùng khai báo danh sách robot thủ công trong ứng dụng, ứng dụng tự lưu dữ liệu (SQLite)
- C. Kết hợp: tự quét để gợi ý danh sách, người dùng xác nhận và bổ sung
- X. Other (please specify)

[Answer]: B

## Q4. Ai dùng và có cần đăng nhập không?

Lý do hỏi: ảnh hưởng đến bảo mật khi cho phép chạy/dừng robot.

- A. Một người vận hành trên máy nội bộ, không cần đăng nhập
- B. Nhiều người, đăng nhập bằng tài khoản đơn giản trong ứng dụng (admin / chỉ xem)
- C. Đăng nhập theo tài khoản doanh nghiệp (AD/SSO)
- X. Other (please specify)

[Answer]: A

## Q5. Bản đầu tiên chạy ở đâu và robot được chạy bằng cách nào?

Lý do hỏi: quyết định cách ứng dụng khởi động robot (nếu có chức năng chạy/dừng).

- A. Cùng máy Windows với robot, khởi động robot bằng `run.bat` của từng process
- B. Chỉ theo dõi (đọc log/trạng thái), không khởi động robot
- C. Điều khiển qua hệ thống trung tâm có sẵn (Minibot Center)
- X. Other (please specify)

[Answer]: A
