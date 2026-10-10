# Functional Design — U1 ConsumeData — Questions

Interaction mode: Guide me.

U1 nhận một message Kafka (một CIF), đọc 5 file excel, phân loại KHCN/KHDN, call
ECM mock lấy hồ sơ PDF, tạo file minh họa dòng tiền, dựng StrRecord phần input.
Dưới đây là các điểm cần làm rõ để thiết kế chức năng.

---

## Q1 — Cách xác định loại khách hàng (KHCN/KHDN)

- A. Dựa vào sự hiện diện file: có `ca_nhan_thuc_hien_giao_dich.xlsx` → KHCN; có
  `to_chuc_thuc_hien_giao_dich.xlsx` → KHDN (gợi ý)
- B. Dựa vào một cột cờ trong file thong_tin_dau_vao_bao_cao_str.xlsx
- C. Có mã số thuế (MASOTHUE) → KHDN, ngược lại KHCN
- X. Other (please specify)

[Answer]: A

---

## Q2 — Nguồn file sau khi nhận message (chỉ có CIF)

Message Kafka chỉ mang 1 CIF. Robot tìm file nguồn thế nào?

- A. Quét thư mục theo ngày hiện tại /Users/hainguyen/Projects/RPA/AMLD/YYYYMM/YYYYMMDD,
  tìm thư mục con khớp CIF (gợi ý)
- B. CIF trực tiếp là tên thư mục con cố định
- X. Other (please specify)

[Answer]:A

---

## Q3 — Mapping business_code ECM cho hồ sơ PDF

ECM có nhiều business_code (mb_smart_channel, customer_info_ca, ss_customer_doc,
ss_auto_upload_customer_info, customer_information, biz_onboarding). Lấy hồ sơ
thế nào?

- A. Thử lần lượt các business_code, gom tất cả file PDF trả về theo customerCode
  = CIF (gợi ý)
- B. Chỉ dùng một business_code cố định (mô tả)
- X. Other (please specify)

[Answer]: A

---

## Q4 — Phép tính dòng tiền (đã có công thức trong tài liệu US2)

Dùng công thức từ bang_ke_giao_dich_tai_khoan_dang_ngo.xlsx như tài liệu mô tả?

- A. Có — tiền vào (HUONG_GD=C): count distinct(TK_DOIUNG+TENKH_DOIUNG),
  count(MA_GD), sum(SOTIEN_GD_QD); tiền ra (HUONG_GD=D) tương tự (gợi ý)
- X. Other (please specify)

[Answer]: A

---

## Q5 — Khi thiếu file/lỗi ở U1

- A. Ghi lỗi vào StrRecord (BOT_ECM/BOT_GHICHU), đặt processingStopped=true, để
  U5 tổng hợp & gửi email (gợi ý, theo hợp đồng pipeline)
- X. Other (please specify)

[Answer]: A

---

## Q6 — Idempotency message trùng (cùng CIF/eventID)

- A. Chưa cần chống trùng ở phạm vi này; mỗi message xử lý độc lập (gợi ý — đơn giản)
- B. Chống trùng theo eventID (bỏ qua message đã xử lý)
- X. Other (please specify)

[Answer]: B.
