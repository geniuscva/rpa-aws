# Tech Stack Decisions — U1 ConsumeData (dùng chung cả robot)

## Ngôn ngữ & nền tảng
- **Python 3.11+**, chạy local như một ứng dụng nền.
- Các cấu phần là module trong cùng một process (pipeline U1→U5).

## Thư viện
- Danh sách thư viện cụ thể được khai báo và quản lý trong **`requirements.txt`**
  ở gốc dự án (không cố định cứng trong tài liệu này). Dự kiến gồm: client Kafka,
  thư viện đọc Excel, HTTP client gọi ECM, thư viện sinh PDF, Playwright (cho các
  Unit web U2–U4), ddddocr (U3), pytest (test). Phiên bản pin trong requirements.txt.

## Cấu hình & bí mật
- **Mọi cấu hình và thông tin xác thực (user/pass, endpoint, đường dẫn) để ở file
  `data/config.yaml`** — KHÔNG load từ biến môi trường (theo quyết định của người
  dùng cho dự án local này).
- `data/config.yaml` KHÔNG được commit (thêm vào .gitignore); cung cấp
  `data/config.example.yaml` làm mẫu.
- Secrets không hardcode trong mã nguồn (vẫn tuân thủ nguyên tắc không-hardcode;
  nguồn cấu hình là file config thay vì env).

## Logging
- Log dạng JSON, mỗi dòng gồm: **Thời gian / Log Level / Message**, lưu trong
  file `.json` (xem observability-requirements.md).

## Test
- pytest; posture TDD; sàn coverage 80% (classic scope).
