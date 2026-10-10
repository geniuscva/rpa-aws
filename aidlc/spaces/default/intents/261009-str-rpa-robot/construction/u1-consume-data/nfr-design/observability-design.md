# Observability Design — U1 ConsumeData

- **StructuredLogger:** ghi log dạng JSON lines, mỗi bản ghi gồm timestamp, level
  (INFO/ERROR), message (OBS-U1-1).
- **Điểm log:** nhận message, resolve folder, phân loại KH, kiểm file, gọi ECM,
  tính dòng tiền, xuất PDF, kết quả (OBS-U1-2).
- **Dữ liệu cho trạng thái lô:** log chứa CIF, trạng thái, mã lỗi, chi tiết để U5
  dựng file trạng thái (OBS-U1-3).
- **Lọc secret:** không ghi giá trị password/token (OBS-U1-4).
- File log cấu hình đường dẫn trong data/config.yaml.
