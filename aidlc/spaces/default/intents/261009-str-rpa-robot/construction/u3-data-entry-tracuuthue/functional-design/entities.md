# Entities — U3 DataEntryTraCuuThue

Cấu phần U3 tra cứu tình trạng người nộp thuế trên web Cục Thuế thật (chỉ KHDN),
giải captcha bằng ddddocr, và cập nhật `StrRecord`. U3 đọc từ `StrRecord` (mã số
thuế, loại KH) do U1 dựng; độc lập với U2.

## Source of truth

```yaml
entities:
  - name: TaxLookupRequest
    description: Yêu cầu tra cứu người nộp thuế cho một KHDN.
    attributes:
      - { name: cif, type: string, required: true }
      - { name: maSoThue, type: string, required: true, constraint: "từ StrRecord.MASOTHUE" }
    constraints:
      - "Chỉ tạo khi StrRecord.LOAIKHACHHANG = KHDN"

  - name: CaptchaChallenge
    description: Ảnh captcha cần giải trên web Cục Thuế.
    attributes:
      - { name: imageBytes, type: bytes, required: true }
      - { name: solvedText, type: string, required: false }
      - { name: attempts, type: integer, required: true, default: 0 }
    constraints:
      - "Giải bằng ddddocr; tối đa N lần thử (chốt ở code), quá thì coi là không có kết quả"

  - name: TaxLookupResult
    description: Kết quả tra cứu Cục Thuế.
    attributes:
      - { name: cif, type: string, required: true }
      - { name: found, type: boolean, required: true }
      - { name: status, type: string, required: false, constraint: "trạng thái người nộp thuế nếu có" }
      - { name: pdfPath, type: string, required: false, constraint: "Tra cứu tình trạng người nộp thuế.pdf" }
    relationships:
      - "mỗi TaxLookupResult thuộc một CIF"

  - name: StrRecord
    description: >
      Object pipeline dùng chung (hợp đồng contract-summary.md). U3 chỉ đọc MASOTHUE
      và LOAIKHACHHANG, ghi cột BOT_TRACUUTHE. Không ghi đè cột của U1/U2.
    attributes:
      - { name: CIF, type: string, required: true }
      - { name: LOAIKHACHHANG, type: string, required: true }
      - { name: MASOTHUE, type: string, required: false }
      - { name: BOT_TRACUUTHE, type: string, required: false, constraint: "kết quả tra cứu thuế do U3 ghi" }
      - { name: processing_stopped, type: boolean, required: true }
    constraints:
      - "U3 chỉ ghi BOT_TRACUUTHE (và BOT_GHICHU khi lỗi); mọi cột khác read-only với U3"
```

## Tóm tắt

U3 làm việc với `TaxLookupRequest` (chỉ KHDN), `CaptchaChallenge` (ddddocr),
`TaxLookupResult`, và chỉ ghi cột `BOT_TRACUUTHE` của `StrRecord`. Độc lập với U2
(Accuity) — hai nhánh tra cứu riêng, hội tụ ở U4.
