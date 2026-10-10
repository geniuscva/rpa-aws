# Security Requirements — U3 DataEntryTraCuuThue

- **SEC-U3-1:** Cấu hình (URL, tham số) đọc từ `data/config.yaml`, không hardcode.
- **SEC-U3-2:** Không log nội dung nhạy cảm; captcha và mã số thuế xử lý trong bộ
  nhớ, chỉ log trạng thái.
- **SEC-U3-3:** PDF tra cứu lưu ở thư mục output cấu hình, không nơi khác.
