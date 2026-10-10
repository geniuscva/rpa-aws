# Unit Test Instructions — U4 DataEntryAMLD

Posture TDD, pytest, mock `AmldPortalPort` (không chạm AMLD Portal thật).

| Lớp | Happy | Edge/error |
|---|---|---|
| AmldStage | KHCN/KHDN đủ tài liệu → BOT_ALMD=OK, nhập I→II→IV→V→VI (bỏ III) | thiếu tài liệu bắt buộc → không nộp, stop; tick ngoài tập → stop; đăng nhập treo >3 → stop; bước nhập lỗi >3 → stop; record đã dừng → bỏ qua |
| RetryPolicy | thành công trong ≤3 lần | lỗi quá 3 lần → raise |
| TickValidator | tick hợp lệ qua; Phần V 6/7/8 → tự thêm 4,5 | tick ngoài tập → lỗi |
| AttachmentUploader | đủ tài liệu bắt buộc → thứ tự upload đúng (Bảng kê→Minh Họa Dòng Tiền→Hồ sơ mở TK→…) | thiếu 1 tài liệu bắt buộc → lỗi, không nộp |

Quy tắc: không test luôn-đúng; chạy không cần web AMLD thật; KHÔNG điền Phần III
(khẳng định rõ trong test rằng Phần III không được nhập).
