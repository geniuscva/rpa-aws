# Requirements Analysis — Questions

Interaction mode: Guide me (walk through interactively).

Tài liệu US2 (docs/08_US2_TomTat.md) đã rất chi tiết về quy trình. Dưới đây là
những điểm còn chưa rõ, cần chốt trước khi viết requirements.

---

## Q1 — Ngôn ngữ & framework triển khai robot

Robot sẽ xây bằng công nghệ gì? Điều này quyết định cách tương tác với web portal.

- A. Python + Playwright/Selenium (điều khiển trình duyệt, xử lý excel/pdf tốt) (gợi ý)
- B. Python + nền tảng RPA chuyên dụng (UiPath/Power Automate) qua script
- C. Node.js/TypeScript + Playwright
- D. Chưa quyết — để giai đoạn thiết kế chọn
- X. Other (please specify)

[Answer]: A

---

## Q2 — Phạm vi bản dựng đầu tiên (lát cắt mỏng / walking skeleton)

Lát cắt end-to-end đầu tiên nên chứng minh điều gì? (Robot thật tương tác với 3 hệ thống ngoài, nên bản đầu có thể dùng mock.)

- A. Chạy khung đầy đủ nhưng dùng dữ liệu/portal giả lập (mock Accuity, Cục Thuế, AMLD) — chứng minh luồng đọc file → tổng hợp → nhập form chạy thông (gợi ý)
- B. Làm thật ngay với 1 hệ thống (ví dụ chỉ nhập AMLD Portal), các phần khác làm sau
- C. Chỉ làm khâu đọc & kiểm tra file + tổng hợp dòng tiền trước, chưa đụng web
- X. Other (please specify)

[Answer]: A

---

## Q3 — Nguồn dữ liệu đầu vào khi phát triển

Lúc phát triển/test, dữ liệu nguồn (5 file excel + PDF hồ sơ) lấy từ đâu?

- A. Có bộ file mẫu đặt sẵn trong repo (thư mục test fixtures) để robot đọc (gợi ý)
- B. Truy cập trực tiếp network share `\\10.1.18.197\tt35 share\QTRR\...` khi chạy thật
- C. Cả hai: fixtures cho test, network share cho chạy thật
- X. Other (please specify)

[Answer]: A

---

## Q4 — Môi trường chạy portal thật & credentials

Khi làm việc với AMLD Portal / Accuity / Cục Thuế thật: có môi trường test của NHNN không, hay chỉ có production?

- A. Chưa có môi trường test — chỉ mô phỏng/mock trong giai đoạn này, chạy thật do nghiệp vụ cung cấp credentials sau (gợi ý)
- B. Có môi trường test/sandbox của NHNN để robot thử
- C. Chạy thẳng production với credentials nghiệp vụ cấp
- X. Other (please specify)

[Answer]: X - mock web Accuity có trang login với user.pass và 1 nút export file Tra cứu thuế.pdf , AMLD và tra cứu thuế dùng web thực

---

## Q5 — Captcha ở Cục Thuế (bước tra cứu KHDN)

Tài liệu nói "Đọc & nhập mã xác nhận (captcha)" khi tra cứu Cục Thuế. Robot xử lý captcha thế nào?

- A. Tự đọc captcha bằng OCR; nếu fail thì bỏ qua bước Cục Thuế (coi như không có kết quả) (gợi ý)
- B. Dừng và yêu cầu người vận hành nhập captcha thủ công
- C. Dùng dịch vụ giải captcha bên thứ ba
- X. Other (please specify)

[Answer]: X dùng ddddocr framework

---

## Q6 — Chế độ xử lý lô & chạy định kỳ

Tài liệu nói "mỗi ngày 2 lượt quét folder". Robot chạy thế nào?

- A. Có bộ lịch tự quét 2 lần/ngày; cũng chạy được thủ công theo yêu cầu (gợi ý)
- B. Chỉ chạy thủ công khi người vận hành kích hoạt
- C. Chạy liên tục, phát hiện folder mới thì xử lý ngay
- X. Other (please specify)

[Answer]: X - chạy liên tục theo queue Kafka (robot là consumer, nhận message lô/KH cần xử lý thì xử lý ngay)

---

## Q7 — Robot dự phòng (failover)

Tài liệu nói "chuyển sang robot khác" sau 3 lần retry thất bại. Cơ chế này hiểu thế nào trong phạm vi dự án?

- A. Trong phạm vi hiện tại chỉ cần ghi nhận trạng thái "cần failover" + báo lỗi; việc có robot thứ 2 là hạ tầng vận hành, ngoài phạm vi code (gợi ý)
- B. Cần cài đặt đầy đủ 2 instance robot và cơ chế bàn giao công việc giữa chúng
- X. Other (please specify)

[Answer]: X - gửi mail thất bại sau 3 lần retry bằng mail exchange

---

## Q8 — Mục tiêu phạm vi dữ liệu khách hàng (KHCN vs KHDN)

Robot cần xử lý cả khách hàng cá nhân (KHCN) và tổ chức (KHDN) ngay từ đầu, hay ưu tiên một loại?

- A. Cả hai loại ngay từ đầu (tài liệu mô tả đầy đủ cả hai) (gợi ý)
- B. Ưu tiên KHCN trước, KHDN sau
- C. Ưu tiên KHDN trước, KHCN sau
- X. Other (please specify)

[Answer]: A
