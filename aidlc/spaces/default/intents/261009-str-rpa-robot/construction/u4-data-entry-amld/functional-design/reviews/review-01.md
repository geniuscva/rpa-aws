## Review

**Reviewer:** aidlc-architecture-reviewer-agent
**Verdict:** READY
**Iteration:** 1

Thiết kế chức năng U4 DataEntryAMLD nhất quán với hợp đồng pipeline và DAG: U4 là
điểm hội tụ, nhận StrRecord sau khi U2 (Accuity) và U3 (Cục Thuế) đã bồi đắp, và
chỉ ghi các cột BOT_ALMD, BOT_TINHTRANGTRASOAT, BOT_GHICHU — tôn trọng quy ước sở
hữu cột trong contract-summary.md. entities.md mô hình hoá đúng AmldSession (đăng
nhập, reload ≤ 3), StrReport (tiến độ Mẫu số 01 theo thứ tự I/II/IV/V/VI, bỏ III),
SectionTickValue (kiểm tra tick Phần IV/V), AttachmentItem (Phần VI đúng thứ tự),
RetryPolicy (≤ 3). rules.md có BR4.1–BR4.11 phủ đủ: bỏ qua record đã dừng, thứ tự
nhập bỏ Phần III, rẽ nhánh KHCN/KHDN ở Phần II, upload Phần VI đúng thứ tự, quy
tắc Phần V (6/7/8 → +4,5), chặn tick ngoài tập định nghĩa, thiếu tài liệu bắt buộc
→ email FAIL, retry ≤ 3, đăng nhập treo reload ≤ 3, ghi kết quả, không hardcode
credentials. functional-spec.md có workflow 13 bước, state machine phủ các nhánh
login-fail/missing-attachment/tick-ngoài-tập/retry-exhausted/stopped, ER diagram
dẫn xuất, scenarios đầy đủ. traceability.json phủ 9 AC của US3.1/US3.2/US3.3/US4.1/
US5.1 với target BRx.y tồn tại trong rules.md; reverse giải thích các BR hành vi
(BR4.1, BR4.7, BR4.10). Các project rule đã affirmed được phản ánh (cấm Phần III,
chặn thiếu tài liệu bắt buộc, chặn tick ngoài tập, credentials từ data/config.yaml).
Các điểm dưới là gợi ý cho các bước sau, không chặn.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Low | BR4.6 / SectionTickValue.inDefinedSet | Tập định nghĩa cụ thể cho từng mục tick Phần IV/V (danh sách giá trị hợp lệ) chưa liệt kê chi tiết; chốt ở Code Generation theo tài liệu Mẫu số 01. | Chốt tập giá trị hợp lệ Phần IV/V ở Code Generation U4. | New |
| R-02 | Low | BR4.8 / RetryPolicy | Phạm vi "một bước nhập" được bọc retry (login, mỗi Phần, mỗi upload) nên liệt kê rõ các bước áp retry khi hiện thực. | Làm rõ ranh giới bước retry ở NFR Design/Code Generation U4. | New |
| R-03 | Low | BR4.3 Phần II (KHDN) | Quy tắc chọn người đại diện "GTTT ngày cấp mới nhất" cần nguồn dữ liệu rõ ràng (sheet NDD_Thong_Tin_Dinh_Danh hoặc màn hình "Xem"); xác nhận ở Code Generation. | Chốt nguồn chọn người đại diện ở Code Generation U4. | New |
