# Unit Test Instructions — U1 ConsumeData

Posture: TDD. Framework: pytest. Sàn coverage: 80% (classic). Hệ thống ngoài
(Kafka, ECM) được mock; không chạm hệ thống thật trong test.

## Phạm vi test

| Lớp | Happy path | Edge/error (>=2) |
|---|---|---|
| KafkaConsumerAdapter | message hợp lệ → KafkaStrEvent | message thiếu field; eventName sai |
| IdempotencyStore | eventID mới → xử lý | eventID trùng → bỏ qua |
| SourceFolderResolver | tìm thấy thư mục CIF | không tìm thấy; nhiều thư mục |
| ExcelReader | đọc đủ 5 file | file hỏng; thiếu cột |
| CustomerClassifier | có file cá nhân → KHCN; tổ chức → KHDN | không có cả hai |
| Required-file check | đủ file → tiếp | thiếu file → processingStopped=true |
| EcmClientAdapter (mock) | search+download trả PDF | ECM timeout; không có hồ sơ |
| CashFlowCalculator | tính đúng vào/ra theo mẫu | bảng kê rỗng; HUONG_GD lạ |
| ConsumeDataStage | dựng StrRecord đầy đủ | lỗi giữa chừng → processingStopped |

## Fixtures

- Bộ 5 file excel mẫu (KHCN và KHDN) trong tests/fixtures.
- Mock ECM server/response theo docs/SERVICES_CONNECTION_INFO.md (auth/search/download).
- Mock Kafka message theo hợp đồng {eventID, eventName, cif, timeStamp}.

## Quy tắc

- Không viết test luôn-đúng (assert True).
- Test chạy không cần dựng hệ thống thật.
- Kiểm cả quy tắc nghiệp vụ: BR1.1–BR1.8.
