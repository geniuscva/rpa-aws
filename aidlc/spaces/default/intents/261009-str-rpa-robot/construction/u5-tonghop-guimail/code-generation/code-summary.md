# Code Summary — U5 TongHopVaGuiMail

## Những gì đã xây

Cài đặt đầy đủ cấu phần U5 (TongHopVaGuiMail): chặng cuối pipeline, chạy MỘT LẦN
cho cả lô. Tổng hợp trạng thái mọi CIF (gồm KH lỗi/dừng luồng), dựng file Excel
trạng thái, dựng + gửi một email lô kèm đính kèm. Dùng khung chung đã có từ U1.
Code ở `robot/u5_tonghop/`.

### Cấu phần U5 (robot/u5_tonghop/)
- `result_builder.py` — `ResultBuilder.build(record, stt)` / `build_batch(records)`
  → `ProcessingResult` (SUCCESS/FAIL): FAIL khi processing_stopped hoặc BOT_* lỗi;
  errorCode từ BOT_TINHTRANGTRASOAT, errorDetail từ BOT_GHICHU. KH lỗi vẫn có một
  hàng, đánh STT theo thứ tự (BR5.1/5.5).
- `status_report.py` — `BatchStatusReport.write(results, path)` dựng Excel đúng cột
  STT / STR_CIF / Trạng thái / Mã lỗi / Chi tiết lỗi (BR5.2); openpyxl import trễ,
  `rows()` thuần để test. 
- `email_sender.py` — `EmailPort` (interface) + `MockEmailPort` + `SmtpEmailPort`;
  `build_status_email()` (From/To người lập/Cc + đính kèm Excel, config-driven —
  BR5.7); `EmailSender.send()` trả `SendResult`, lỗi gửi → ok=False, KHÔNG raise để
  giữ report (BR5.3). `MailConfig` đọc từ config, không hardcode, không log secret.
- `tonghop_stage.py` — `TongHopStage.process_batch(records, context)` →
  `BatchResult`: dựng ProcessingResult cho mọi CIF (cô lập lỗi BR5.5), ghi Excel
  (BR5.2), dựng + gửi một email lô (BR5.3/5.4); gửi lỗi → ghi log, giữ report; trả
  report_path, sent, sent_at/error, success_count, fail_count.

## Test
- 10 test (pytest), tất cả PASS. Mock `EmailPort` + workbook; không gửi mail/ghi
  Excel thật.
- Phủ (result): OK→SUCCESS; record dừng→FAIL + chi tiết từ BOT_GHICHU; BOT_* lỗi→
  FAIL; build_batch đánh STT đúng thứ tự và cô lập lỗi.
- Phủ (report): cột đúng + thứ tự hàng; write lưu workbook; lô rỗng → chỉ header.
- Phủ (stage): lô toàn SUCCESS → một email + sent_at; lô có KH lỗi → vẫn một email
  đủ hàng (BR5.4/5.5); gửi mail lỗi → giữ report + không raise (BR5.3).
- Lệnh: `.venv/bin/pytest tests/u5_tonghop` → `10 passed`. Toàn bộ suite:
  `.venv/bin/pytest` → `82 passed` (25 U1 + 12 U2 + 12 U3 + 23 U4 + 10 U5).

## Lưu ý
- Thông tin mail (From/Cc/host/credentials) đọc từ `data/config.yaml`, không
  hardcode, không log secret (BR5.7/NFR4). Người nhận To = EMAIL người lập báo cáo
  lấy từ record. Danh sách Cc theo cấu hình (bao gồm các địa chỉ mandate ở
  project.md khi điền vào config).
- Hiện thực SMTP thật gắn ở bước chạy thật; test chạy hoàn toàn trên mock.
- Lỗi gửi email không làm hỏng BatchStatusReport đã dựng (BR5.3) — hỗ trợ chạy lại
  thủ công.
