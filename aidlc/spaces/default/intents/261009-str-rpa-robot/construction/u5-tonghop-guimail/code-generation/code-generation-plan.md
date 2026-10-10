# Code Generation Plan — U5 TongHopVaGuiMail

## Summary

Viết code cấu phần U5: chặng cuối pipeline, chạy MỘT LẦN cho cả lô sau khi mọi CIF
đã qua U1–U4. Tổng hợp trạng thái từng CIF (gồm cả KH lỗi/dừng luồng — BR5.1,
BR5.5), dựng file Excel trạng thái đúng cột STT/STR_CIF/Trạng thái/Mã lỗi/Chi tiết
lỗi (BR5.2), dựng email lô (From/To người lập/Cc, đính kèm Excel — BR5.3) và gửi
qua mail exchange; KH thất bại sau 3 retry nằm trong email lô (BR5.4). Lỗi gửi mail
→ ghi log, giữ nguyên report đã dựng (BR5.3). Thông tin mail đọc từ
`data/config.yaml`, không hardcode (BR5.7/NFR4). Code ở `robot/u5_tonghop/`. Dùng
khung chung đã có từ U1.

## Cấu trúc

```
robot/u5_tonghop/
  __init__.py
  result_builder.py        # ResultBuilder: StrRecord -> ProcessingResult (SUCCESS/FAIL)
  status_report.py         # BatchStatusReport: dựng file Excel đúng cột
  email_sender.py          # EmailPort (interface) + mock + impl + StatusEmail builder
  tonghop_stage.py         # TongHopStage.process_batch(records, context) -> BatchResult
tests/u5_tonghop/
  test_result_builder.py
  test_status_report.py
  test_tonghop_stage.py
```

## Các bước

- [ ] B1. result_builder.py: `ResultBuilder.build(record)` → `ProcessingResult`
  (status=FAIL nếu processing_stopped hoặc có BOT_* lỗi, ngược lại SUCCESS; lấy
  errorCode/errorDetail từ BOT_GHICHU/BOT_TINHTRANGTRASOAT). KH lỗi vẫn có một
  hàng (BR5.1, BR5.5). (US2.5 / FR12)
- [ ] B2. status_report.py: `BatchStatusReport.write(results, path)` dựng file
  Excel với đúng cột STT, STR_CIF, Trạng thái, Mã lỗi, Chi tiết lỗi (BR5.2); đánh
  STT theo thứ tự. Dùng openpyxl (import trễ, mock/kiểm tra được). (BR5.2)
- [ ] B3. email_sender.py: `EmailPort` (interface gửi mail) + mock + impl SMTP;
  `StatusEmail` builder (From/To=EMAIL_NGUOI_LAP_BAO_CAO/Cc từ config, đính kèm
  Excel, tiêu đề/nội dung template). Credentials/endpoint từ config (BR5.7). Gửi
  lỗi → trả trạng thái lỗi, không raise làm hỏng report (BR5.3). (BR5.3, BR5.7)
- [ ] B4. tonghop_stage.py: `TongHopStage.process_batch(records, context)` —
  dựng ProcessingResult cho mọi CIF (BR5.1, cô lập lỗi BR5.5), ghi Excel (BR5.2),
  dựng + gửi email lô (BR5.3, BR5.4); gửi lỗi → ghi log, giữ report (BR5.3); trả
  `BatchResult` (report_path, sent, sent_at/err). (BR5.1-5.7)
- [ ] B5. Unit tests TDD: lô toàn SUCCESS; lô có KH lỗi (cô lập, vẫn một email);
  record dừng luồng → hàng FAIL với mã lỗi; cột Excel đúng; gửi mail lỗi → giữ
  report + log; mock EmailPort + openpyxl.

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

Lệnh kiểm tra: `.venv/bin/pytest`. Mock EmailPort + openpyxl trong test (không gửi
mail thật). Các lớp "API / endpoint" và "Frontend behavior" trong profile không áp
dụng cho U5.

## Traceability
- US2.5 → B1, B2, B3, B4
