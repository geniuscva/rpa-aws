# Reliability Requirements — U2 DataEntryAccuity

## Sources
- requirements.md (NFR3), quyết định reliability của người dùng.

## Yêu cầu

- **REL-U2-1:** Lỗi khi tra cứu Accuity cho một CIF được cô lập: ghi lỗi vào
  StrRecord (BOT_ACCUITY/BOT_GHICHU, kèm địa chỉ web), đặt processingStopped=true;
  pipeline tiếp tục với CIF kế tiếp.
- **REL-U2-2:** Thao tác web Accuity có timeout chờ phần tử; lỗi tạm thời (chưa
  render kịp) có thể thử lại nhẹ nhưng không treo pipeline.
- **REL-U2-3:** Khi record vào U2 đã có processingStopped=true (lỗi từ U1), U2 bỏ
  qua tra cứu và chuyển tiếp nguyên record (cô lập lỗi theo CIF — NFR3).
- **REL-U2-4:** Web Accuity được trừu tượng hóa sau một adapter để test tự động
  dùng mock, không phụ thuộc web thật (NFR6).
