# Unit Test Instructions — U5 TongHopVaGuiMail

Posture TDD, pytest, mock `EmailPort` và openpyxl (không gửi mail thật).

| Lớp | Happy | Edge/error |
|---|---|---|
| ResultBuilder | record OK → SUCCESS | record dừng/BOT_* lỗi → FAIL + mã lỗi/chi tiết từ BOT_GHICHU |
| BatchStatusReport | ghi đúng cột STT/STR_CIF/Trạng thái/Mã lỗi/Chi tiết lỗi, đánh STT theo thứ tự | lô rỗng → file chỉ header |
| TongHopStage | lô toàn SUCCESS → gửi 1 email kèm Excel, sent_at ghi nhận | lô có KH lỗi (cô lập, vẫn 1 email đủ hàng); gửi mail lỗi → giữ report + ghi log, không raise |

Quy tắc: không test luôn-đúng; chạy không cần mail server thật; khẳng định KH lỗi
vẫn có một hàng FAIL trong email lô (BR5.4/BR5.5).
