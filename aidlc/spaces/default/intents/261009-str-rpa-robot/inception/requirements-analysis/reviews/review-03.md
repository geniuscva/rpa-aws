## Review

**Reviewer:** aidlc-product-lead-agent
**Verdict:** READY
**Iteration:** 1

Chỉnh sửa duy nhất ở lần này là giao thức Kafka: `localhost:9092` chuyển từ
SASL_PLAINTEXT sang PLAINTEXT, nhất quán ở cả FR1.1 và C7. Phần còn lại của bản
requirements giữ nguyên và vẫn nhất quán. Sẵn sàng đưa ra cổng phê duyệt; các
điểm mở còn lại là việc của thiết kế, không chặn.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Low | FR1 / OQ1 | Schema message Kafka chưa định nghĩa; FR1 phụ thuộc vào nó để map message sang thư mục ngày/CIF. | Chốt schema ở giai đoạn thiết kế; đã ghi nhận ở OQ1 nên không chặn. | Unresolved |
| R-02 | Low | NFR2 | Ngưỡng ≤ 15 phút/báo cáo chưa nói rõ đo end-to-end gồm cả thời gian chờ hệ thống ngoài hay chỉ phần robot xử lý. | Làm rõ phạm vi đo khi vào NFR/thiết kế. | Unresolved |
| R-03 | Low | FR7.3 | Dựa vào ddddocr để qua captcha Cục Thuế là điểm có thể fail; chưa nêu ngưỡng số lần thử OCR trước khi coi là không có kết quả. | Định nghĩa số lần thử OCR ở thiết kế. | Unresolved |
| R-04 | Low | OQ4 | Jira FCRM-6209 đang Cancelled; phạm vi cần nghiệp vụ xác nhận lại trước khi triển khai thật. | Đã ghi nhận ở OQ4; người duyệt nên lưu ý rủi ro này. | Resolved (reviewer) |
| R-05 | Low | FR14 / OQ4 | Cách map customerCode/business_code của ECM mock sang từng CIF và từng loại hồ sơ PDF chưa định nghĩa. | Đã ghi nhận ở OQ4 mới; chốt ở thiết kế. | New |
| R-06 | Low | project.md | Rule bắt buộc LOG_DONE đã promote ở giai đoạn trước nay mâu thuẫn với quyết định bỏ LOG_DONE; cần được gỡ/điều chỉnh ở bước learnings để bộ nhớ không mâu thuẫn. | Xử lý ở nghi thức learnings cuối giai đoạn. | New |

> R-01 Not re-checked this round

> R-02 Not re-checked this round

> R-03 Not re-checked this round

> R-05 Not re-checked this round

> R-06 Not re-checked this round
