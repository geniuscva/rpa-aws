# Business Rules — U2 DataEntryAccuity

Quy tắc nghiệp vụ của cấu phần U2. Mỗi quy tắc có id `BRx.y` (nhóm 2).

## Source of truth

```yaml
rules:
  - id: BR2.1
    statement: Bỏ qua record đã dừng xử lý.
    category: policy
    applies_to: StrRecord
    trigger: Khi U2 nhận StrRecord từ U1
    logic: >
      IF record.processingStopped = true THEN U2 không tra cứu, trả nguyên record
      cho cấu phần sau (U5 sẽ tổng hợp).
    violation: N/A (hành vi cô lập lỗi chuẩn của pipeline).
    source: FR12

  - id: BR2.2
    statement: Chọn Entity Type theo loại khách hàng.
    category: calculation
    applies_to: AccuityQuery
    trigger: Khi dựng yêu cầu tra cứu Accuity
    logic: >
      IF LOAIKHACHHANG = KHCN THEN entityType = Individual;
      ELSE IF LOAIKHACHHANG = KHDN THEN entityType = Organization.
      searchMode = Single; searchName = TENKHACHHANG.
    violation: Nếu TENKHACHHANG rỗng → ghi lỗi tra cứu (BR2.5).
    source: FR6

  - id: BR2.3
    statement: Đăng nhập Accuity và tra cứu, export PDF kết quả.
    category: policy
    applies_to: AccuityLookupResult
    trigger: Sau khi dựng AccuityQuery
    logic: >
      Đăng nhập web Accuity mock (credentials từ cấu hình) → chọn entityType +
      Single → nhập searchName → submit → export kết quả ra Tra cứu Accuity.pdf.
    violation: Lỗi đăng nhập/thao tác → BR2.5.
    source: FR6

  - id: BR2.4
    statement: Khi Match Score = 100 thì in thêm hồ sơ bản ghi.
    category: policy
    applies_to: AccuityLookupResult
    trigger: Sau khi có kết quả tra cứu
    logic: >
      IF matchScore = 100 THEN mở bản ghi khớp và print hồ sơ ra
      Tra cứu Accuity(n).pdf (n chạy theo số bản ghi).
    violation: Thiếu hồ sơ in khi matchScore=100 → ghi chú cảnh báo, không dừng.
    source: FR6

  - id: BR2.5
    statement: Lỗi tra cứu Accuity ghi vào StrRecord và dừng record.
    category: policy
    applies_to: StrRecord
    trigger: Khi đăng nhập/thao tác/export Accuity lỗi
    logic: >
      IF lỗi THEN ghi BOT_ACCUITY = lỗi (kèm địa chỉ web), ghi BOT_GHICHU mô tả,
      đặt processingStopped=true; chuyển thẳng tới U5.
    violation: N/A (đây là hành vi xử lý lỗi chuẩn).
    source: FR6

  - id: BR2.6
    statement: Ghi kết quả tra cứu thành công vào BOT_ACCUITY.
    category: constraint
    applies_to: StrRecord
    trigger: Khi tra cứu Accuity hoàn tất không lỗi
    logic: >
      Ghi BOT_ACCUITY = OK (kèm matchScore/đường dẫn PDF nếu cần), chuyển record
      cho U3.
    violation: N/A.
    source: FR6

  - id: BR2.7
    statement: Không hardcode credentials Accuity.
    category: constraint
    applies_to: AccuityQuery
    trigger: Khi đăng nhập Accuity
    logic: Credentials Accuity đọc từ cấu hình (data/config.yaml), không hardcode, không log.
    violation: Vi phạm bảo mật (NFR4) — không được phép.
    source: NFR4
```

## Tóm tắt quy tắc

| ID | Loại | Nội dung |
|---|---|---|
| BR2.1 | policy | Bỏ qua record đã dừng |
| BR2.2 | calculation | Entity Type theo loại KH |
| BR2.3 | policy | Đăng nhập + tra cứu + export PDF |
| BR2.4 | policy | Match Score 100 → in thêm hồ sơ |
| BR2.5 | policy | Lỗi tra cứu → dừng record |
| BR2.6 | constraint | Ghi BOT_ACCUITY khi thành công |
| BR2.7 | constraint | Không hardcode credentials Accuity |
