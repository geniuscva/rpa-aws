# Security Requirements — U4 DataEntryAMLD

- **SEC-U4-1:** Credentials AMLD (USER_ID/PASSWORD người lập) đọc từ `data/config.yaml`,
  không hardcode.
- **SEC-U4-2:** Không log mật khẩu/thông tin đăng nhập; chỉ log trạng thái.
- **SEC-U4-3:** Tài liệu đính kèm đọc từ thư mục output cấu hình.
