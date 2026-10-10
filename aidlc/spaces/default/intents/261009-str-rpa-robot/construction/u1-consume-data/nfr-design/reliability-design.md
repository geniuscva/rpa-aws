# Reliability Design — U1 ConsumeData

- **Cô lập lỗi:** `StrRecordBuilder` bắt lỗi ở mỗi bước, ghi BOT_ECM/BOT_GHICHU,
  đặt processingStopped=true; consumer không sập (REL-U1-1).
- **ECM timeout+retry:** `EcmClientAdapter` dùng timeout cấu hình và retry nhẹ
  (ví dụ 2–3 lần backoff ngắn) cho lỗi tạm thời (REL-U1-2).
- **Idempotency:** `IdempotencyStore` kiểm eventID trước khi xử lý; ghi sau khi
  xong (REL-U1-3).
- **Message lỗi:** parse fail → log + bỏ qua, không dừng consumer (REL-U1-4).
