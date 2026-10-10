# Logical Components — U3 DataEntryTraCuuThue (NFR Design)

| Thành phần | Trách nhiệm | NFR |
|---|---|---|
| TaxAuthorityAdapter | Interface tới web Cục Thuế thật (mở, nhập MST, tra cứu, export) — mock trong test | NFR6 |
| CaptchaSolver | Giải captcha ảnh bằng ddddocr, giới hạn số lần | REL |
| TaxLookupStep | Nhập MST, tra cứu, print PDF nếu có | — |
| TaxAuthorityStage | process(record,context): chỉ KHDN, ghi BOT_TRACUUTHE | REL |
| StructuredLogger (dùng chung) | Log JSON | OBS |

Adapter ẩn web Cục Thuế; test mock. U3 độc lập U2.
