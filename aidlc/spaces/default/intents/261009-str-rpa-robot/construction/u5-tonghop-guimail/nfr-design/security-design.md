# Security Design — U5 TongHopVaGuiMail

- SMTP host/user/pass từ config.yaml, không hardcode; không log mật khẩu.
- File đính kèm chỉ chứa dữ liệu nghiệp vụ, không secret.
