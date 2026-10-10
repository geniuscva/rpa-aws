# Code Generation Plan — U4 DataEntryAMLD

## Summary

Viết code cấu phần U4: điểm hội tụ U2+U3, nhập Mẫu số 01 lên AMLD Online Portal
(web thật) cho một CIF. Nhập theo thứ tự Phần I → II → IV → V → VI, **BỎ Phần
III** (BR4.2). Kiểm tra tài liệu bắt buộc trước khi nộp (BR4.7), kiểm giá trị
tick Phần IV/V trong tập cho phép (BR4.6), quy tắc Phần V 6/7/8 → +4,5 (BR4.5),
upload Phần VI đúng thứ tự (BR4.4), retry ≤ 3 lần mỗi bước (BR4.8) và đăng nhập
treo reload ≤ 3 lần (BR4.9), ghi `BOT_ALMD` + `BOT_TINHTRANGTRASOAT` (BR4.10).
Credentials/endpoint từ `data/config.yaml`, không hardcode (BR4.11/NFR4). Code ở
`robot/u4_amld/`. Dùng khung chung đã có từ U1. Ràng buộc project.md được tuân
thủ: KHÔNG điền Phần III; KHÔNG nộp khi thiếu đính kèm bắt buộc (email FAIL ở
U5); KHÔNG đi tiếp khi giá trị tick ngoài tập hợp.

## Cấu trúc

```
robot/u4_amld/
  __init__.py
  amld_portal_adapter.py   # AmldPortalPort (interface) + Playwright impl + mock + AmldSession
  retry_policy.py          # RetryPolicy: thử ≤ max_attempts lần rồi báo thất bại
  tick_validator.py        # TickValidator: kiểm tick Phần IV/V trong tập cho phép + quy tắc 6/7/8→+4,5
  attachment_uploader.py   # AttachmentUploader: kiểm tài liệu bắt buộc + thứ tự upload Phần VI
  amld_stage.py            # AmldStage.process(record, context) -> record
tests/u4_amld/
  test_amld_stage.py
  test_retry_policy.py
  test_tick_validator.py
  test_attachment_uploader.py
```

## Các bước

- [ ] B1. amld_portal_adapter.py: `AmldPortalPort` (login, open_form, fill_section,
  upload, submit...) + `AmldSession` (username từ record, password/endpoint từ
  config — BR4.11); hiện thực Playwright (production) + mock (test). Đăng nhập
  treo → reload ≤ 3 lần (BR4.9). (US2.4 / FR8, FR9)
- [ ] B2. retry_policy.py: `RetryPolicy.run(step)` thử ≤ `max_attempts` (mặc định
  3); vẫn lỗi → raise để stage dừng record + failover (BR4.8, NFR3). (BR4.8)
- [ ] B3. tick_validator.py: `TickValidator` kiểm mỗi giá trị tick Phần IV/V thuộc
  tập cho phép (BR4.6 — ngoài tập → lỗi, KHÔNG đi tiếp); áp quy tắc Phần V nếu tập
  chứa 6/7/8 thì thêm 4 và 5 (BR4.5). (BR4.5, BR4.6)
- [ ] B4. attachment_uploader.py: `AttachmentUploader` kiểm đủ tài liệu bắt buộc
  (Bảng kê, Minh Họa Dòng Tiền.pdf, Hồ sơ mở tài khoản) trước khi nộp — thiếu →
  lỗi, KHÔNG nộp (BR4.7); sắp xếp upload Phần VI đúng thứ tự cố định (BR4.4). (BR4.4, BR4.7)
- [ ] B5. amld_stage.py: `AmldStage.process()` — bỏ qua record đã dừng (BR4.1);
  kiểm tài liệu (BR4.7); đăng nhập (BR4.9); nhập I→II(rẽ KHCN/KHDN, BR4.3)→IV→V→VI,
  BỎ III (BR4.2), mỗi bước bọc RetryPolicy (BR4.8); dùng TickValidator cho IV/V;
  dùng AttachmentUploader cho VI; thành công → `BOT_ALMD=OK` + `BOT_TINHTRANGTRASOAT`;
  lỗi/thiếu tài liệu/tick ngoài tập → `BOT_ALMD=ERROR` + stop() + BOT_GHICHU (BR4.6,
  BR4.7, BR4.10). (BR4.1-4.11)
- [ ] B6. Unit tests TDD: happy KHCN & KHDN; bỏ Phần III; thiếu tài liệu bắt buộc →
  không nộp; tick ngoài tập → dừng; Phần V 6/7/8 → +4,5; retry fail quá 3 lần →
  dừng; đăng nhập treo quá 3 lần → dừng; record đã dừng → bỏ qua. Mock
  `AmldPortalPort`.

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

Lệnh kiểm tra: `.venv/bin/pytest`. Mock AMLD Portal trong test (không chạm web
thật). Các lớp "API / endpoint" và "Frontend behavior" trong profile không áp
dụng cho U4.

## Traceability
- US2.4 → B1, B2, B3, B4, B5
