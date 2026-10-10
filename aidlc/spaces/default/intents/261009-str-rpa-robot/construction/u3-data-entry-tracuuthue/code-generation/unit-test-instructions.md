# Unit Test Instructions — U3 DataEntryTraCuuThue

Posture TDD, pytest, mock TaxAuthorityPort và CaptchaSolver (không chạm web thật).

| Lớp | Happy | Edge/error |
|---|---|---|
| TaxAuthorityStage | KHDN có kết quả → BOT_TRACUUTHE=OK, PDF | KHCN → N/A; không kết quả; lỗi web → processing_stopped |
| CaptchaSolver (mock) | giải đúng | fail quá N lần → không kết quả |

Quy tắc: không test luôn-đúng; chạy không cần web thật.
