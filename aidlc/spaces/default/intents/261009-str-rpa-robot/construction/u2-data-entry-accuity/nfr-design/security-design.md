# Security Design — U2 DataEntryAccuity

- Credentials Accuity đọc từ `data/config.yaml` (ConfigProvider), không hardcode.
- Không log user/pass; chỉ log trạng thái tra cứu.
- PDF kết quả lưu ở thư mục output cấu hình.
