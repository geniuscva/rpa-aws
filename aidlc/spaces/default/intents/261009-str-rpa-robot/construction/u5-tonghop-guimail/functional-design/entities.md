# Entities — U5 TongHopVaGuiMail

Cấu phần U5 là chặng cuối pipeline: nhận `StrRecord` của tất cả CIF trong một lô
(bao gồm cả record đã dừng từ U1–U4), tổng hợp trạng thái từng khách hàng thành
bảng, dựng file excel trạng thái đính kèm, và gửi một email trạng thái lô qua hệ
thống mail exchange — kể cả email báo thất bại cho những KH lỗi sau 3 lần retry.
U5 đọc toàn bộ `StrRecord`; không ghi đè cột xử lý của các cấu phần trước (chỉ bổ
sung `BOT_GHICHU` tổng hợp nếu cần).

## Source of truth

```yaml
entities:
  - name: ProcessingResult
    description: Kết quả xử lý của một CIF trong lô, dẫn xuất từ StrRecord.
    attributes:
      - { name: stt, type: integer, required: true, constraint: "số thứ tự trong bảng trạng thái" }
      - { name: cif, type: string, required: true, constraint: "từ StrRecord.CIF (STR_CIF)" }
      - { name: status, type: string, required: true, constraint: "SUCCESS | FAIL" }
      - { name: errorCode, type: string, required: false, constraint: "mã lỗi khi FAIL" }
      - { name: errorDetail, type: string, required: false, constraint: "chi tiết lỗi khi FAIL (từ BOT_GHICHU)" }
    constraints:
      - "status = FAIL khi processingStopped = true hoặc có BOT_* lỗi; ngược lại SUCCESS"
    relationships:
      - "mỗi ProcessingResult thuộc một CIF (một CustomerCase)"

  - name: BatchStatusReport
    description: >
      File excel trạng thái tổng hợp cho cả lô, đính kèm vào email. Mỗi hàng là một
      ProcessingResult.
    attributes:
      - { name: batchId, type: string, required: true }
      - { name: rows, type: list, required: true, constraint: "danh sách ProcessingResult (STT, STR_CIF, Trạng thái, Mã lỗi, Chi tiết lỗi)" }
      - { name: attachmentPath, type: string, required: true, constraint: "đường dẫn file excel đã dựng" }
      - { name: sentAt, type: string, required: false }
    relationships:
      - "mỗi BatchStatusReport tổng hợp cho một BatchJob (một lô)"

  - name: StatusEmail
    description: Email trạng thái lô gửi qua mail exchange.
    attributes:
      - { name: from, type: string, required: true, constraint: "nguyendinhhai1996@hotmail.com (FR13.1)" }
      - { name: to, type: string, required: true, constraint: "từ StrRecord.EMAIL_NGUOI_LAP_BAO_CAO của người lập" }
      - { name: cc, type: list, required: true, constraint: "nguyendinhhai1996@hotmail.com (FR13.1); các Cc bổ sung theo rule đội nếu cấu hình" }
      - { name: subject, type: string, required: true, constraint: "theo template mục 5.4 tài liệu" }
      - { name: body, type: string, required: true, constraint: "theo template mục 5.4 tài liệu" }
      - { name: attachment, type: string, required: true, constraint: "file excel BatchStatusReport" }
    constraints:
      - "Gửi qua hệ thống mail exchange (FR13.2)"
      - "Cc/From/endpoint mail đọc từ data/config.yaml, không hardcode, không log secret (NFR4)"

  - name: StrRecord
    description: >
      Object pipeline dùng chung (hợp đồng contract-summary.md). U5 đọc TOÀN BỘ
      StrRecord của mọi CIF trong lô để dựng ProcessingResult; không ghi đè cột xử
      lý của U1–U4. Có thể bổ sung BOT_GHICHU tổng hợp khi cần.
    attributes:
      - { name: CIF, type: string, required: true }
      - { name: EMAIL_NGUOI_LAP_BAO_CAO, type: string, required: true, constraint: "To của email trạng thái" }
      - { name: BOT_ECM, type: string, required: false }
      - { name: BOT_ACCUITY, type: string, required: false }
      - { name: BOT_TRACUUTHE, type: string, required: false }
      - { name: BOT_ALMD, type: string, required: false }
      - { name: BOT_TINHTRANGTRASOAT, type: string, required: false }
      - { name: BOT_GHICHU, type: string, required: false, constraint: "ghi chú/mã lỗi tổng hợp" }
      - { name: processing_stopped, type: boolean, required: true }
    constraints:
      - "U5 đọc toàn bộ record của lô; chỉ bổ sung BOT_GHICHU tổng hợp, không ghi đè cột khác"
```

## Tóm tắt

U5 làm việc với `ProcessingResult` (một hàng trạng thái/CIF, dẫn xuất từ
`StrRecord`), `BatchStatusReport` (file excel đính kèm cấp lô), và `StatusEmail`
(email gửi qua mail exchange). U5 đọc toàn bộ `StrRecord` của mọi CIF trong lô để
tổng hợp — gồm cả KH lỗi dừng luồng (status FAIL) — rồi dựng và gửi một email
trạng thái lô duy nhất.
