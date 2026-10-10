# Build and Test Summary — Robot RPA STR

## Trạng thái build & tiền đề
- Build-ready: `.venv/bin/python -c "import main"` thành công — toàn bộ pipeline
  U1→U5 import sạch, không lỗi import/kiểu/tham chiếu.
- Test-ready: `.venv/bin/pytest` → **84 passed** (0 failed).
- Deployment-ready: ở mức chạy local (robot nền). Không có pipeline CD; chạy
  bằng `.venv/bin/python main.py` sau khi điền `data/config.yaml` và có Kafka/ECM.

## Kiểm kê loại test đã sinh
- **Unit tests** (per-unit, từ Code Generation): U1=25, U2=12, U3=12, U4=23, U5=10.
- **Integration tests** (stage này, Standard): `tests/test_integration.py` = 2
  (happy path cross-unit + nhánh dừng-sớm).
- Performance/Security test instructions: KHÔNG sinh ở mức Standard. NFR hiệu
  năng/độ chính xác là mục tiêu đo sau golive (xem ma trận bên dưới).

## Kỳ vọng coverage theo Unit
| Unit | Cấu phần | Test | Nhánh phủ |
|---|---|---|---|
| U1 | ConsumeData | 25 | Kafka parse, idempotency, resolve folder, phân loại, dòng tiền, ECM, stage e2e |
| U2 | DataEntryAccuity | 12 | map loại KH, happy KHCN/KHDN, match=100, lỗi login/lookup, record đã dừng |
| U3 | DataEntryTraCuuThue | 12 | chỉ KHDN, có/không kết quả, KHCN skip, captcha fail, lỗi web |
| U4 | DataEntryAMLD | 23 | retry ≤3, tick IV/V, đính kèm bắt buộc, thứ tự Phần VI, bỏ Phần III, stage |
| U5 | TongHopVaGuiMail | 10 | tổng hợp cô lập lỗi, Excel trạng thái, email mock/SMTP, batch |

## Target Verification Matrix
| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| TGT-TEST-SUITE | team.md Testing Posture (coverage floor + Standard) | Toàn bộ suite xanh | 84 passed, 0 failed | `.venv/bin/pytest` → 84 passed | build-and-test | Met |
| TGT-BUILD-IMPORT | build-instructions.md §3 | Import pipeline không lỗi | import main OK | `.venv/bin/python -c "import main"` exit 0 | build-and-test | Met |
| TGT-INTEG-XUNIT | build-and-test.md Step 3 (Standard) | ≥2 ranh giới cross-unit xanh | 2 passed | `tests/test_integration.py` 2 passed | build-and-test | Met |
| TGT-NFR3-RESILIENCE | requirements.md NFR3 | retry ≤3 nhập, reload ≤3 login, cô lập lỗi 1 KH | Có test khẳng định | U4 retry_policy (3), amld_stage; U5 cô lập lỗi; integration TC02 | build-and-test | Met |
| TGT-NFR4-SECRETS | requirements.md NFR4 / project.md | Không hardcode secret | config từ data/config.yaml, gitignore | robot/config.py; .gitignore; không log secret | build-and-test | Met |
| TGT-NFR6-TESTABILITY | requirements.md NFR6 | Hệ ngoài sau interface, mock được | Mọi cổng (ECM/Accuity/Tax/AMLD/Email) có Port + mock | 84 test chạy không cần dịch vụ ngoài | build-and-test | Met |
| TGT-NFR1-ACCURACY | requirements.md NFR1 | ≥90% khớp T24 (đo hàng tháng từ golive) | Chưa đo | Cần dữ liệu production sau golive | (sau golive) | Unverified |
| TGT-NFR2-RUNTIME | requirements.md NFR2 | ≤15 phút/báo cáo | Chưa đo | Cần chạy thật end-to-end với portal thật | (sau golive) | Unverified |

## Readiness
- **Build-ready / Test-ready: Đạt.** Toàn bộ logic nghiệp vụ có test xanh; pipeline
  dựng và import được; mọi hệ ngoài mock sau interface.
- **NFR1 (độ chính xác) và NFR2 (thời gian):** là mục tiêu đo lường vận hành thật
  sau golive với portal/T24 thật — không thể đo cục bộ ở stage này. Đánh dấu
  `Unverified`; không có stage validation sau trong scope `classic` local nên
  đây là giới hạn đã biết, chuyển cho giai đoạn vận hành.

## Giới hạn / mục còn tồn
- NFR1/NFR2 cần đo sau golive (production). Robot đã cài đặt đủ cơ chế (logging
  NFR5, retry NFR3) để thu thập số liệu khi chạy thật.
- Playwright/ddddocr chỉ dùng khi chạy thật; test chạy hoàn toàn trên mock.
