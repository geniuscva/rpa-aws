# Entities — U2 DataEntryAccuity

Mô hình thực thể của cấu phần U2 (DataEntryAccuity). U2 nhận `StrRecord` từ U1,
tra cứu khách hàng trên web Accuity mock và ghi kết quả vào cột `BOT_ACCUITY`.
Mô tả ở mức logic, không gắn công nghệ.

## Source of truth

```yaml
entities:
  - name: AccuityQuery
    description: Yêu cầu tra cứu Accuity dựng từ StrRecord của một CIF.
    attributes:
      - { name: cif, type: string, required: true, unique: true }
      - { name: entityType, type: string, required: true, allowed_values: ["Individual", "Organization"], constraint: "Individual cho KHCN, Organization cho KHDN (từ LOAIKHACHHANG)" }
      - { name: searchName, type: string, required: true, constraint: "tên KH từ TENKHACHHANG (STR_TEN_KH)" }
      - { name: searchMode, type: string, required: true, allowed_values: ["Single"], default: "Single" }
    constraints:
      - "entityType suy ra từ LOAIKHACHHANG của StrRecord; searchName không được rỗng"

  - name: AccuityLookupResult
    description: Kết quả tra cứu Accuity cho một CIF, gồm PDF export và điểm khớp.
    attributes:
      - { name: cif, type: string, required: true, unique: true }
      - { name: resultPdfPath, type: string, required: false, constraint: "Tra cứu Accuity.pdf" }
      - { name: matchScore, type: integer, required: false, min: 0, max: 100 }
      - { name: profilePdfPaths, type: "list<string>", required: false, constraint: "Tra cứu Accuity(n).pdf khi matchScore=100" }
      - { name: status, type: string, required: true, allowed_values: ["OK", "ERROR"] }
    constraints:
      - "Khi matchScore = 100 thì phải có ít nhất một profilePdfPaths"
    relationships:
      - "mỗi AccuityLookupResult thuộc một CIF (một StrRecord)"

  - name: StrRecord
    description: >
      Object dữ liệu dùng chung của pipeline (hợp đồng ở contract-summary.md). U2
      chỉ đọc các cột định danh (CIF, LOAIKHACHHANG, TENKHACHHANG) và CHỈ ghi cột
      BOT_ACCUITY (và BOT_GHICHU khi lỗi). Schema đầy đủ ở contract-summary.md.
    attributes:
      - { name: CIF, type: string, required: true, unique: true }
      - { name: processingStopped, type: boolean, required: true, default: false }
      - { name: LOAIKHACHHANG, type: string, required: true, allowed_values: ["KHCN", "KHDN"] }
      - { name: TENKHACHHANG, type: string, required: false }
      - { name: BOT_ACCUITY, type: string, required: false, constraint: "trạng thái/kết quả tra cứu Accuity (U2 ghi)" }
      - { name: BOT_GHICHU, type: string, required: false, constraint: "ghi chú lỗi khi tra cứu thất bại" }
    constraints:
      - "U2 chỉ ghi BOT_ACCUITY/BOT_GHICHU; không chạm cột của cấu phần khác"
      - "Nếu record.processingStopped=true khi vào U2 thì bỏ qua, chuyển tiếp nguyên record"
    relationships:
      - "mỗi StrRecord ứng với một CIF; U2 cập nhật BOT_ACCUITY từ AccuityLookupResult"
```

## Tóm tắt

U2 làm việc với: `AccuityQuery` (yêu cầu tra cứu dựng từ loại KH + tên KH),
`AccuityLookupResult` (PDF kết quả + điểm khớp, kèm hồ sơ in thêm khi Match Score
= 100), và cập nhật cột `BOT_ACCUITY` của `StrRecord`. Web Accuity được trừu
tượng hóa sau một adapter (NFR6) để mock trong test. Kiểu dữ liệu ở mức logic;
kiểu kỹ thuật cụ thể chốt ở Code Generation.
