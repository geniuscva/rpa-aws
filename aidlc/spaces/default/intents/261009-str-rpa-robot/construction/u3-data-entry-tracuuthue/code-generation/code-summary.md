# Code Summary — U3 DataEntryTraCuuThue

## Những gì đã xây

Cài đặt đầy đủ cấu phần U3 (DataEntryTraCuuThue): tra cứu web Cục Thuế thật (chỉ
KHDN) theo một CIF, giải captcha bằng ddddocr, export `Tra cứu tình trạng người
nộp thuế.pdf`, cập nhật `StrRecord.BOT_TRACUUTHE`. Độc lập với U2. Dùng khung
chung đã có từ U1 (`robot/models.py`, `pipeline.py`, `config.py`,
`logging_setup.py`). Code ở `robot/u3_tracuuthue/`.

### Cấu phần U3 (robot/u3_tracuuthue/)
- `captcha_solver.py` —
  - `CaptchaSolver`: giải captcha bằng ddddocr (import trễ, mock được trong
    test), giới hạn số lần thử (`max_attempts`, mặc định 3, BR3.3).
    `solve(image)` trả chuỗi nhận dạng; `solve_with_retry(image_provider,
    verifier)` lặp giải–submit tới khi được chấp nhận hoặc hết lượt → `CaptchaError`.
  - `CaptchaError`.
- `tax_authority_adapter.py` —
  - `TaxAuthorityPort` (Protocol): cổng trừu tượng tới web Cục Thuế (open,
    enter_mst, get_captcha_image, submit, has_result, export_pdf). Cho phép thay
    hiện thực Playwright thật bằng mock trong test (NFR6, US2.3/FR7).
  - `TaxAuthorityClient`: điều phối open → enter_mst → giải captcha (qua
    `CaptchaSolver.solve_with_retry`, verifier = `port.submit`) → kiểm tra kết
    quả → export PDF. Gom mọi lỗi cổng/captcha thành `TaxAuthorityError`.
  - `MockTaxAuthorityPort`: mock cho test/dev (mô phỏng captcha được chấp nhận
    sau N lần, có/không kết quả, lỗi thao tác).
  - `PlaywrightTaxAuthorityPort`: hiện thực thật (import Playwright trễ; URL/
    selector đọc từ config, không hardcode — BR3.7). Không chạy trong test.
  - `TaxAuthorityError`, `TaxLookupResult` (found + pdf_path).
- `tax_stage.py` — `TaxAuthorityStage.process(record, context) -> record`:
  - BR3.1: bỏ qua record đã dừng.
  - BR3.2: KHCN → `BOT_TRACUUTHE = SKIPPED`, không tra cứu; KHDN thiếu MST → lỗi
    (BR3.6).
  - KHDN có MST: tra cứu qua client. Có kết quả → nối PDF, `BOT_TRACUUTHE = OK`
    (BR3.4). Không có kết quả → `SKIPPED` (không in PDF, không lỗi). Lỗi/captcha
    fail → `BOT_TRACUUTHE = ERROR` + `stop()` (processing_stopped + BOT_GHICHU,
    BR3.6).
  - BR3.5: ghi `BOT_TRACUUTHE`, chuyển record cho U4.

## Test
- 12 test (pytest), tất cả PASS. Mock `TaxAuthorityPort` + `CaptchaSolver`;
  không cần web Cục Thuế hay ddddocr thật.
- Phủ (captcha): giải đúng, engine trả rỗng → `CaptchaError`, retry thành công
  lần 2, fail vượt giới hạn (đúng max_attempts lần), bỏ qua lần rỗng rồi thành công.
- Phủ (stage): KHDN có kết quả → OK + 1 PDF; KHCN → SKIPPED không tra cứu; KHDN
  không có kết quả → SKIPPED không PDF; captcha fail vượt giới hạn → dừng record;
  lỗi thao tác web → dừng record; KHDN thiếu MST → lỗi; record đã dừng từ trước
  được bỏ qua.
- Lệnh: `.venv/bin/pytest tests/u3_tracuuthue` → `12 passed`. Toàn bộ suite:
  `.venv/bin/pytest` → `49 passed` (25 U1 + 12 U2 + 12 U3).

## Lưu ý
- URL/cấu hình Cục Thuế đọc từ `data/config.yaml` (không hardcode, không commit,
  không log secret — BR3.7/NFR4). `PlaywrightTaxAuthorityPort` kỳ vọng một mục
  `tax_authority` trong config khi chạy thật; test chạy hoàn toàn trên mock.
- Giá trị `BOT_TRACUUTHE` theo functional-spec: `OK` / `SKIPPED` / `ERROR`
  (KHCN và "không có kết quả" đều là `SKIPPED`).
- Hiện thực Playwright thật và captcha ddddocr thật gắn ở bước chạy thật; test
  không phụ thuộc trình duyệt hay thư viện OCR.
