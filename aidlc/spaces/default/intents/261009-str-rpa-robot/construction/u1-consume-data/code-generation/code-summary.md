# Code Summary — U1 ConsumeData

## Những gì đã xây

Khởi tạo khung dự án Python dùng chung cho cả robot và cài đặt đầy đủ cấu phần U1
(ConsumeData). Code ở gốc workspace dưới `robot/`.

### Khung dùng chung (robot/)
- `models.py` — `StrRecord` (object pipeline, các cột theo contract-summary),
  `KafkaStrEvent`, `CustomerType`, `CashFlowSide`. StrRecord có `stop()` ghi lỗi +
  `processing_stopped`, `to_status_row()` cho U5.
- `config.py` — `ConfigProvider`/`load_config` đọc `data/config.yaml` (secrets ở
  file, không hardcode).
- `logging_setup.py` — `StructuredLogger` ghi JSON lines (timestamp/level/message).
- `pipeline.py` — interface `PipelineStage.process(record, context)` + `run_pipeline`
  bỏ qua record đã dừng (trừ cấu phần cuối).

### Cấu phần U1 (robot/u1_consume/)
- `kafka_consumer.py` — nhận & parse message, bỏ qua message lỗi (BR1.1).
- `idempotency.py` — chống trùng theo eventID (BR1.2).
- `source_folder.py` — resolve thư mục CIF theo ngày + kiểm file bắt buộc (FR2/FR3).
- `classifier.py` — phân loại KHCN/KHDN theo file (BR1.3).
- `excel_reader.py` — đọc 5 file excel (openpyxl).
- `ecm_client.py` — `EcmClientAdapter` auth→search(nhiều business_code)→download,
  timeout+retry, transport ẩn sau interface để mock (FR14, BR1.5).
- `cashflow.py` — `CashFlowCalculator` (công thức US2) + `CashFlowPdfRenderer`
  xuất Minh Họa Dòng Tiền.pdf (BR1.6/BR1.8).
- `consume_stage.py` — `ConsumeDataStage.process()` ghép toàn bộ, dựng StrRecord,
  xử lý lỗi (BR1.7).

## Test
- 25 test (pytest), tất cả PASS. Mock Kafka message và ECM transport; folder/excel
  tạm bằng openpyxl.
- Phủ: parse message (hợp lệ/thiếu field/sai eventName/non-json), idempotency,
  resolve folder + thiếu file, phân loại KHCN/KHDN, công thức dòng tiền (vào/ra/
  rỗng/sai số), ECM (gom PDF/lỗi token/không có file), và consume stage end-to-end
  (happy KHCN/KHDN, thiếu folder, lỗi ECM).
- Lệnh: `pytest` → `25 passed`.

## Lưu ý
- `data/config.yaml` không commit (.gitignore); dùng `data/config.example.yaml` làm mẫu.
- Reportlab/kafka/httpx chưa cần cho test (import tại chỗ / mock); khai báo ở requirements.txt cho chạy thật.
