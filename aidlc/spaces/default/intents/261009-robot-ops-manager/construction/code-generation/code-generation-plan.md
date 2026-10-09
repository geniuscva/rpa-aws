# Kế hoạch Code Generation — Ứng dụng quản lý vận hành robot

## Summary

- Builds: ứng dụng web cục bộ (FastAPI + SQLite + một trang HTML) để khai báo, chạy/dừng, theo dõi robot, xem lịch sử/log và cảnh báo
- Touches: thư mục mới `robot_ops/` (mã nguồn), `tests/`, `requirements.txt`, `pyproject.toml`, `README.md`, `run_app.bat` ở gốc workspace
- Tests: 14 kiểm thử `pytest` (ít nhất một cho mỗi yêu cầu FR1-FR5, NFR2, NFR3, NFR4; mỗi thành phần có test luồng thành công)

## Thiết kế ngắn

- Công nghệ: Python, FastAPI, uvicorn, SQLite (`sqlite3` chuẩn), giao diện một trang `index.html` + JavaScript thuần (polling mỗi 3 giây). Không đăng nhập; lắng nghe `127.0.0.1:8000` theo mặc định (C1-C4, NFR2).
- Thành phần:
  - `db.py` — kết nối SQLite, tạo bảng `robots`, `runs`, `alerts`.
  - `repository.py` — CRUD cho robot, run, alert.
  - `runner.py` — khởi động robot bằng `subprocess.Popen` trong thư mục làm việc đã khai báo, ghi stdout/stderr ra file log, theo dõi kết thúc bằng thread, dừng cả cây tiến trình (`taskkill /T /F` trên Windows).
  - `scheduler.py` — vòng lặp kiểm tra robot trễ lịch quá 5 phút, tạo cảnh báo.
  - `main.py` — API REST + phục vụ trang tĩnh + `/health`.
  - `static/index.html` — danh sách robot, nút Chạy/Dừng, lịch sử, log, cảnh báo.
- Trạng thái robot: `Đang chạy` nếu có run đang mở; ngược lại theo run gần nhất (`error` → `Lỗi`, còn lại `Dừng`).

## Các bước thực hiện

- [x] Step 1: Khung dự án và cấu hình: `robot_ops/__init__.py`, `requirements.txt` (fastapi, uvicorn, httpx, pytest), `pyproject.toml` (pytest, ruff dòng 100), cấu hình qua biến môi trường (`ROBOT_OPS_DB`, `ROBOT_OPS_LOG_DIR`, `ROBOT_OPS_HOST`, `ROBOT_OPS_PORT`). (NFR2, NFR4)
- [x] Step 2: Chuẩn bị test runner: `tests/conftest.py` (DB tạm, client), ghi lệnh chạy đúng phạm vi vào `unit-test-instructions.md`: `python -m pytest tests -q`. (NFR5)
- [x] Step 3: Mô hình dữ liệu / DB — cài đặt `db.py` (bảng `robots`, `runs`, `alerts`; khi khởi động đánh dấu run đang dở là `stopped`). (FR1.3, FR4.1, NFR3)
- [x] Step 4: Kiểm thử DB: `tests/test_db.py` — dữ liệu bền vững sau khi mở lại; run dở được đánh dấu `stopped`.
- [x] Step 5: Repository — cài đặt `repository.py` (CRUD robot, tạo/kết thúc run, phân trang lịch sử, tạo/xử lý cảnh báo, tính trạng thái robot). (FR1.1, FR1.2, FR2.1, FR4.2, FR5.3)
- [x] Step 6: Kiểm thử repository: `tests/test_repository.py` — tạo/sửa/xoá robot, trạng thái suy ra, phân trang lịch sử, xử lý cảnh báo.
- [x] Step 7: Logic nghiệp vụ — cài đặt `runner.py` và `scheduler.py` (chạy, chặn chạy trùng, dừng cây tiến trình, ghi log, mã thoát ≠ 0 tạo cảnh báo, trễ lịch > 5 phút tạo cảnh báo, lỗi khởi động trả thông báo). (FR3.1-FR3.3, FR4.1, FR4.3, FR5.1, FR5.2, NFR3)
- [x] Step 8: Kiểm thử logic: `tests/test_runner.py`, `tests/test_scheduler.py` — chạy lệnh thành công/lỗi (dùng `python -c`), chặn chạy trùng, dừng tiến trình, sai đường dẫn, cảnh báo trễ lịch.
- [x] Step 9: API — cài đặt `main.py` (`GET/POST/PUT/DELETE /api/robots`, `POST /api/robots/{id}/start|stop`, `GET /api/robots/{id}/runs`, `GET /api/runs/{id}/log`, `GET /api/alerts`, `POST /api/alerts/{id}/resolve`, `GET /health`; kiểm tra dữ liệu đầu vào; mặc định chỉ bind `127.0.0.1`). (FR1-FR5, NFR2, NFR4)
- [x] Step 10: Kiểm thử API: `tests/test_api.py` — luồng khai báo → chạy → xem lịch sử/log → cảnh báo → xử lý; dữ liệu sai trả 422; `/health`.
- [x] Step 11: Giao diện — `robot_ops/static/index.html` (bảng robot với trạng thái, nút Chạy/Dừng, form khai báo, lịch sử, xem log, cảnh báo; tự làm mới ≤ 5 giây). (FR2.2, FR3, FR4.2, FR4.3, FR5)
- [x] Step 12: Kiểm thử giao diện: `tests/test_ui.py` — trang chủ được phục vụ và chứa các phần tử chính (bảng robot, nút chạy/dừng, khu cảnh báo).
- [x] Step 13: Cấu hình môi trường/build: `run_app.bat` (khởi động uvicorn), logging của ứng dụng ra file. (NFR4)
- [x] Step 14: Tài liệu và truy vết: `README.md` (cài đặt, chạy, cách khai báo robot từ folder `RPA_NHAPBAOCAO_STR`, cảnh báo không có đăng nhập), `code-summary.md`, `traceability.json`.

## Truy vết yêu cầu → bước

| Yêu cầu | Bước |
|---|---|
| FR1 | 3, 5, 9 |
| FR2 | 5, 9, 11 |
| FR3 | 7, 9, 11 |
| FR4 | 3, 5, 7, 9, 11 |
| FR5 | 5, 7, 9, 11 |
| NFR1 | 5, 10 |
| NFR2 | 1, 9 |
| NFR3 | 3, 7 |
| NFR4 | 1, 9, 13 |
| NFR5 | 2, 4, 6, 8, 10, 12 |

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "org",
  "ordering": "implement each applicable testable layer, then write and run that layer's tests.",
  "scope": "express",
  "test_strategy": "minimal",
  "project_type": "greenfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    }
  ],
  "obligations": {
    "strategy": "minimal",
    "strategy_volume": [
      "One verifiable test per requirement at the narrowest effective level.",
      "At least one happy-path unit test per component.",
      "Unit tests are the default; a bugfix/security scope floor may require an integration or E2E regression when that is the narrowest level that reproduces the defect."
    ],
    "scope_floor": [
      "Keep the existing test suite green.",
      "This scope adds no extra new-test floor beyond the selected test strategy."
    ],
    "combination_rule": "Apply every selected-strategy obligation and every scope-floor obligation; neither replaces the other, and a targeted scope regression may add the narrowest necessary test type beyond the strategy default."
  },
  "plan_profile": {
    "methodology": "test-after",
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
      "Data model / database behavior - implement.",
      "Data model / database behavior - write and run its tests after implementation.",
      "Repository / data access - implement.",
      "Repository / data access - write and run its tests after implementation.",
      "Business logic - implement.",
      "Business logic - write and run its tests after implementation.",
      "API / endpoint - implement.",
      "API / endpoint - write and run its tests after implementation.",
      "Frontend behavior - implement.",
      "Frontend behavior - write and run its tests after implementation.",
      "Environment/build configuration.",
      "Documentation and traceability."
    ]
  },
  "input_sha256": "sha256:6cb23162168334768ff8f29699669845616670119c9eb58bf9bb05af6fefd3de",
  "contract_sha256": "sha256:283a836cf0757ed2efa4b5dd3135f3986eb59880b3017f4ba87a685cfebedfdb"
}
```
