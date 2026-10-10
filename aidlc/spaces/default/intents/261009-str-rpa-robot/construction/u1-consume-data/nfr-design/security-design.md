# Security Design — U1 ConsumeData

- **Cấu hình/secret:** `ConfigProvider` đọc `data/config.yaml`; file này nằm trong
  .gitignore; `data/config.example.yaml` làm mẫu (SEC-U1-1/2).
- **Không log secret:** `StructuredLogger` lọc/không ghi trường password/token
  (SEC-U1-3).
- **Token ECM:** chỉ giữ trong bộ nhớ phiên xử lý, không ghi đĩa (SEC-U1-5).
- **Giới hạn truy cập file:** chỉ đọc thư mục nguồn cấu hình và ghi output ở nơi
  cấu hình (SEC-U1-4).
