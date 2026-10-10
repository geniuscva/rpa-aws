# Contract Design — Questions

Interaction mode: Guide me.

Các cấu phần là module trong một process, truyền object `StrRecord` tuần tự
U1→U5. Hợp đồng chính là schema `StrRecord` + interface mỗi cấu phần. Ngoài ra có
các ranh giới với hệ thống ngoài (Kafka message, ECM API).

---

## Q1 — Hình thức hợp đồng giữa các cấu phần

Hợp đồng U1→U2→U3→U4→U5 nên định nghĩa thế nào?

- A. Shared schema `StrRecord` + interface chung `process(StrRecord, context) -> StrRecord`
  cho mỗi cấu phần (in-process, truyền object) (gợi ý)
- B. Mỗi cấu phần là một service riêng gọi qua API nội bộ
- X. Other (please specify)

[Answer]:A

---

## Q2 — Hợp đồng message Kafka đầu vào (U1)

Message Kafka ở topic RPA_STR_NHNN_INPUT nên mang gì?

- A. Payload JSON tối thiểu: batchId, batchDate (ngày lô), danh sách CIF (hoặc
  chỉ ngày để U1 tự quét thư mục ngày) (gợi ý)
- B. Payload đầy đủ cả dữ liệu KH (không chỉ tham chiếu)
- X. Other (please specify)

[Answer]:X - message kafka :   {
        "eventID": "AUTOTEST-d0bd209b15de",
        "eventName": "LIST_CUST_STR",
        "cif": "6670501",
        "timeStamp": "1790226266242"
    }

---

## Q3 — Hợp đồng ECM API (U1 gọi ECM mock)

Hợp đồng với ECM mock theo tài liệu docs/SERVICES_CONNECTION_INFO.md:

- A. REST: POST auth token → POST search theo customerCode → GET file content
  theo doc_id (như tài liệu đã mô tả) (gợi ý)
- X. Other (please specify)

[Answer]: X theo tài liệu /docs/SERVICES_CONNECTION_INFO.md

---

## Q4 — Xử lý lỗi & bỏ qua giữa các cấu phần

Khi một cấu phần lỗi với một CIF, hợp đồng pipeline nên:

- A. Ghi trạng thái lỗi vào `StrRecord` (BOT_GHICHU + cột trạng thái của cấu phần),
  đánh dấu record là "dừng xử lý", các cấu phần sau bỏ qua record đã dừng và
  chuyển thẳng tới U5 để tổng hợp/email (gợi ý)
- B. Ném exception dừng cả pipeline của CIF đó ngay
- X. Other (please specify)

[Answer]: X - Ghi trạng thái lỗi vào `StrRecord` (BOT_GHICHU + BOT_TINHTRANGTRASOAT),
  đánh dấu record là "dừng xử lý", các cấu phần sau bỏ qua record đã dừng và
  chuyển thẳng tới U5 để tổng hợp/email (gợi ý)
