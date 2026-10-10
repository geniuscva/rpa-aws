# Code Generation Plan — U1 ConsumeData

Kế hoạch viết code cho cấu phần U1. Ngôn ngữ Python 3.11+. Code ứng dụng đặt ở
gốc workspace. Mỗi bước có checkbox; developer tick khi hoàn thành.

## Cấu trúc dự án (khởi tạo ở U1, dùng chung cả robot)

```
rpa_aws/
  robot/
    __init__.py
    config.py            # ConfigProvider đọc data/config.yaml
    logging_setup.py     # StructuredLogger (JSON: timestamp/level/message)
    models.py            # StrRecord và các dataclass dùng chung (hợp đồng)
    pipeline.py          # PipelineStage interface: process(record, context)
    u1_consume/
      __init__.py
      kafka_consumer.py  # KafkaConsumerAdapter + parse KafkaStrEvent
      idempotency.py     # IdempotencyStore (ProcessedEvent)
      source_folder.py   # SourceFolderResolver
      excel_reader.py    # ExcelReader (5 file)
      classifier.py      # CustomerClassifier (KHCN/KHDN)
      ecm_client.py      # EcmClientAdapter (auth/search/download) + interface
      cashflow.py        # CashFlowCalculator + CashFlowPdfRenderer
      consume_stage.py   # ConsumeDataStage: process(record, context) -> record
  data/
    config.example.yaml  # mẫu cấu hình (không secret thật)
  tests/
    u1_consume/          # test cho U1
  requirements.txt
  .gitignore             # loại data/config.yaml, output, logs
```

## Các bước

- [ ] B1. Khởi tạo cấu trúc dự án + requirements.txt + .gitignore (loại data/config.yaml) (hạ tầng dự án)
- [ ] B2. models.py: dataclass StrRecord (các cột theo contract-summary) + KafkaStrEvent, control fields processingStopped/writtenBy — (US nền, hợp đồng)
- [ ] B3. pipeline.py: interface PipelineStage.process(record, context); StageContext (config, logger) — (hợp đồng)
- [ ] B4. config.py: ConfigProvider đọc data/config.yaml; config.example.yaml — (US5.1 / SEC-U1-1)
- [ ] B5. logging_setup.py: StructuredLogger JSON lines (timestamp/level/message) — (US5.2 / OBS-U1-1)
- [ ] B6. kafka_consumer.py: KafkaConsumerAdapter, parse + validate KafkaStrEvent (BR1.1), bỏ qua message lỗi — (US1.1 / FR1)
- [ ] B7. idempotency.py: IdempotencyStore kiểm/ghi eventID (BR1.2) — (US1.1 / REL-U1-3)
- [ ] B8. source_folder.py: SourceFolderResolver quét thư mục ngày khớp CIF (BR...) — (US1.2 / FR2)
- [ ] B9. excel_reader.py: đọc 5 file excel, trích cột StrRecord — (US1.3)
- [ ] B10. classifier.py: CustomerClassifier KHCN/KHDN theo file (BR1.3) — (US1.5 / FR4)
- [ ] B11. kiểm đủ file bắt buộc (BR1.4), thiếu → processingStopped — (US1.3 / FR3)
- [ ] B12. ecm_client.py: EcmClientAdapter auth→search(nhiều business_code)→download PDF, timeout+retry (BR1.5) — (US1.4 / FR14)
- [ ] B13. cashflow.py: CashFlowCalculator (công thức US2) + CashFlowPdfRenderer xuất Minh Họa Dòng Tiền.pdf (BR1.6/BR1.8) — (US2.1 / FR5)
- [ ] B14. consume_stage.py: ConsumeDataStage.process() ghép các bước, dựng StrRecord, xử lý lỗi (BR1.7) — (US1.x)
- [ ] B15. Unit tests: happy KHCN/KHDN, thiếu file, lỗi ECM, message trùng, tính dòng tiền — (TDD, >=2 edge case/bước)
- [ ] B16. Mock cho Kafka & ECM trong test (NFR6)

## Testing Contract
```json
{
  "version": 1,
  "methodology": "tdd",
  "source": "team",
  "ordering": "For each testable layer (file-ingestion and LOG_DONE checks, data aggregation and mapping, external lookups, portal form-fill, email notification), write the failing test first, then implement until it passes, then refactor.",
  "scope": "classic",
  "test_strategy": "standard",
  "project_type": "greenfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    },
    {
      "layer": "team",
      "text": "- **Methodology**: tdd\n- **Methodology evidence**: The team affirmed test-driven development — write\n  the test first, then the code that makes it pass. The STR robot's logic is\n  specified by concrete source-file mappings and the seven acceptance scenarios,\n  which translate cleanly into tests written ahead of implementation.\n- **Ordering**: For each testable layer (file-ingestion and LOG_DONE checks,\n  data aggregation and mapping, external lookups, portal form-fill, email\n  notification), write the failing test first, then implement until it passes,\n  then refactor.\n- Coverage floor: 80% line coverage, run in CI before merge (classic scope\n  default).\n- Test types: unit tests for data-aggregation and mapping logic (cash-flow\n  diagram counts, Phần IV/V derivation rules); integration/contract tests for\n  folder-ingestion and LOG_DONE checks; scenario tests covering the seven\n  acceptance scenarios (success, missing file, incomplete log, Accuity login\n  failure, retry, failover, batch email).\n- External systems (AMLD Portal, Accuity, Tax Authority) are mocked/stubbed in\n  automated tests; live interaction is verified separately."
    }
  ],
  "obligations": {
    "strategy": "standard",
    "strategy_volume": [
      "Five to eight tests per component.",
      "Unit tests plus integration tests for key boundaries.",
      "Add E2E, performance, or security tests when requirements demand them."
    ],
    "scope_floor": [
      "Keep the existing test suite green.",
      "This scope adds no extra new-test floor beyond the selected test strategy."
    ],
    "combination_rule": "Apply every selected-strategy obligation and every scope-floor obligation; neither replaces the other, and a targeted scope regression may add the narrowest necessary test type beyond the strategy default."
  },
  "plan_profile": {
    "methodology": "tdd",
    "runner_step": "Bootstrap the minimal test runner/configuration and record the exact unit-scoped command.",
    "runner_ready_before_first_test": true,
    "testable_layers": [
      "Data model / database behavior",
      "Repository / data access",
      "Business logic",
      "API / endpoint",
      "Frontend behavior"
    ],
    "steps": [
      "Project structure and production configuration skeleton.",
      "Bootstrap the minimal test runner/configuration and record the exact unit-scoped command.",
      "Data model / database behavior - Red: write the failing tests and record the failing command output.",
      "Data model / database behavior - Green: implement only enough behavior to pass.",
      "Data model / database behavior - Refactor: improve the implementation while tests stay green.",
      "Repository / data access - Red: write the failing tests and record the failing command output.",
      "Repository / data access - Green: implement only enough behavior to pass.",
      "Repository / data access - Refactor: improve the implementation while tests stay green.",
      "Business logic - Red: write the failing tests and record the failing command output.",
      "Business logic - Green: implement only enough behavior to pass.",
      "Business logic - Refactor: improve the implementation while tests stay green.",
      "API / endpoint - Red: write the failing tests and record the failing command output.",
      "API / endpoint - Green: implement only enough behavior to pass.",
      "API / endpoint - Refactor: improve the implementation while tests stay green.",
      "Frontend behavior - Red: write the failing tests and record the failing command output.",
      "Frontend behavior - Green: implement only enough behavior to pass.",
      "Frontend behavior - Refactor: improve the implementation while tests stay green.",
      "Environment/build configuration.",
      "Documentation and traceability."
    ]
  },
  "input_sha256": "sha256:9428f3c5d56dad3330d0e1998fa7e40c612a950fde619e5890b229d643f86f8a",
  "contract_sha256": "sha256:1d58533d1ef4f47c922b5771eb12135e2cd9faab9f9a7ff8e661728eeb9c2da6"
}
```

Lưu ý: Testing Contract trên là nguồn chuẩn (TDD, chiến lược standard, 5–8 test/
component). Kế hoạch bước ở trên bám theo lớp testable; các lớp "API/endpoint" và
"Frontend behavior" không áp dụng cho U1 (robot nền, không có API/UI) nên bỏ qua.
Lệnh kiểm tra: `pytest`.

## Traceability (story → bước)

- US1.1 → B6, B7
- US1.2 → B8
- US1.3 → B9, B11
- US1.4 → B12
- US1.5 → B10
- US2.1 → B13
- US5.1 → B4
- US5.2 → B5
