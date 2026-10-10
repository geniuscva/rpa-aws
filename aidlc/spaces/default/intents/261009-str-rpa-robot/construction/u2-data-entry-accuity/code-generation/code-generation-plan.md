# Code Generation Plan — U2 DataEntryAccuity

Viết code cấu phần U2: truy cập web Accuity mock, tra cứu theo tên KH, export
`Tra cứu Accuity.pdf`, cập nhật `StrRecord.BOT_ACCUITY`. Code ở `robot/u2_accuity/`.
Dùng khung chung (`robot/models.py`, `pipeline.py`, `config.py`, `logging_setup.py`)
đã có từ U1.

## Cấu trúc

```
robot/u2_accuity/
  __init__.py
  accuity_adapter.py   # AccuityAdapter interface + hiện thực Playwright + mock
  accuity_stage.py     # AccuityStage.process(record, context) -> record
tests/u2_accuity/
  test_accuity_stage.py
  test_accuity_adapter.py
```

## Các bước

- [ ] B1. accuity_adapter.py: interface AccuityPort (login, lookup, export_pdf);
  hiện thực PlaywrightAccuityAdapter (production) + để test mock. Credentials từ
  config. (US2.2 / FR6)
- [ ] B2. accuity_stage.py: AccuityStage.process() — chọn Entity Type theo loại KH,
  tra cứu theo STR_TEN_KH, export Tra cứu Accuity.pdf; Match Score 100 → print hồ
  sơ; ghi BOT_ACCUITY; lỗi → ghi StrRecord + processing_stopped. (BR cho FR6)
- [ ] B3. Unit tests: happy (KHCN/KHDN), lỗi đăng nhập, không có kết quả; mock
  AccuityPort. (TDD)

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
Lệnh kiểm tra: `.venv/bin/pytest`. Mock AccuityPort trong test. Lưu ý: các lớp
"API / endpoint" và "Frontend behavior" trong profile không áp dụng cho U2 (robot
nền, không API/UI) nên bỏ qua.

## Traceability
- US2.2 → B1, B2
