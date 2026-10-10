# Unit — Story Map

Mỗi hàng là một user story, gắn Unit (cấu phần pipeline) thực thi và thứ tự trong
Unit.

| Story | Unit ID | Directory | Thứ tự trong Unit |
|---|---|---|---|
| US1.1 — Nhận việc qua Kafka | U1 | u1-consume-data | 1 |
| US1.2 — Nhận diện thư mục nguồn theo ngày | U1 | u1-consume-data | 2 |
| US1.3 — Kiểm tra đủ file excel bắt buộc | U1 | u1-consume-data | 3 |
| US1.4 — Lấy hồ sơ KH qua ECM mock | U1 | u1-consume-data | 4 |
| US1.5 — Phân loại KHCN/KHDN | U1 | u1-consume-data | 5 |
| US2.1 — Tổng hợp sơ đồ dòng tiền | U1 | u1-consume-data | 6 |
| US2.2 — Tra cứu Accuity (mock) | U2 | u2-data-entry-accuity | 1 |
| US2.3 — Tra cứu Cục Thuế (KHDN) | U3 | u3-data-entry-tracuuthue | 1 |
| US3.1 — Đăng nhập AMLD Portal | U4 | u4-data-entry-amld | 1 |
| US3.2 — Nhập Mẫu số 01 đầy đủ | U4 | u4-data-entry-amld | 2 |
| US3.3 — Chặn giá trị tick ngoài định nghĩa | U4 | u4-data-entry-amld | 3 |
| US4.1 — Retry khi bước nhập lỗi | U4 | u4-data-entry-amld | 4 |
| US4.2 — Thông báo thất bại sau 3 lần retry | U5 | u5-tonghop-guimail | 2 |
| US4.3 — Cô lập lỗi theo khách hàng | U5 | u5-tonghop-guimail | 1 |
| US5.1 — Không hardcode secrets | U4 | u4-data-entry-amld | 5 |
| US5.2 — Lưu vết xử lý | U5 | u5-tonghop-guimail | 3 |
| US6.1 — Tổng hợp trạng thái lô | U5 | u5-tonghop-guimail | 4 |
| US6.2 — Gửi email trạng thái lô | U5 | u5-tonghop-guimail | 5 |

## Hàng cross-cutting

- **US5.1 (không hardcode secrets)** áp dụng cho mọi cấu phần gọi hệ thống ngoài
  (U1 ECM, U2 Accuity, U3 Cục Thuế, U4 AMLD, U5 mail). Ghi chính ở U4 nhưng là
  ràng buộc chung — mỗi adapter đọc credentials từ cấu hình/biến môi trường.
- **US4.3 (cô lập lỗi theo KH)** và **US6.1/US6.2** gom ở U5, dựa trên trạng thái
  trong `StrRecord` do các cấu phần trước ghi.

## Kiểm tra bao phủ

- Mọi story US1.1–US6.2 được gán Unit. Mọi Unit U1–U5 có hàng. Khớp
  traceability.json.
