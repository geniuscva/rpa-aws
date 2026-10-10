# Reliability Requirements — U3 DataEntryTraCuuThue

- **REL-U3-1:** Captcha giải bằng ddddocr, thử lại tối đa N lần; quá thì coi không
  có kết quả (không lỗi cứng).
- **REL-U3-2:** Lỗi web/timeout → ghi StrRecord (BOT_TRACUUTHE/BOT_GHICHU), đặt
  processing_stopped=true; không làm sập pipeline.
- **REL-U3-3:** KHCN bỏ qua U3 an toàn (ghi BOT_TRACUUTHE = N/A).
