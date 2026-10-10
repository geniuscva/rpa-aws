# Unit Test Instructions — U2 DataEntryAccuity

Posture TDD, pytest, mock AccuityPort (không chạm web thật).

| Lớp | Happy | Edge/error |
|---|---|---|
| AccuityStage | tra cứu thành công → BOT_ACCUITY=OK, có PDF | lỗi đăng nhập → processing_stopped; không có kết quả → BOT_ACCUITY ghi rõ |
| AccuityAdapter (mock) | login + lookup + export trả path | login fail raise |

Quy tắc: không test luôn-đúng; chạy không cần web thật.
