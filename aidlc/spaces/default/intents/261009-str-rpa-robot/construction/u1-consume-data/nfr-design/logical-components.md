# Logical Components — U1 ConsumeData (NFR Design)

Phân rã nội bộ U1 thành các thành phần logic hiện thực NFR + chức năng.

| Thành phần | Trách nhiệm | NFR liên quan |
|---|---|---|
| KafkaConsumerAdapter | Kết nối Kafka localhost:9092 PLAINTEXT, nhận message, parse KafkaStrEvent | REL-U1-4 |
| IdempotencyStore | Lưu/kiểm eventID đã xử lý (ProcessedEvent) | REL-U1-3 |
| ConfigProvider | Đọc data/config.yaml (endpoint, user/pass, đường dẫn) | SEC-U1-1/2 |
| SourceFolderResolver | Quét thư mục ngày, khớp CIF | — |
| ExcelReader | Đọc 5 file excel, trích cột | — |
| CustomerClassifier | Xác định KHCN/KHDN theo file | — |
| EcmClientAdapter | Auth → search → download PDF, timeout+retry | REL-U1-2, SEC-U1-5 |
| CashFlowCalculator | Tính số liệu dòng tiền | PERF |
| CashFlowPdfRenderer | Xuất Minh Họa Dòng Tiền.pdf | — |
| StructuredLogger | Ghi log JSON (timestamp/level/message) | OBS-U1-1..4 |
| StrRecordBuilder | Khởi tạo & điền StrRecord phần input; set processingStopped khi lỗi | REL-U1-1 |

Các adapter (Kafka, ECM) ẩn sau interface để mock trong test (NFR6).
