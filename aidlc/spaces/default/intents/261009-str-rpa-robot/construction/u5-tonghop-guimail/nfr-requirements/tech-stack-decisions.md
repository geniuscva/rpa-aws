# Tech Stack Decisions — U5 TongHopVaGuiMail

- Python 3.11+ (chung). Thư viện ở `requirements.txt`.
- Dựng file excel trạng thái bằng openpyxl.
- Gửi email qua mail exchange (SMTP) — thư viện smtplib/email chuẩn hoặc client cấu hình.
- Cấu hình mail ở `data/config.yaml`, không hardcode.
- Test: pytest; SMTP mock trong test.
