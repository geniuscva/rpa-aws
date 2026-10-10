# Reliability Design — U2 DataEntryAccuity

- Lỗi đăng nhập/thao tác Accuity → ghi BOT_ACCUITY/BOT_GHICHU, đặt
  processing_stopped=true; chuyển tới U5.
- Thao tác web có timeout; không treo pipeline.
- U2 độc lập U3: chỉ ghi BOT_ACCUITY, không đụng cột khác.
