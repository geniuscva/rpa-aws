# Tech Stack Decisions — U4 DataEntryAMLD

- Python 3.11+ (chung). Thư viện ở `requirements.txt`.
- Tự động hóa AMLD Portal thật bằng Playwright.
- Credentials/cấu hình ở `data/config.yaml`, không hardcode.
- Test: pytest; AMLD mock trong test tự động, thật khi production.
