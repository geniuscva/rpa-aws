# Security Requirements — U5 TongHopVaGuiMail

- **SEC-U5-1:** Thông tin mail exchange (SMTP host/user/pass) đọc từ `data/config.yaml`,
  không hardcode.
- **SEC-U5-2:** Không log mật khẩu mail; chỉ log trạng thái gửi.
- **SEC-U5-3:** File trạng thái đính kèm chỉ chứa dữ liệu nghiệp vụ (CIF, trạng
  thái, mã lỗi), không chứa secret.
