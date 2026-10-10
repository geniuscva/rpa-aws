# Contract Summary — Robot RPA nhập liệu STR

Các hợp đồng chính thức mà hệ thống phải tôn trọng. Pipeline nội bộ truyền object
`StrRecord` tuần tự U1→U5; ngoài ra có hai hợp đồng với hệ thống ngoài (Kafka,
ECM). Mỗi message Kafka tương ứng **một CIF** (một khách hàng cần xử lý).

## Contracts table

| # | Provider | Consumer | Mechanism | Owner |
|---|---|---|---|---|
| 1 | External: Kafka (RPA_STR_NHNN_INPUT) | U1 ConsumeData | async message (JSON) | U1 |
| 2 | External: ECM mock (localhost:8831) | U1 ConsumeData | sync REST | U1 |
| 3 | U1 ConsumeData | U2 DataEntryAccuity | in-process shared schema (StrRecord) | shared |
| 4 | U2 DataEntryAccuity | U3 DataEntryTraCuuThue | in-process shared schema (StrRecord) | shared |
| 5 | U3 DataEntryTraCuuThue | U4 DataEntryAMLD | in-process shared schema (StrRecord) | shared |
| 6 | U4 DataEntryAMLD | U5 TongHopVaGuiMail | in-process shared schema (StrRecord) | shared |

## Contract 1 — Kafka input message (một CIF mỗi message)

```yaml
# AsyncAPI (rút gọn)
asyncapi: 2.6.0
info:
  title: STR input events
  version: 1.0.0
channels:
  RPA_STR_NHNN_INPUT:
    subscribe:
      message:
        name: ListCustStrEvent
        contentType: application/json
        payload:
          type: object
          required: [eventID, eventName, cif, timeStamp]
          properties:
            eventID:
              type: string
              example: "AUTOTEST-d0bd209b15de"
            eventName:
              type: string
              const: "LIST_CUST_STR"
            cif:
              type: string
              example: "6670501"
            timeStamp:
              type: string
              description: epoch millis dạng chuỗi
              example: "1790226266242"
# Broker: localhost:9092, PLAINTEXT, không user/pass
# Mỗi message = một CIF cần xử lý; U1 dùng cif để quét thư mục ngày và gọi ECM.
```

## Contract 2 — ECM mock REST API

Theo `docs/SERVICES_CONNECTION_INFO.md` (Mock Server FastAPI, base URL
`http://localhost:8831`). Credentials đọc từ cấu hình/biến môi trường (không
hardcode).

```yaml
# OpenAPI (rút gọn) — ECM mock
openapi: 3.0.3
info:
  title: ECM mock API
  version: 1.0.0
servers:
  - url: http://localhost:8831
paths:
  /auth/realms/ms-core/protocol/openid-connect/token:
    post:
      summary: Lấy access token (client_credentials)
      requestBody:
        content:
          application/x-www-form-urlencoded:
            schema:
              type: object
              required: [grant_type, client_id, client_secret]
              properties:
                grant_type: { type: string, const: client_credentials }
                client_id: { type: string }
                client_secret: { type: string }
      responses:
        '200':
          description: Token
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token: { type: string }
  /ecm-core-v1.0/businesses/{business_code}/files/search:
    post:
      summary: Tìm file hồ sơ theo customerCode
      parameters:
        - name: business_code
          in: path
          required: true
          schema: { type: string }
          description: "mb_smart_channel | customer_info_ca | ss_customer_doc | ss_auto_upload_customer_info | customer_information | biz_onboarding"
      security: [ { bearerAuth: [] } ]
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                metadata:
                  type: object
                  properties:
                    customerCode:
                      type: object
                      properties:
                        type: { type: string, example: eq }
                        value: { type: string, example: "6670501" }
                pagination:
                  type: object
                  properties:
                    page: { type: integer, example: 1 }
                    size: { type: integer, example: 100 }
      responses:
        '200': { description: Danh sách file (doc_id, metadata) }
  /ecm-core-v1.0/files/{doc_id}/content:
    get:
      summary: Tải nội dung file (PDF)
      parameters:
        - name: doc_id
          in: path
          required: true
          schema: { type: string }
          example: mb01e9fed8047d5c
      security: [ { bearerAuth: [] } ]
      responses:
        '200':
          description: File PDF
          content:
            application/pdf: {}
components:
  securitySchemes:
    bearerAuth: { type: http, scheme: bearer }
```

## Contracts 3–6 — Hợp đồng pipeline nội bộ (StrRecord + interface)

Mọi ranh giới giữa các cấu phần dùng chung một hợp đồng: object `StrRecord` và
một interface xử lý chung. Mỗi cấu phần nhận `StrRecord`, cập nhật các cột của
mình, trả lại `StrRecord` cho cấu phần sau.

### Interface chung của mỗi cấu phần

```yaml
# Shared interface contract (in-process)
interface: PipelineStage
method:
  name: process
  input:
    record: StrRecord          # bản ghi theo CIF, cập nhật tại chỗ
    context: StageContext      # cấu hình, credentials (từ env), logger
  output:
    record: StrRecord          # cùng record, đã cập nhật cột của cấu phần
  error_handling:
    on_error: >
      Ghi lỗi vào record.BOT_GHICHU và record.BOT_TINHTRANGTRASOAT, đặt
      record.processingStopped = true; KHÔNG ném exception ra pipeline. Các cấu
      phần sau thấy processingStopped = true thì bỏ qua xử lý record đó và chuyển
      thẳng tới U5 để tổng hợp và gửi email.
order: [U1 ConsumeData, U2 DataEntryAccuity, U3 DataEntryTraCuuThue, U4 DataEntryAMLD, U5 TongHopVaGuiMail]
```

### Shared schema — StrRecord

```yaml
# Shared schema contract — StrRecord (một bản ghi theo CIF)
StrRecord:
  type: object
  key: CIF
  control_fields:
    processingStopped: { type: boolean, description: true = cấu phần sau bỏ qua }
    writtenBy: { type: string, description: cấu phần ghi gần nhất }
  fields:
    # --- U1 ConsumeData điền ---
    CIF: string
    NGAYTIEPNHAN: string
    EMAIL_NGUOI_LAP_BAO_CAO: string
    USER_ID_NGUOI_LAP_BAO_CAO: string
    BOT_ECM: string
    TENKHACHHANG: string
    LOAIKHACHHANG: string            # KHCN | KHDN
    MASOTHUE: string
    SOLUONG_KH_THUHUONG: string
    SOLUONG_GIAODICHRA: string
    SOTIEN_GIAODICHRA: string
    SOLUONG_KH_GUITIENVAO: string
    SOLUONG_GIAODICHVAO: string
    SOTIEN_GIAODICHVAO: string
    STR_STK: string
    LOAITIEN_SOTIEN: string
    STR_MA_BAO_CAO: string
    TEN_CHI_NHANH: string
    SO_NHA_DUONG_PHO_CHI_NHANH: string
    "PHUONG/XA_CHI_NHANH": string
    "TINH/THANH_PHO_CHI_NHANH": string
    TEN_NGUOI_LAP_BAO_CAO: string
    SDT_LAM_VIEC_NGUOI_LAP_BAO_CAO: string
    SDT_DD_NGUOI_LAP_BAO_CAO: string
    PHAN_IV_LOẠI_BAO_CAO_DANG_NGO: string
    PHAN_IV_DAU_HIEU_DANG_NGO: string
    NGAY_BAT_DAU: string
    NGAY_KET_THUC: string
    PHAN_IV_3_PHAN_TICH_LY_DO_BAO_CAO: string
    PHAN_IV_CO_SO_HOP_LY_DE_NGHI_NGO: string
    PHAN_IV_NHAN_DINH_LOAI_TOI_PHAM: string
    PHAN_V_CONG_VIEC_XU_LY: string
    SDT_CHI_NHANH: string
    # --- U2 DataEntryAccuity điền ---
    BOT_ACCUITY: string
    # --- U3 DataEntryTraCuuThue điền ---
    BOT_TRACUUTHE: string
    # --- U4 DataEntryAMLD điền ---
    BOT_ALMD: string
    BOT_TINHTRANGTRASOAT: string
    # --- U4/U5 điền ---
    BOT_GHICHU: string
```

## Contract ownership rules

- **StrRecord schema** thuộc sở hữu chung (shared); định nghĩa và quy ước cột
  ai-ghi-cột-nào là một hợp đồng được tất cả cấu phần tôn trọng.
- Mỗi cấu phần CHỈ ghi các cột thuộc trách nhiệm của mình (xem phân nhóm trong
  schema); U5 đọc toàn bộ.
- **Thay đổi phá vỡ** (đổi tên/bỏ cột đang dùng): phải thống nhất ở Contract
  Design/Functional Design trước khi áp dụng.
- **Thay đổi cộng thêm** an toàn: thêm cột mới; cấu phần không biết cột mới thì
  bỏ qua, không lỗi.
- Hợp đồng Kafka (1) và ECM (2) thuộc U1; credentials đọc từ env.

## Open questions

| Contract | Question | Blocks |
|---|---|---|
| 1 (Kafka) | eventID/timeStamp có cần dùng để idempotency/dedup message trùng không? | U1 |
| 2 (ECM) | Map business_code nào cho từng loại hồ sơ PDF (HSMTK, GTTT...) | U1 |
| 3–6 (StrRecord) | Kiểu dữ liệu chính xác của các cột số (số tiền, số lượng) — chốt ở Functional Design (entities.md) | U1, U4 |
