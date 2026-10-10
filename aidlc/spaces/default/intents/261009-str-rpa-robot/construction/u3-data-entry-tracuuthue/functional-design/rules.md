# Business Rules — U3 DataEntryTraCuuThue

Quy tắc nghiệp vụ của cấu phần U3. Mỗi quy tắc có id `BRx.y` (nhóm 3).

## Source of truth

```yaml
rules:
  - id: BR3.1
    statement: Bỏ qua record đã dừng xử lý.
    category: policy
    applies_to: StrRecord
    trigger: Khi U3 nhận StrRecord từ U1
    logic: >
      IF record.processingStopped = true THEN U3 không tra cứu, trả nguyên record
      cho cấu phần sau.
    violation: N/A (hành vi cô lập lỗi chuẩn của pipeline).
    source: FR12

  - id: BR3.2
    statement: Chỉ tra cứu Cục Thuế khi khách hàng là KHDN.
    category: policy
    applies_to: TaxLookupQuery
    trigger: Trước khi tra cứu Cục Thuế
    logic: >
      IF LOAIKHACHHANG = KHCN THEN bỏ qua tra cứu, ghi BOT_TRACUUTHE = SKIPPED;
      ELSE IF LOAIKHACHHANG = KHDN THEN dựng query với taxCode = MASOTHUE.
    violation: Nếu KHDN mà MASOTHUE rỗng → ghi lỗi tra cứu (BR3.6).
    source: FR7.1

  - id: BR3.3
    statement: Nhập mã số thuế và giải captcha bằng ddddocr.
    category: policy
    applies_to: Captcha
    trigger: Khi mở trang tra cứu người nộp thuế (KHDN)
    logic: >
      Mở web Cục Thuế → nhập taxCode → lấy ảnh captcha → giải bằng ddddocr →
      nhập chuỗi captcha → submit. Giải sai thì thử lại trong giới hạn số lần.
    violation: Vượt giới hạn giải captcha hoặc lỗi thao tác → BR3.6.
    source: FR7.2, FR7.3

  - id: BR3.4
    statement: In PDF khi có kết quả; bỏ qua khi không có.
    category: policy
    applies_to: TaxLookupResult
    trigger: Sau khi submit tra cứu
    logic: >
      IF có kết quả THEN print Tra cứu tình trạng người nộp thuế.pdf và
      BOT_TRACUUTHE = OK; ELSE IF không có kết quả THEN BOT_TRACUUTHE = SKIPPED
      (bỏ qua in PDF, không coi là lỗi).
    violation: N/A.
    source: FR7.4

  - id: BR3.5
    statement: Ghi kết quả tra cứu vào BOT_TRACUUTHE.
    category: constraint
    applies_to: StrRecord
    trigger: Khi tra cứu Cục Thuế hoàn tất
    logic: Ghi BOT_TRACUUTHE (OK/SKIPPED), chuyển record cho U4.
    violation: N/A.
    source: FR7

  - id: BR3.6
    statement: Lỗi tra cứu Cục Thuế ghi vào StrRecord và dừng record.
    category: policy
    applies_to: StrRecord
    trigger: Khi tra cứu lỗi (timeout, captcha fail vượt giới hạn, lỗi robot)
    logic: >
      IF lỗi THEN ghi BOT_TRACUUTHE = lỗi, ghi BOT_GHICHU mô tả, đặt
      processingStopped=true; chuyển thẳng tới U5.
    violation: N/A (đây là hành vi xử lý lỗi chuẩn).
    source: FR7.5

  - id: BR3.7
    statement: Không hardcode credentials/endpoint Cục Thuế.
    category: constraint
    applies_to: TaxLookupQuery
    trigger: Khi truy cập web Cục Thuế
    logic: URL/cấu hình Cục Thuế đọc từ data/config.yaml, không hardcode, không log secret.
    violation: Vi phạm bảo mật (NFR4) — không được phép.
    source: NFR4
```

## Tóm tắt quy tắc

| ID | Loại | Nội dung |
|---|---|---|
| BR3.1 | policy | Bỏ qua record đã dừng |
| BR3.2 | policy | Chỉ tra cứu khi KHDN |
| BR3.3 | policy | Nhập MST + giải captcha ddddocr |
| BR3.4 | policy | Có kết quả → in PDF; không có → bỏ qua |
| BR3.5 | constraint | Ghi BOT_TRACUUTHE |
| BR3.6 | policy | Lỗi tra cứu → dừng record |
| BR3.7 | constraint | Không hardcode credentials Cục Thuế |
