# Reliability Design — U5 TongHopVaGuiMail

- Cô lập lỗi theo KH: mỗi CIF một hàng; KH lỗi là hàng FAIL, không hỏng cả lô.
- EmailSender xử lý lỗi gửi; thất bại thì log rõ.
- Luôn dựng được file trạng thái từ StrRecord đã thu thập.
