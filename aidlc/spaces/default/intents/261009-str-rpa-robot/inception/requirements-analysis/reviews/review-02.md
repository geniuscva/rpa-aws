## Review

**Reviewer:** aidlc-product-lead-agent
**Verdict:** READY
**Iteration:** 1

Bản requirements đã cập nhật theo các thay đổi của người yêu cầu: chạy local với
thư mục nguồn `/Users/hainguyen/Projects/RPA/AMLD/YYYYMM/YYYYMMDD`, bỏ hẳn cơ chế
LOG_DONE, bổ sung FR14 lấy hồ sơ PDF qua ECM mock API (localhost:8831) với luồng
auth → search → download rõ ràng, Kafka chuyển sang localhost:9092 không
user/pass topic RPA_STR_NHNN_INPUT, và email trạng thái dùng địa chỉ mới. Các
thay đổi nhất quán giữa FR, Constraints (C4/C7/C8), Assumptions và Out of Scope
(O2 ECM mock). ID truy vết được giữ và mở rộng hợp lý (thêm FR14, C8, OQ4 mới).
Mục tiêu nghiệp vụ và tiêu chí đo lường giữ nguyên. Sẵn sàng đưa ra cổng phê
duyệt; các điểm dưới là gợi ý, không chặn.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Low | FR1 / OQ1 | Schema message Kafka chưa định nghĩa; FR1 phụ thuộc vào nó để map message sang thư mục ngày/CIF. | Chốt schema ở giai đoạn thiết kế; đã ghi nhận ở OQ1 nên không chặn. | Unresolved |
| R-02 | Low | NFR2 | Ngưỡng ≤ 15 phút/báo cáo chưa nói rõ đo end-to-end gồm cả thời gian chờ hệ thống ngoài hay chỉ phần robot xử lý. | Làm rõ phạm vi đo khi vào NFR/thiết kế. | Unresolved |
| R-03 | Low | FR7.3 | Dựa vào ddddocr để qua captcha Cục Thuế là điểm có thể fail; chưa nêu ngưỡng số lần thử OCR trước khi coi là không có kết quả. | Định nghĩa số lần thử OCR ở thiết kế. | Unresolved |
| R-04 | Low | OQ4 | Jira FCRM-6209 đang Cancelled; phạm vi cần nghiệp vụ xác nhận lại trước khi triển khai thật. | Đã ghi nhận ở OQ4; người duyệt nên lưu ý rủi ro này. | Resolved (reviewer) |
| R-05 | Low | FR14 / OQ4 | Cách map customerCode/business_code của ECM mock sang từng CIF và từng loại hồ sơ PDF chưa định nghĩa. | Đã ghi nhận ở OQ4 mới; chốt ở thiết kế. | New |
| R-06 | Low | project.md | Rule bắt buộc LOG_DONE đã promote ở giai đoạn trước nay mâu thuẫn với quyết định bỏ LOG_DONE; cần được gỡ/điều chỉnh ở bước learnings để bộ nhớ không mâu thuẫn. | Xử lý ở nghi thức learnings cuối giai đoạn. | New |

> R-01 Reviewer note: Schema message Kafka vẫn để mở (OQ1); đúng là việc của thiết kế, không chặn.

> R-02 Reviewer note: Phạm vi đo NFR2 vẫn chưa làm rõ end-to-end hay chỉ phần robot.

> R-03 Reviewer note: Vẫn chưa nêu ngưỡng số lần thử OCR captcha; để thiết kế quyết.

> R-04 Reviewer note: Mục OQ4 cũ (Jira Cancelled) đã được gỡ khỏi bản này theo chủ ý người yêu cầu.
