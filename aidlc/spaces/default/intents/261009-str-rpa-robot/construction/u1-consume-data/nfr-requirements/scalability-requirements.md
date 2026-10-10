# Scalability Requirements — U1 ConsumeData

## Sources
- requirements.md (NFR7, OQ3 — số liệu tải để trống trong tài liệu).

## Yêu cầu

- **SCAL-U1-1:** U1 xử lý tuần tự từng message (một CIF). Không yêu cầu xử lý
  đồng thời nhiều CIF ở phạm vi này (chạy local).
- **SCAL-U1-2:** Consumer Kafka xử lý message theo thứ tự đến; message tồn đọng
  nằm trong hàng đợi cho tới khi được xử lý.
- **SCAL-U1-3:** Số liệu tải thực tế (số CIF/ngày) chưa có (OQ3); nếu khối lượng
  lớn trong tương lai, cân nhắc xử lý song song — ngoài phạm vi hiện tại.
