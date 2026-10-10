# Reliability Design — U4 DataEntryAMLD

- RetryPolicy bọc mỗi bước nhập, ≤3 lần; vẫn lỗi → báo thất bại (U5 email).
- AmldLoginStep: treo → reload & login lại ≤3 lần.
- TickValidator chặn giá trị ngoài tập → dừng luồng KH, ghi lỗi.
- AttachmentUploader: thiếu tài liệu bắt buộc → FAIL, không nộp.
- Lỗi ghi BOT_ALMD/BOT_TINHTRANGTRASOAT/BOT_GHICHU, processing_stopped khi dừng.
