# Security Requirements — U2 DataEntryAccuity

## Sources
- requirements.md (NFR4), quyết định cấu hình của người dùng (config.yaml).

## Yêu cầu

- **SEC-U2-1:** Thông tin xác thực Accuity (user/password, URL) đọc từ file
  `data/config.yaml`, không hardcode trong mã nguồn. (nguồn: NFR4, điều chỉnh)
- **SEC-U2-2:** `data/config.yaml` không được commit vào git; file mẫu
  `data/config.example.yaml` chứa khóa `accuity` không có giá trị thật.
- **SEC-U2-3:** Không ghi giá trị secret (password Accuity) ra log; chỉ ghi tên
  khóa, URL (không kèm credential) hoặc trạng thái.
- **SEC-U2-4:** U2 chỉ ghi file PDF kết quả tra cứu ở thư mục output được cấu
  hình (output_root/<cif>).
- **SEC-U2-5:** Phiên đăng nhập Accuity chỉ giữ trong bộ nhớ phiên xử lý; không
  lưu cookie/credential ra đĩa.
