# Security Requirements — U1 ConsumeData

## Sources
- requirements.md (NFR4), quyết định cấu hình của người dùng (config.yaml).

## Yêu cầu

- **SEC-U1-1:** Thông tin xác thực ECM (và cấu hình khác) đọc từ file
  `data/config.yaml`, không hardcode trong mã nguồn. (nguồn: NFR4, điều chỉnh)
- **SEC-U1-2:** `data/config.yaml` không được commit vào git (thêm .gitignore);
  cung cấp file mẫu `data/config.example.yaml` không chứa giá trị thật.
- **SEC-U1-3:** Không ghi giá trị secret (password, token) ra log; chỉ ghi tên
  khóa hoặc trạng thái.
- **SEC-U1-4:** U1 chỉ đọc thư mục nguồn được phép
  (/Users/hainguyen/Projects/RPA/AMLD/YYYYMM/YYYYMMDD) và ghi file PDF/log ở nơi
  được cấu hình.
- **SEC-U1-5:** Token ECM lấy qua client_credentials chỉ giữ trong bộ nhớ phiên
  xử lý, không ghi ra đĩa.

> Lưu ý: so với rule chung "đọc secrets từ env/secrets manager", dự án này dùng
> file config.yaml theo yêu cầu người dùng (chạy local). Nguyên tắc không-hardcode
> và không-lộ-secret vẫn giữ.
