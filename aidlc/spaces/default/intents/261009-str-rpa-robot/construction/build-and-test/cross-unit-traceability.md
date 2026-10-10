# Cross-Unit Traceability — Build and Test Coverage Gate

Verdict tổng: **PASS** — mọi FR (FR1–FR14) và NFR (NFR1–NFR7) đều được một cấu
phần (U1–U5) hiện thực và có test; mọi AC trong `stories.md` đều có code tương
ứng. Hai NFR đo lường vận hành (NFR1 độ chính xác, NFR2 thời gian) không đo được
cục bộ nên đánh dấu Unverified-chuyển-vận-hành (xem Giới hạn).

## Lưu ý về ID truy vết
`traceability.json` của Code Generation từng Unit dùng lược đồ rút gọn
`US2.1..US2.5` (một ID/Unit) do Unit được định nghĩa lại thành 5 cấu phần
pipeline sau giai đoạn User Stories. Bảng dưới ánh xạ lại về **FR/NFR trong
requirements.md** và **AC trong stories.md** (nguồn chuẩn của cổng này), theo đúng
chức năng nghiệp vụ mà code hiện thực. Đây là ghi chú tài liệu, không phải thiếu
phủ.

## Phủ FR → Unit → code (có test)
| FR | Mô tả | Unit | Code chính | Test | Verdict |
|---|---|---|---|---|---|
| FR1 | Nhận việc qua Kafka | U1 | kafka_consumer.py, idempotency.py | U1 | OK |
| FR2 | Nhận diện thư mục nguồn theo ngày | U1 | source_folder.py | U1 | OK |
| FR3 | Kiểm tra đủ dữ liệu + ECM | U1 | source_folder.py, ecm_client.py | U1 | OK |
| FR4 | Phân loại KHCN/KHDN | U1 | classifier.py | U1 | OK |
| FR5 | Sơ đồ dòng tiền | U1 | cashflow.py | U1 | OK |
| FR6 | Tra cứu Accuity | U2 | accuity_adapter.py, accuity_stage.py | U2 | OK |
| FR7 | Tra cứu Cục Thuế (KHDN, ddddocr) | U3 | tax_authority_adapter.py, captcha_solver.py, tax_stage.py | U3 | OK |
| FR8 | Đăng nhập AMLD Portal (reload ≤3) | U4 | amld_portal_adapter.py | U4 | OK |
| FR9 | Nhập Mẫu số 01 I/II/IV/V/VI, bỏ III | U4 | amld_stage.py, tick_validator.py, attachment_uploader.py | U4 | OK |
| FR10 | Chặn tick ngoài tập | U4 | tick_validator.py | U4 | OK |
| FR11 | Retry ≤3 + email thất bại | U4/U5 | retry_policy.py, email_sender.py | U4/U5 | OK |
| FR12 | Tổng hợp lỗi theo KH | U5 | result_builder.py | U5 | OK |
| FR13 | Gửi email trạng thái lô | U5 | status_report.py, email_sender.py, tonghop_stage.py | U5 | OK |
| FR14 | Lấy hồ sơ qua ECM mock API | U1 | ecm_client.py | U1 | OK |

## Phủ NFR
| NFR | Mô tả | Hiện thực | Verdict |
|---|---|---|---|
| NFR1 | Độ chính xác ≥90% (đo hàng tháng từ golive) | Logic nhập đầy đủ; đo được sau production | Unverified (vận hành) |
| NFR2 | ≤15 phút/báo cáo | Pipeline tự động; đo được khi chạy thật | Unverified (vận hành) |
| NFR3 | Độ bền lỗi hệ ngoài (retry/reload ≤3, cô lập lỗi) | retry_policy.py, amld reload, U5 cô lập lỗi | OK (có test) |
| NFR4 | Không hardcode secret | config.py đọc data/config.yaml, gitignore | OK |
| NFR5 | Lưu vết logging | logging_setup.py (JSON lines), ghi log mỗi bước | OK |
| NFR6 | Khả năng kiểm thử (mock sau interface) | Mọi cổng có Port + mock; 84 test không cần dịch vụ ngoài | OK |
| NFR7 | Môi trường vận hành local | Chạy local, Kafka/ECM mock; main.py | OK |

## Phủ AC (stories.md) → code
| Nhóm AC | Unit hiện thực | Verdict |
|---|---|---|
| AC1.1.* (Kafka) | U1 kafka_consumer/idempotency | OK |
| AC1.2.* (thư mục ngày) | U1 source_folder | OK |
| AC1.3.* (file bắt buộc) | U1 source_folder | OK |
| AC1.4.* (ECM) | U1 ecm_client | OK |
| AC1.5.* (phân loại) | U1 classifier | OK |
| AC2.1.* (dòng tiền) | U1 cashflow | OK |
| AC2.2.* (Accuity) | U2 | OK |
| AC2.3.* (Cục Thuế KHDN) | U3 | OK |
| AC3.1.* (đăng nhập AMLD) | U4 amld_portal_adapter | OK |
| AC3.2.* (Mẫu 01 I/II/IV/V/VI, bỏ III, Phần V 6/7/8→+4,5, thứ tự Phần VI) | U4 amld_stage/tick_validator/attachment_uploader | OK |
| AC3.3.* (chặn tick ngoài tập) | U4 tick_validator | OK |
| AC4.1.* (retry ≤3) | U4 retry_policy | OK |
| AC4.2.* (email thất bại) | U4/U5 | OK |
| AC4.3.* (cô lập lỗi KH) | U5 result_builder + pipeline | OK |
| AC5.1.* (không hardcode) | config.py | OK |
| AC5.2.* (logging) | logging_setup.py | OK |
| AC6.1.* (tổng hợp lô) | U5 status_report | OK |
| AC6.2.* (gửi email) | U5 email_sender/tonghop_stage | OK |

## Phần tử chưa phủ
Không có FR/NFR/AC nghiệp vụ nào chưa phủ. Toàn bộ có code + test tương ứng (84
test xanh).

## Giới hạn đã biết
- NFR1 (độ chính xác ≥90% so T24) và NFR2 (≤15 phút/báo cáo) là mục tiêu **đo
  lường vận hành thật** sau golive với portal/T24 production — không đo được ở
  stage này. Chuyển cho giai đoạn vận hành; robot đã có logging (NFR5) để thu số
  liệu.
- Lược đồ ID trong `traceability.json` từng Unit là US2.1..US2.5 (một ID/Unit),
  khác lược đồ chi tiết trong stories.md; bảng trên đã ánh xạ lại theo chức năng.
