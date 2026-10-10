# Security Design — U3 DataEntryTraCuuThue

- Cấu hình web Cục Thuế đọc từ config.yaml, không hardcode.
- Không log nội dung nhạy cảm; MST/captcha xử lý trong bộ nhớ.
- PDF lưu thư mục output cấu hình.
