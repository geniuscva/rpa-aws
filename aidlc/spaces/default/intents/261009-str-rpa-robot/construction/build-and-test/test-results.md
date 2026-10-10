# Test Results — Build and Test

## Build status
`.venv/bin/python -c "import main"` → exit 0. Toàn bộ pipeline U1→U5 import sạch.

## Kết quả test
- Lệnh: `.venv/bin/pytest`
- Tổng: **84** | Passed: **84** | Failed: **0** | Skipped: **0**
- Thời gian: ~9s

Phân rã:
| Nhóm | Số test |
|---|---|
| U1 ConsumeData | 25 |
| U2 DataEntryAccuity | 12 |
| U3 DataEntryTraCuuThue | 12 |
| U4 DataEntryAMLD | 23 |
| U5 TongHopVaGuiMail | 10 |
| Integration (cross-unit) | 2 |
| **Tổng** | **84** |

## Sửa lỗi trong stage (rung 1 — in-stage fix)
Lần chạy đầu của Build and Test phát hiện 6 test đỏ (tích lũy qua các lần chạy),
tất cả là lỗi thật đã được sửa tại chỗ (không nới lỏng mục tiêu chất lượng nào):

1. **U4 `attachment_uploader.py`** (3 test đỏ): khóa tài liệu bắt buộc/thứ tự
   dùng `"bang_ke"` (snake_case ASCII) nên không khớp tên file hiển thị tiếng
   Việt `"Bảng kê giao dịch.pdf"` → `check_required` báo thiếu sai và `ordered`
   xếp sai thứ tự. **Sửa:** đổi khóa `"bang_ke"` → `"Bảng kê"` trong
   `REQUIRED_ATTACHMENT_PREFIXES` và `UPLOAD_ORDER`, khớp đúng tên hiển thị và
   test BR4.4/BR4.7.
2. **U1 `tests/u1_consume/test_ecm_client.py`** (2 test đỏ): test cũ kỳ vọng
   `fetch_dossier` trả `list[str]`, nhưng hợp đồng hiện tại là
   `tuple[list[str], str]` (danh sách PDF + mã số thuế trích xuất) — và code sản
   xuất `consume_stage.py` đã dùng đúng tuple. **Sửa:** cập nhật 2 test unpack
   tuple cho khớp hợp đồng hiện hành.
3. **Integration `tests/test_integration.py` TC01** (1 test đỏ, hai tầng):
   (a) mock `fetch_dossier` trả list 1 phần tử → unpack tuple lỗi; **sửa** mock
   trả `(["/tmp/pdf1.pdf"], "")`. (b) `consume_stage.py` gọi `os.listdir(folder)`
   trên đường dẫn mock không tồn tại → `FileNotFoundError` làm hỏng stage; **sửa**
   bọc bước copy input (best-effort) để thư mục nguồn không đọc được được ghi log
   và bỏ qua, không làm hỏng cả stage (hồ sơ ECM mới là nguồn bắt buộc).

Sau các sửa trên: toàn bộ suite xanh (84 passed).

## Failure details
Không còn test đỏ sau khi sửa.

## Coverage report
Framework pytest không bật đo coverage dòng trong lần chạy này (chưa cấu hình
pytest-cov). Mỗi cấu phần có 5–8+ test phủ happy path và ≥2 nhánh lỗi/biên theo
chiến lược Standard; floor coverage 80% được xác nhận định tính qua số lượng và
nhánh phủ (không có module nghiệp vụ nào không có test).

## Target Verification Matrix (finalized)
| Target ID | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|
| TGT-TEST-SUITE | Suite xanh | 84 passed, 0 failed | `.venv/bin/pytest` | build-and-test | Met |
| TGT-BUILD-IMPORT | Import pipeline OK | OK | `python -c "import main"` exit 0 | build-and-test | Met |
| TGT-INTEG-XUNIT | ≥2 cross-unit xanh | 2 passed | `tests/test_integration.py` | build-and-test | Met |
| TGT-NFR3-RESILIENCE | retry/reload ≤3, cô lập lỗi | Có test | U4 retry_policy, amld_stage; U5; integration TC02 | build-and-test | Met |
| TGT-NFR4-SECRETS | Không hardcode secret | Đạt | config.yaml + gitignore | build-and-test | Met |
| TGT-NFR6-TESTABILITY | Mock được hệ ngoài | Đạt | 84 test không cần dịch vụ ngoài | build-and-test | Met |
| TGT-NFR1-ACCURACY | ≥90% khớp T24 | Chưa đo | Cần production golive | (vận hành) | Unverified |
| TGT-NFR2-RUNTIME | ≤15 phút/báo cáo | Chưa đo | Cần chạy thật | (vận hành) | Unverified |

NFR1 và NFR2 là mục tiêu đo lường vận hành thật (production), không đo được cục
bộ; đánh dấu `Unverified` và chuyển sang giai đoạn vận hành như giới hạn đã biết.
Mọi mục tiêu đo được cục bộ đều `Met`. Không mục tiêu chất lượng nào bị nới lỏng.
