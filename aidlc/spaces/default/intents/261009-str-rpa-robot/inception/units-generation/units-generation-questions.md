# Units Generation — Questions

Interaction mode: Guide me.

Nhóm 12 component thành các đơn vị công việc (Unit). Vì đã chọn walking skeleton,
Unit đầu tiên là lát cắt mỏng end-to-end chạy được.

---

## Q1 — Chiến lược chia Unit

Chia Unit theo cách nào?

- A. Theo khả năng (capability) bám luồng nghiệp vụ, với Unit 1 là walking
  skeleton end-to-end dùng mock:
    - U1 skeleton: Kafka → đọc 1 CIF → (mock Accuity/AMLD/ECM) → nhập form tối
      thiểu → email trạng thái — chứng minh các mảnh nối được
    - U2 ingest: SourceDataReader đầy đủ + EcmClient (ECM mock)
    - U3 tổng hợp & tra cứu: CashFlowDiagramBuilder + AccuityLookup +
      TaxAuthorityLookup + CaptchaSolver
    - U4 nhập portal đầy đủ: AmldPortalFiller (Phần I–VI) + RetryManager
    - U5 thông báo & tổng hợp lỗi: ErrorAggregator + EmailNotifier đầy đủ
  (gợi ý)
- B. Chia theo lớp kỹ thuật (ingest / lookup / portal / notify) không có skeleton
  riêng
- C. Gộp thành ít Unit lớn (1–2 Unit)
- X. Other (please specify)

[Answer]:A

---

## Q2 — Độ mịn Unit

- A. Vừa phải: ~5 Unit như đề xuất (gợi ý)
- B. Mịn hơn (mỗi component/nhóm nhỏ một Unit)
- C. Thô hơn (2–3 Unit)
- X. Other (please specify)

[Answer]: A

---

## Q3 — Mô hình triển khai

Robot chạy local, đây là một ứng dụng chạy nền duy nhất.

- A. Một ứng dụng triển khai duy nhất (các Unit là module trong cùng một process)
  (gợi ý)
- B. Nhiều tiến trình/triển khai độc lập
- X. Other (please specify)

[Answer]:A

---

## Q4 — Loại (kind) của các Unit

Tất cả Unit đều là code chạy (service/library) của một ứng dụng robot.

- A. U1–U5 đều là `service` (một phần của robot chạy nền) (gợi ý)
- B. Tách library riêng cho phần dùng chung
- X. Other (please specify)

[Answer]: A
