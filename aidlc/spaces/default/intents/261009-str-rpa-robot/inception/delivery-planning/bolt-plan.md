# Bolt Plan — Robot RPA nhập liệu STR

Một **Bolt** là một lượt build trên một phần công việc, kết thúc bằng thứ gì đó
chạy được và kiểm chứng được. Pipeline tuyến tính nên mỗi Unit là một Bolt, thi
công đúng thứ tự DAG U1 → U2 → U3 → U4 → U5.

Runtime thực thi tuần tự (pipeline phụ thuộc tuyến tính). Phát triển/test có thể
song song: nhờ hợp đồng `StrRecord`, mỗi cấu phần code/test độc lập bằng
`StrRecord` giả, rồi ghép lại.

Không có walking skeleton riêng (theo quyết định ở Units Generation).

## Bolt 1 — U1 ConsumeData

- **Units:** U1 (u1-consume-data).
- **Definition of Done:** nhận message Kafka (một CIF), đọc 5 file excel, phân
  loại KHCN/KHDN, call ECM mock lấy hồ sơ PDF, tạo `Minh Họa Dòng Tiền.pdf`, dựng
  `StrRecord` phần input; test xanh.
- **Confidence hypothesis:** chứng minh khâu input (Kafka → excel → ECM → dòng
  tiền → StrRecord) chạy thông và tạo đúng dữ liệu.
- **Demo mong đợi:** đẩy một message vào topic, robot tạo được `StrRecord` + file
  dòng tiền cho một CIF.

## Bolt 2 — U2 DataEntryAccuity

- **Units:** U2 (u2-data-entry-accuity).
- **Definition of Done:** đăng nhập Accuity mock, tra cứu theo tên KH, xuất
  `Tra cứu Accuity.pdf`, cập nhật BOT_ACCUITY vào `StrRecord`; test xanh.
- **Confidence hypothesis:** chứng minh tự động hóa web (dù là mock) chạy được và
  bồi đắp đúng `StrRecord`.
- **Demo mong đợi:** với một `StrRecord` đầu vào, xuất được file Accuity.pdf.

## Bolt 3 — U3 DataEntryTraCuuThue

- **Units:** U3 (u3-data-entry-tracuuthue).
- **Definition of Done:** với KHDN, mở web Cục Thuế thật, nhập MST, giải captcha
  ddddocr, xuất PDF tra cứu, cập nhật BOT_TRACUUTHE; KHCN thì bỏ qua; test xanh.
- **Confidence hypothesis:** chứng minh giải được captcha và tương tác web thật
  Cục Thuế — một trong hai điểm rủi ro cao nhất.
- **Demo mong đợi:** với một KHDN, lấy được thông tin thuế hoặc xử lý đúng khi
  không có kết quả.

## Bolt 4 — U4 DataEntryAMLD

- **Units:** U4 (u4-data-entry-amld).
- **Definition of Done:** đăng nhập AMLD thật, nhập Phần I/II/IV/V/VI (bỏ III),
  rẽ nhánh KHCN/KHDN, chặn giá trị tick ngoài định nghĩa, đính kèm Phần VI, retry
  ≤ 3, cập nhật trạng thái vào `StrRecord`; test xanh.
- **Confidence hypothesis:** chứng minh nhập được báo cáo đầy đủ lên portal thật
  — điểm rủi ro cao nhất và phức tạp nhất.
- **Demo mong đợi:** một báo cáo nhập đủ các Phần cho một CIF.

## Bolt 5 — U5 TongHopVaGuiMail

- **Units:** U5 (u5-tonghop-guimail).
- **Definition of Done:** tổng hợp `StrRecord` các CIF, dựng file excel trạng
  thái, gửi email qua mail exchange (To người lập, Cc nguyendinhhai1996@hotmail.com),
  gồm email báo thất bại sau 3 lần retry; test xanh.
- **Confidence hypothesis:** chứng minh khâu tổng hợp & thông báo end-to-end hoạt
  động và khép kín pipeline.
- **Demo mong đợi:** sau khi xử lý vài CIF, nhận được email trạng thái kèm file.

## Thứ tự rủi ro

Rủi ro cao nhất là tương tác web thật (U3 Cục Thuế/captcha, U4 AMLD). Thứ tự DAG
đã đặt chúng ở giữa pipeline; khi vào Construction nên dành nhiều chú ý và test
cho U3/U4.
