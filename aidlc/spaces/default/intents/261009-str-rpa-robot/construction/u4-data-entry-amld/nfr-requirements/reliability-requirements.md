# Reliability Requirements — U4 DataEntryAMLD

- **REL-U4-1:** Mỗi bước nhập lỗi retry ≤ 3 lần (RetryPolicy); vẫn lỗi → báo thất
  bại (chuyển tín hiệu cho U5 gửi email).
- **REL-U4-2:** Treo màn hình đăng nhập → reload & đăng nhập lại ≤ 3 lần, quá thì
  báo lỗi.
- **REL-U4-3:** Giá trị tick Phần IV/V ngoài tập định nghĩa → dừng luồng KH, ghi lỗi.
- **REL-U4-4:** Thiếu tài liệu đính kèm bắt buộc → không nộp, báo FAIL.
- **REL-U4-5:** Lỗi ghi vào StrRecord (BOT_ALMD/BOT_TINHTRANGTRASOAT/BOT_GHICHU),
  đặt processing_stopped khi dừng luồng KH.
