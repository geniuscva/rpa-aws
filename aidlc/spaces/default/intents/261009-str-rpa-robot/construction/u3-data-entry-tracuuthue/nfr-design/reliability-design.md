# Reliability Design — U3 DataEntryTraCuuThue

- CaptchaSolver thử ddddocr tối đa N lần; quá → coi không có kết quả.
- Lỗi web/timeout → ghi BOT_TRACUUTHE/BOT_GHICHU, processing_stopped=true.
- KHCN bỏ qua an toàn (BOT_TRACUUTHE = N/A).
