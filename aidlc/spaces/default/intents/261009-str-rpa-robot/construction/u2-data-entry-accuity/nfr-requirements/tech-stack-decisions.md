# Tech Stack Decisions — U2 DataEntryAccuity

> Kế thừa quyết định tech-stack chung của robot (xem U1 tech-stack-decisions.md).
> Mục này chỉ ghi điểm riêng của U2.

## Ngôn ngữ & nền tảng
- **Python 3.11+**; U2 là module trong cùng process pipeline, hiện thực interface
  `PipelineStage.process(record, context)`.

## Thư viện riêng của U2
- **Playwright** (điều khiển trình duyệt web Accuity mock): đăng nhập, điền form
  tra cứu, export/print PDF. Pin phiên bản trong `requirements.txt` ở gốc dự án.
- Web Accuity được bọc sau một **AccuityAdapter** (interface) để test thay bằng
  mock/fake, không phụ thuộc Playwright/web thật trong unit test (NFR6).

## Cấu hình & bí mật
- Thêm khóa `accuity` vào `data/config.yaml` (url, username, password). Đọc qua
  `robot.config`; KHÔNG hardcode, KHÔNG commit config.yaml, cập nhật
  `data/config.example.yaml`.

## Logging
- Dùng chung logger JSON của robot (Thời gian / Log Level / Message).

## Test
- pytest; posture TDD; sàn coverage 80% (classic scope). AccuityAdapter mock
  trong test; không gọi web thật.
