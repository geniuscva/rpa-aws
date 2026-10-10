# Build Instructions — Robot RPA STR

Robot Python chạy local; không có bước compile/bundle. "Build" ở đây là dựng môi
trường chạy được và xác minh import toàn bộ pipeline.

## 1. Phụ thuộc
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```
`requirements.txt` gồm: playwright, kafka-python, openpyxl/pandas, httpx, reportlab,
ddddocr, pytest, PyYAML.

Với Playwright (chạy thật, không cần cho test vì đã mock):
```bash
.venv/bin/playwright install chromium
```

## 2. Cấu hình
```bash
cp data/config.example.yaml data/config.yaml
```
Điền `data/config.yaml`: user/pass AMLD Portal, Accuity, endpoint Cục Thuế, ECM
(`http://localhost:8831`), Kafka (`localhost:9092`, PLAINTEXT, topic
`RPA_STR_NHNN_INPUT`), SMTP mail. File này KHÔNG commit (.gitignore); không log
giá trị secret.

Dịch vụ phụ thuộc khi chạy thật: Kafka + ECM mock server (xem
`docs/SERVICES_CONNECTION_INFO.md`); thư mục nguồn
`/Users/hainguyen/Projects/RPA/AMLD/YYYYMM/YYYYMMDD`.

## 3. Lệnh build / xác minh
```bash
# Xác minh cú pháp + import toàn bộ pipeline U1->U5
.venv/bin/python -c "import main"
```

## 4. Chạy robot
```bash
.venv/bin/python main.py
```
`main.py` nạp config, consume Kafka, chạy từng CIF qua U1→U4 tuần tự rồi U5 tổng
hợp + gửi email.

## 5. Xử lý lỗi build thường gặp
- `ConfigError: Không tìm thấy file cấu hình` → chưa copy `config.example.yaml`.
- `ModuleNotFoundError` → chưa `pip install -r requirements.txt` trong `.venv`.
- `pytest: command not found` → dùng `.venv/bin/pytest` (không dùng `pytest` trần).
- Lỗi Playwright khi chạy thật → chạy `playwright install chromium`.
