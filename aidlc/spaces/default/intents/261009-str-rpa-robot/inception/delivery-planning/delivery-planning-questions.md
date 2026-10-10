# Delivery Planning — Questions

Interaction mode: Guide me.

Pipeline tuyến tính U1→U2→U3→U4→U5 (không walking skeleton riêng). DAG gần như ép
thứ tự thi công. Dưới đây là các điểm cần chốt.

---

## Q1 — Thứ tự thi công (Bolt sequence)

Một Bolt là một lượt build trên một phần công việc, kết thúc bằng thứ gì đó chạy
được. Chuỗi phụ thuộc là tuyến tính nên thứ tự tự nhiên theo DAG.

- A. Mỗi Unit là một Bolt, thi công đúng thứ tự U1 → U2 → U3 → U4 → U5 (gợi ý)
- B. Gộp vài Unit thành một Bolt
- X. Other (please specify)

[Answer]:A

---

## Q2 — Chạy tuần tự hay song song các Bolt

- A. Tuần tự (do pipeline phụ thuộc tuyến tính) (gợi ý)
- B. Song song khi có thể
- X. Other (please specify)

[Answer]:B

---

## Q3 — Điều gì đáng lo nhất (ưu tiên xử lý sớm)

Rủi ro lớn nhất của bản build này là gì?

- A. Tương tác web thật (AMLD/Cục Thuế) dễ vỡ selector/captcha — rủi ro cao nhất,
  nằm ở U3/U4 (gợi ý)
- B. Đọc & tổng hợp dữ liệu excel/dòng tiền (U1)
- C. Tích hợp Kafka/ECM mock (U1)
- X. Other (please specify)

[Answer]:A

---

## Q4 — Cách chạy Construction (iteration)

Thứ tự chạy các giai đoạn Construction cho các Unit:

- A. Unit-major: làm xong trọn vẹn từng Unit (thiết kế + code + kiểm) rồi mới
  sang Unit kế — mặc định, có checkpoint cuối mỗi Unit (gợi ý)
- B. Stage-major: chạy từng giai đoạn cho tất cả Unit trước
- X. Other (please specify)

[Answer]: A

---

## Q5 — Cách staff Construction

- A. Tôi (một phiên làm việc) chạy toàn bộ Construction theo cấu hình đã chọn
  (gợi ý — phù hợp dự án solo, chạy local)
- B. Mỗi team sở hữu một Unit và tự duyệt
- X. Other (please specify)

[Answer]:A
