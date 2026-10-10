# Tech Stack Decisions — U3 DataEntryTraCuuThue

- Python 3.11+ (chung cả robot). Thư viện khai báo ở `requirements.txt`.
- Tự động hóa web Cục Thuế thật bằng Playwright (chung với các Unit web).
- Giải captcha bằng **ddddocr**.
- Cấu hình/secret (URL Cục Thuế, cấu hình) ở `data/config.yaml`, không hardcode.
- Test: pytest; web Cục Thuế được mock trong test tự động, chạy thật khi production.
