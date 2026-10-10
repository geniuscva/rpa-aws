## Review

**Reviewer:** aidlc-architecture-reviewer-agent
**Verdict:** READY
**Iteration:** 1

Contract summary phủ đủ các ranh giới: hai hợp đồng ngoài (Kafka message, ECM
REST) và bốn ranh giới nội bộ dùng chung hợp đồng StrRecord + interface
process(StrRecord, context). Message Kafka được pin đúng theo mẫu người dùng cung
cấp (eventID, eventName=LIST_CUST_STR, cif, timeStamp) và làm rõ mỗi message là
một CIF. ECM API khớp docs/SERVICES_CONNECTION_INFO.md (auth → search → get
content) với credentials đọc từ env. Schema StrRecord liệt kê đủ cột và phân nhóm
cấu phần nào ghi cột nào, có control_fields (processingStopped, writtenBy) hỗ trợ
quy ước bỏ qua record lỗi và nhảy tới U5 — nhất quán với Q4. Quy tắc sở hữu và
thay đổi cộng-thêm an toàn rõ ràng. Sẵn sàng cho cổng; các điểm dưới là gợi ý.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Low | Contract 1 (Kafka) | Chưa chốt idempotency: message trùng (cùng eventID/cif) có thể gây xử lý lặp một CIF; đã ghi ở Open Questions. | Chốt chính sách dedup ở Functional Design. | New |
| R-02 | Low | Contract 2 (ECM) | Mapping business_code cho từng loại hồ sơ PDF chưa định; ảnh hưởng U1 khi tải đúng tài liệu. | Chốt ở Functional Design U1. | New |
| R-03 | Low | StrRecord | Mọi cột đang để kiểu string; kiểu số/ngày chính xác hoãn tới entities.md — hợp lý nhưng cần nhất quán khi tính toán số tiền. | Chốt kiểu ở Functional Design. | New |
