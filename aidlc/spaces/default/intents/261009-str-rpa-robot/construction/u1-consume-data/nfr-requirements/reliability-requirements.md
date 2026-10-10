# Reliability Requirements — U1 ConsumeData

## Sources
- requirements.md (NFR3), quyết định reliability của người dùng.

## Yêu cầu

- **REL-U1-1:** Lỗi khi xử lý một CIF được cô lập: ghi lỗi vào StrRecord
  (BOT_ECM/BOT_GHICHU), đặt processingStopped=true; consumer KHÔNG sập, tiếp tục
  nhận message kế tiếp.
- **REL-U1-2:** Gọi ECM có timeout và retry nhẹ cho lỗi tạm thời; vượt ngưỡng thì
  đánh dấu lỗi và dừng record (không treo pipeline).
- **REL-U1-3:** Chống trùng message theo eventID (idempotency): message đã xử lý
  thì bỏ qua.
- **REL-U1-4:** Message Kafka không hợp lệ được log và bỏ qua, không làm dừng
  consumer.
