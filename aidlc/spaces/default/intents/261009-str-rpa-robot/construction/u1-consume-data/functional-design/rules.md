# Business Rules — U1 ConsumeData

Quy tắc nghiệp vụ của cấu phần U1. Mỗi quy tắc có id `BRx.y`.

## Source of truth

```yaml
rules:
  - id: BR1.1
    statement: Message Kafka phải hợp lệ mới xử lý.
    category: validation
    applies_to: KafkaStrEvent
    trigger: Khi nhận một message từ topic RPA_STR_NHNN_INPUT
    logic: >
      IF eventName != "LIST_CUST_STR" HOẶC thiếu cif/eventID/timeStamp
      THEN coi là message không hợp lệ.
    violation: Ghi log lỗi, bỏ qua message, không dừng consumer.
    source: FR1

  - id: BR1.2
    statement: Chống trùng message theo eventID.
    category: policy
    applies_to: KafkaStrEvent
    trigger: Trước khi xử lý một message hợp lệ
    logic: >
      IF eventID đã có trong ProcessedEvent THEN bỏ qua message (đã xử lý);
      ELSE xử lý và ghi eventID vào ProcessedEvent khi hoàn tất.
    violation: Bỏ qua message trùng, ghi log.
    source: FR1

  - id: BR1.3
    statement: Xác định loại khách hàng theo file hiện diện.
    category: calculation
    applies_to: CustomerSourceFolder
    trigger: Sau khi xác định thư mục CIF
    logic: >
      IF có ca_nhan_thuc_hien_giao_dich.xlsx THEN LOAIKHACHHANG = KHCN;
      ELSE IF có to_chuc_thuc_hien_giao_dich.xlsx THEN LOAIKHACHHANG = KHDN.
    violation: Nếu không có cả hai → thiếu file bắt buộc (BR1.4).
    source: FR4

  - id: BR1.4
    statement: Kiểm tra đủ file excel bắt buộc trong folder CIF.
    category: validation
    applies_to: CustomerSourceFolder
    trigger: Khi đọc thư mục CIF
    logic: >
      Bắt buộc có: (cá nhân HOẶC tổ chức), bang_ke_giao_dich_tai_khoan_dang_ngo.xlsx,
      thong_tin_giao_dich_dang_ngo.xlsx, thong_tin_dau_vao_bao_cao_str.xlsx.
      IF thiếu bất kỳ file nào THEN requiredFilesPresent=false và liệt kê missingFiles.
    violation: Ghi lỗi vào StrRecord, đặt processingStopped=true (BR1.7).
    source: FR3

  - id: BR1.5
    statement: Lấy hồ sơ PDF qua ECM mock, thử lần lượt các business_code.
    category: policy
    applies_to: CustomerDossier
    trigger: Sau khi file excel đủ
    logic: >
      Lấy token (client_credentials) → với mỗi business_code trong danh sách hỗ
      trợ, search theo customerCode = CIF → tải PDF theo doc_id trả về; gom tất cả
      PDF.
    violation: IF lỗi ECM hoặc không có hồ sơ bắt buộc THEN ghi BOT_ECM lỗi và
      processingStopped=true.
    source: FR14

  - id: BR1.6
    statement: Tính số liệu dòng tiền từ bảng kê.
    category: calculation
    applies_to: CashFlowDiagram
    trigger: Khi dựng sơ đồ dòng tiền
    logic: >
      Tiền vào (HUONG_GD=C): customerCount = count distinct(TK_DOIUNG+TENKH_DOIUNG);
      txnCount = count(MA_GD); amount = sum(SOTIEN_GD_QD).
      Tiền ra (HUONG_GD=D): tính tương tự. reportSubjectName = STR_TEN_KH.
    violation: Nếu bảng kê rỗng/sai định dạng → ghi lỗi, processingStopped=true.
    source: FR5

  - id: BR1.7
    statement: Lỗi tại U1 ghi vào StrRecord và dừng xử lý record (không ném exception).
    category: policy
    applies_to: StrRecord
    trigger: Khi gặp lỗi bất kỳ ở U1 (thiếu file, lỗi ECM, lỗi tính toán)
    logic: >
      IF lỗi THEN ghi BOT_ECM/BOT_GHICHU mô tả lỗi, đặt processingStopped=true;
      các cấu phần sau bỏ qua, chuyển thẳng tới U5 để tổng hợp & email.
    violation: N/A (đây là hành vi xử lý lỗi chuẩn).
    source: FR12

  - id: BR1.8
    statement: Xuất file minh họa dòng tiền.
    category: constraint
    applies_to: CashFlowDiagram
    trigger: Sau khi tính số liệu dòng tiền
    logic: Dựng và lưu file Minh Họa Dòng Tiền.pdf cho CIF.
    violation: Lỗi xuất file → ghi lỗi, processingStopped=true.
    source: FR5
```

## Tóm tắt quy tắc

| ID | Loại | Nội dung |
|---|---|---|
| BR1.1 | validation | Message Kafka hợp lệ mới xử lý |
| BR1.2 | policy | Chống trùng theo eventID |
| BR1.3 | calculation | Xác định KHCN/KHDN theo file |
| BR1.4 | validation | Kiểm đủ file bắt buộc |
| BR1.5 | policy | Lấy hồ sơ ECM thử nhiều business_code |
| BR1.6 | calculation | Tính dòng tiền theo công thức US2 |
| BR1.7 | policy | Lỗi ghi vào StrRecord, dừng record |
| BR1.8 | constraint | Xuất Minh Họa Dòng Tiền.pdf |
