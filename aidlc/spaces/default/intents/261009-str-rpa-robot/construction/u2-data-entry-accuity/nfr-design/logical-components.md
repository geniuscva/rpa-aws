# Logical Components — U2 DataEntryAccuity (NFR Design)

| Thành phần | Trách nhiệm | NFR |
|---|---|---|
| AccuityAdapter | Interface tới web Accuity mock (login, tra cứu, export) — mock được trong test | NFR6 |
| AccuityLoginStep | Đăng nhập user/pass từ config | SEC |
| AccuityLookupStep | Chọn Entity Type theo loại KH, tra cứu theo tên, submit | — |
| AccuityExportStep | Export Tra cứu Accuity.pdf; Match Score 100 → print hồ sơ | — |
| AccuityStage | process(record, context): ghi BOT_ACCUITY, trả record | REL |
| StructuredLogger (dùng chung) | Log JSON | OBS |

Adapter ẩn web Accuity sau interface; test dùng mock. Credentials từ config.yaml.
