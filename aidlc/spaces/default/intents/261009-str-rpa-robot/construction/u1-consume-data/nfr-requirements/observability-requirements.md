# Observability Requirements — U1 ConsumeData

## Sources
- requirements.md (NFR5), quyết định logging của người dùng.

## Yêu cầu

- **OBS-U1-1:** Log có cấu trúc dạng JSON. Mỗi bản ghi log gồm các trường:
  **Thời gian (timestamp)**, **Log Level** (INFO/ERROR/...), **Message**. Lưu vào
  file `.json` (ví dụ append JSON lines).
- **OBS-U1-2:** Ghi log ở các mốc chính của U1 theo từng CIF: nhận message, xác
  định thư mục, phân loại KH, kiểm file, gọi ECM, tính dòng tiền, xuất PDF, kết
  quả (thành công/lỗi + mã lỗi).
- **OBS-U1-3:** Log đủ chi tiết để U5 dựng file trạng thái lô (CIF, trạng thái,
  mã lỗi, chi tiết lỗi).
- **OBS-U1-4:** Không log giá trị secret.
