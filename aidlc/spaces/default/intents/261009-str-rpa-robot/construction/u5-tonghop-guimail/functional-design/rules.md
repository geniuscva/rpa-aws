# Business Rules — U5 TongHopVaGuiMail

Quy tắc nghiệp vụ của cấu phần U5. Mỗi quy tắc có id `BRx.y` (nhóm 5).

## Source of truth

```yaml
rules:
  - id: BR5.1
    statement: Tổng hợp trạng thái mọi CIF trong lô (gồm cả KH lỗi).
    category: policy
    applies_to: ProcessingResult
    trigger: Khi lô đã xử lý xong (mọi CIF đã qua U1–U4 hoặc dừng luồng)
    logic: >
      Với mỗi StrRecord trong lô, dựng một ProcessingResult: status = FAIL khi
      processingStopped = true hoặc có BOT_* lỗi, ngược lại SUCCESS; lấy errorCode
      và errorDetail từ BOT_GHICHU. KH lỗi dừng luồng vẫn có một hàng (cô lập lỗi).
    violation: N/A.
    source: FR12.1, FR12.2

  - id: BR5.2
    statement: Dựng bảng trạng thái lô đúng cột.
    category: constraint
    applies_to: BatchStatusReport
    trigger: Sau khi dựng xong các ProcessingResult
    logic: >
      Dựng file excel trạng thái với các cột: STT, STR_CIF, Trạng thái, Mã lỗi,
      Chi tiết lỗi. Mỗi hàng là một ProcessingResult theo thứ tự STT.
    violation: Thiếu cột bắt buộc → file trạng thái không hợp lệ.
    source: FR12.1, FR13.1

  - id: BR5.3
    statement: Gửi một email trạng thái lô kèm file đính kèm.
    category: policy
    applies_to: StatusEmail
    trigger: Sau khi dựng BatchStatusReport
    logic: >
      Gửi email qua mail exchange: From = nguyendinhhai1996@hotmail.com, To =
      EMAIL_NGUOI_LAP_BAO_CAO (người lập), Cc = nguyendinhhai1996@hotmail.com (và
      các Cc bổ sung nếu cấu hình), đính kèm file excel trạng thái, tiêu đề/nội
      dung theo template mục 5.4.
    violation: Không gửi được email → ghi log lỗi gửi, không làm hỏng trạng thái đã dựng.
    source: FR13.1, FR13.2

  - id: BR5.4
    statement: Email báo thất bại cho KH lỗi sau 3 lần retry nằm trong email lô.
    category: policy
    applies_to: ProcessingResult
    trigger: Khi một CIF có BOT_* lỗi do vẫn thất bại sau 3 lần retry (từ U4) hoặc lỗi dừng luồng khác
    logic: >
      KH thất bại sau 3 lần retry được đánh dấu status = FAIL với errorCode/
      errorDetail; thông tin thất bại nằm trong bảng trạng thái của email lô (không
      có cơ chế robot thứ hai trong phạm vi code này).
    violation: N/A.
    source: FR11.2, FR13

  - id: BR5.5
    statement: Cô lập lỗi theo khách hàng — một KH lỗi không chặn tổng hợp lô.
    category: policy
    applies_to: ProcessingResult
    trigger: Khi tổng hợp lô có cả KH thành công và KH lỗi
    logic: >
      Lỗi của một CIF chỉ làm hàng đó status = FAIL; các CIF khác vẫn được tổng
      hợp và email lô vẫn được gửi với đầy đủ các hàng.
    violation: N/A (hành vi cô lập lỗi chuẩn).
    source: FR12.2

  - id: BR5.6
    statement: Lưu vết xử lý từng bước theo KH.
    category: constraint
    applies_to: ProcessingResult
    trigger: Trong suốt quá trình xử lý từng CIF (ghi bởi các cấu phần, đọc bởi U5)
    logic: >
      Mỗi bước xử lý ghi log kết quả (thành công/lỗi + mã lỗi) đủ để U5 dựng file
      trạng thái đính kèm email.
    violation: Thiếu lưu vết → file trạng thái không đầy đủ.
    source: NFR5

  - id: BR5.7
    statement: Không hardcode credentials/endpoint mail exchange.
    category: constraint
    applies_to: StatusEmail
    trigger: Khi gửi email qua mail exchange
    logic: Thông tin mail (From/Cc/endpoint/credentials) đọc từ data/config.yaml, không hardcode, không log secret.
    violation: Vi phạm bảo mật (NFR4/US5.1) — không được phép.
    source: NFR4
```

## Tóm tắt quy tắc

| ID | Loại | Nội dung |
|---|---|---|
| BR5.1 | policy | Tổng hợp trạng thái mọi CIF (gồm KH lỗi) |
| BR5.2 | constraint | Bảng trạng thái đúng cột STT/STR_CIF/Trạng thái/Mã lỗi/Chi tiết lỗi |
| BR5.3 | policy | Gửi email lô kèm file đính kèm |
| BR5.4 | policy | KH lỗi sau 3 retry nằm trong email lô |
| BR5.5 | policy | Cô lập lỗi theo khách hàng |
| BR5.6 | constraint | Lưu vết xử lý từng bước |
| BR5.7 | constraint | Không hardcode credentials mail |
