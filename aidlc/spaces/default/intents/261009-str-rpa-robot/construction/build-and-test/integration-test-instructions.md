# Integration Test Instructions — Robot RPA STR

Test strategy: **Standard** → sinh integration test cho các ranh giới cross-unit
quan trọng. Hệ thống ngoài (Kafka, ECM, Accuity, Cục Thuế, AMLD Portal, SMTP)
mock sau interface (NFR6).

## Phạm vi
Kiểm tra luồng pipeline nối U1→U5 qua hợp đồng dùng chung `StrRecord` và
`run_pipeline`, với tất cả cổng ngoài mock:
- TC01 — Happy path: một CIF KHCN đi hết U1→U4, U5 tổng hợp + gửi email thành công.
- TC02 — Dừng sớm: thiếu file bắt buộc ở U1 → record dừng, U2 không chạy, U5 vẫn
  gửi email với trạng thái lỗi (cô lập lỗi một KH không làm hỏng lô).

## Framework & cách chạy
```bash
.venv/bin/pytest tests/test_integration.py -q
```
File: `tests/test_integration.py`. Dùng `unittest.mock` để mock adapter từng Unit
(ECM, Accuity port, Tax port, AMLD port, Email port) và patch các collaborator nội
bộ của U1 (ExcelReader, CashFlowCalculator...). Không cần dịch vụ ngoài.

## Dữ liệu & môi trường test
- Không cần Kafka/ECM/trình duyệt thật.
- `fetch_dossier(cif)` trả `tuple[list[str], str]` = (danh sách PDF, mã số thuế).
- Mock resolver trả đường dẫn thư mục; stage copy input là best-effort nên thư
  mục không tồn tại không làm hỏng luồng.

## Kỳ vọng coverage (Standard)
- Phủ ít nhất 2 ranh giới cross-unit: happy path trọn pipeline + nhánh dừng-sớm.
- Khẳng định hợp đồng `StrRecord` truyền đúng giữa các Unit và U5 gửi 1 email/lô.

## Mở rộng khi cần
- Thêm TC cho KHDN (U3 tra cứu thuế chạy), lỗi Accuity/AMLD retry, thiếu đính kèm
  bắt buộc (U4 không nộp). Hiện U4/U3 đã có unit test riêng cho các nhánh này.
