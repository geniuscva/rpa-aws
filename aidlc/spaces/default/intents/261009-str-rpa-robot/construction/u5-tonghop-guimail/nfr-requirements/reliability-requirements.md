# Reliability Requirements — U5 TongHopVaGuiMail

- **REL-U5-1:** Cô lập lỗi theo KH: mỗi CIF là một hàng trạng thái; KH lỗi (thiếu
  file, lỗi tra cứu, thất bại sau 3 retry, dừng luồng) là một hàng FAIL, không
  làm hỏng cả lô.
- **REL-U5-2:** Gửi email có xử lý lỗi; nếu gửi thất bại thì ghi log lỗi rõ ràng.
- **REL-U5-3:** Luôn dựng được file trạng thái từ dữ liệu đã thu thập (StrRecord
  của mọi CIF), kể cả khi một số CIF lỗi.
