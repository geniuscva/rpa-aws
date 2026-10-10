# Domain Design — Questions

Interaction mode: Guide me.

Đề xuất phân rã robot STR thành các khối logic (component) theo luồng nghiệp vụ.
Dưới đây là các điểm cần chốt về ranh giới.

---

## Q1 — Mức phân rã component

Phân rã robot thành bao nhiêu khối?

- A. Phân rã theo chức năng nghiệp vụ: Orchestrator (điều phối lô/KH), KafkaConsumer, SourceDataReader (đọc excel + check file), EcmClient (lấy PDF hồ sơ), CashFlowDiagramBuilder, AccuityLookup, TaxAuthorityLookup, AmldPortalFiller, RetryManager, ErrorAggregator, EmailNotifier (gợi ý)
- B. Phân rã thô hơn: Orchestrator, DataIngestion (gộp Kafka + đọc file + ECM), ExternalLookups (gộp Accuity + Cục Thuế), PortalAutomation, Notification
- C. Phân rã mịn hơn (tách thêm từng Phần của Mẫu số 01 thành component riêng)
- X. Other (please specify)

[Answer]: A

---

## Q2 — Lớp trừu tượng cho hệ thống ngoài

Có cần một interface/adapter chung cho các web ngoài (để mock trong test theo NFR6) không?

- A. Có — mỗi hệ thống ngoài (Accuity, Cục Thuế, AMLD, ECM) ẩn sau một interface adapter riêng, cho phép thay mock/real khi test (gợi ý)
- B. Không cần tách interface, gọi trực tiếp
- X. Other (please specify)

[Answer]: A

---

## Q3 — Thực thể (entity) & chủ sở hữu

Các entity chính (mỗi entity thuộc đúng một component). Đề xuất:
- `BatchJob` (lô việc từ Kafka) — Orchestrator
- `CustomerCase` (một KH/CIF trong lô) — Orchestrator
- `SourceData` (dữ liệu 5 file excel của 1 KH) — SourceDataReader
- `CustomerDossier` (hồ sơ PDF từ ECM) — EcmClient
- `CashFlowDiagram` — CashFlowDiagramBuilder
- `LookupResult` (kết quả Accuity/Cục Thuế) — các component lookup
- `StrReport` (báo cáo nhập trên AMLD) — AmldPortalFiller
- `ProcessingResult` (trạng thái + lỗi theo KH) — ErrorAggregator
- `BatchStatusReport` (file + email trạng thái lô) — EmailNotifier

- A. Đồng ý tập entity & chủ sở hữu như đề xuất (gợi ý)
- B. Cần điều chỉnh (mô tả)
- X. Other (please specify)

[Answer]: A

---

## Q4 — Điều phối serial hay song song

Trong một lô nhiều KH, robot xử lý các KH thế nào?

- A. Tuần tự từng KH (đơn giản, dễ truy vết, phù hợp tương tác portal có session) (gợi ý)
- B. Song song nhiều KH
- X. Other (please specify)

[Answer]: A
