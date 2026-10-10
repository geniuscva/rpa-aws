# Code Summary — U2 DataEntryAccuity

## Những gì đã xây

Cài đặt đầy đủ cấu phần U2 (DataEntryAccuity): tra cứu web Accuity (mock) theo một
CIF, export PDF kết quả, cập nhật `StrRecord.BOT_ACCUITY`. Độc lập với U3. Dùng
khung chung đã có từ U1 (`robot/models.py`, `pipeline.py`, `config.py`,
`logging_setup.py`). Code ở `robot/u2_accuity/`.

### Cấu phần U2 (robot/u2_accuity/)
- `accuity_adapter.py` —
  - `AccuityPort` (Protocol): cổng trừu tượng tới Accuity (login, lookup,
    export_result_pdf, export_record_pdf). Hiện thực Playwright thật ẩn sau cổng,
    cho phép mock trong test (NFR6).
  - `AccuityClient`: điều phối login → lookup → export PDF, lưu PDF ra output_dir.
    `entity_type_for()` map KHCN→Individual, KHDN→Organization. Khi Match Score=100
    export thêm PDF hồ sơ `Tra cứu Accuity(1).pdf`. Gom mọi lỗi cổng thành
    `AccuityError`.
  - `AccuityError`, `AccuityResult` (match_score + pdf_paths).
- `accuity_stage.py` — `AccuityStage.process(record, context) -> record`:
  bỏ qua record đã dừng; dựng client từ `port_factory`; tra cứu theo
  `ten_khach_hang` (fallback `cif`); nối PDF vào `dossier_pdf_paths`; ghi
  `BOT_ACCUITY = "OK (match=...)"`; lỗi → `BOT_ACCUITY="ERROR"` + `stop()`
  (processing_stopped + BOT_GHICHU).

## Test
- 12 test (pytest), tất cả PASS. Mock `AccuityPort`; không cần web/Playwright thật.
- Phủ (adapter): map entity type, happy KHCN (1 PDF), KHDN match=100 (2 PDF),
  lỗi login/lookup → `AccuityError`, thiếu match_score mặc định 0.
- Phủ (stage): KHCN thành công cập nhật BOT_ACCUITY, KHDN match=100 nối 2 PDF giữ
  file cũ, lỗi login/lookup → dừng record + BOT_GHICHU, record đã dừng từ trước
  được bỏ qua, fallback tên KH về CIF.
- Lệnh: `.venv/bin/pytest tests/u2_accuity` → `12 passed`. Toàn bộ suite:
  `.venv/bin/pytest` → `37 passed` (25 U1 + 12 U2).

## Lưu ý
- Credentials Accuity đọc từ `data/config.yaml` (không hardcode, không commit).
- Hiện thực Playwright thật của `AccuityPort` sẽ gắn ở bước chạy thật; test chạy
  hoàn toàn trên mock nên không phụ thuộc trình duyệt.
