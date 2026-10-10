# Entities — U1 ConsumeData

Mô hình thực thể của cấu phần U1 (ConsumeData). U1 sở hữu/khởi tạo các thực thể
đầu vào và dựng phần input của `StrRecord`. Mô tả ở mức logic, không gắn công nghệ.

## Source of truth

```yaml
entities:
  - name: KafkaStrEvent
    description: Message việc nhận từ Kafka, mỗi message là một CIF cần xử lý.
    attributes:
      - { name: eventID, type: string, required: true, unique: true }
      - { name: eventName, type: string, required: true, allowed_values: ["LIST_CUST_STR"] }
      - { name: cif, type: string, required: true }
      - { name: timeStamp, type: string, required: true, constraint: "epoch millis dạng chuỗi" }
    constraints:
      - "eventID là khóa chống trùng (dedup): message có eventID đã xử lý thì bỏ qua"

  - name: ProcessedEvent
    description: Bản ghi eventID đã xử lý, phục vụ chống trùng (idempotency).
    attributes:
      - { name: eventID, type: string, required: true, unique: true }
      - { name: processedAt, type: datetime, required: true }
    constraints:
      - "Tồn tại eventID trong tập này nghĩa là message đã xử lý"

  - name: CustomerSourceFolder
    description: Thư mục nguồn của một CIF trong thư mục theo ngày.
    attributes:
      - { name: cif, type: string, required: true, unique: true }
      - { name: folderPath, type: string, required: true, constraint: "theo /Users/hainguyen/Projects/RPA/AMLD/YYYYMM/YYYYMMDD/<cif>" }
      - { name: customerType, type: string, required: true, allowed_values: ["KHCN", "KHDN"] }
      - { name: requiredFilesPresent, type: boolean, required: true }
      - { name: missingFiles, type: "list<string>", required: false }
    relationships:
      - "mỗi CustomerSourceFolder tương ứng một CIF (một KafkaStrEvent)"

  - name: SourceExcelSet
    description: Tập 5 file excel nguồn đã đọc của một CIF.
    attributes:
      - { name: cif, type: string, required: true }
      - { name: inputStr, type: object, required: true, constraint: "từ thong_tin_dau_vao_bao_cao_str.xlsx" }
      - { name: individualTxn, type: object, required: false, constraint: "ca_nhan_thuc_hien_giao_dich.xlsx (KHCN)" }
      - { name: orgTxn, type: object, required: false, constraint: "to_chuc_thuc_hien_giao_dich.xlsx (KHDN)" }
      - { name: suspiciousTxn, type: object, required: true, constraint: "thong_tin_giao_dich_dang_ngo.xlsx" }
      - { name: accountStatement, type: object, required: true, constraint: "bang_ke_giao_dich_tai_khoan_dang_ngo.xlsx" }
    constraints:
      - "KHCN cần individualTxn; KHDN cần orgTxn (đúng một trong hai theo loại KH)"

  - name: CustomerDossier
    description: Hồ sơ PDF của KH lấy qua ECM mock.
    attributes:
      - { name: cif, type: string, required: true }
      - { name: pdfFiles, type: "list<string>", required: false, constraint: "đường dẫn file PDF đã tải" }
      - { name: docIds, type: "list<string>", required: false }
      - { name: businessCodesTried, type: "list<string>", required: false }
      - { name: retrievedAt, type: datetime, required: false }
    relationships:
      - "mỗi CustomerDossier thuộc một CIF"

  - name: CashFlowDiagram
    description: Sơ đồ minh họa dòng tiền, xuất ra PDF.
    attributes:
      - { name: cif, type: string, required: true }
      - { name: inflow_customerCount, type: integer, required: true, constraint: "count distinct(TK_DOIUNG+TENKH_DOIUNG) với HUONG_GD=C" }
      - { name: inflow_txnCount, type: integer, required: true, constraint: "count(MA_GD) với HUONG_GD=C" }
      - { name: inflow_amount, type: decimal, required: true, constraint: "sum(SOTIEN_GD_QD) với HUONG_GD=C" }
      - { name: outflow_customerCount, type: integer, required: true, constraint: "tương tự với HUONG_GD=D" }
      - { name: outflow_txnCount, type: integer, required: true }
      - { name: outflow_amount, type: decimal, required: true }
      - { name: reportSubjectName, type: string, required: true, constraint: "STR_TEN_KH từ thong_tin_dau_vao_bao_cao_str.xlsx" }
      - { name: pdfPath, type: string, required: true, constraint: "Minh Họa Dòng Tiền.pdf" }
    relationships:
      - "mỗi CashFlowDiagram thuộc một CIF"

  - name: StrRecord
    description: >
      Object dữ liệu dùng chung của pipeline (hợp đồng ở contract-summary.md). U1
      khởi tạo và điền phần input; các cấu phần sau bồi đắp. Chỉ liệt kê các trường
      U1 ghi; schema đầy đủ ở contract-summary.md.
    attributes:
      - { name: CIF, type: string, required: true, unique: true }
      - { name: processingStopped, type: boolean, required: true, default: false }
      - { name: LOAIKHACHHANG, type: string, required: true, allowed_values: ["KHCN", "KHDN"] }
      - { name: MASOTHUE, type: string, required: false }
      - { name: TENKHACHHANG, type: string, required: false }
      - { name: SOLUONG_KH_GUITIENVAO, type: integer, required: false }
      - { name: SOLUONG_GIAODICHVAO, type: integer, required: false }
      - { name: SOTIEN_GIAODICHVAO, type: decimal, required: false }
      - { name: SOLUONG_KH_THUHUONG, type: integer, required: false }
      - { name: SOLUONG_GIAODICHRA, type: integer, required: false }
      - { name: SOTIEN_GIAODICHRA, type: decimal, required: false }
      - { name: BOT_ECM, type: string, required: false, constraint: "trạng thái lấy hồ sơ ECM" }
      - { name: BOT_GHICHU, type: string, required: false }
    constraints:
      - "Khi thiếu file bắt buộc hoặc lỗi ECM: ghi BOT_ECM/BOT_GHICHU và đặt processingStopped=true"
    relationships:
      - "mỗi StrRecord ứng với một CIF; U1 nạp dữ liệu từ SourceExcelSet, CustomerDossier, CashFlowDiagram"
```

## Tóm tắt

U1 làm việc với: `KafkaStrEvent` (đầu vào), `ProcessedEvent` (chống trùng theo
eventID), `CustomerSourceFolder` (thư mục CIF theo ngày), `SourceExcelSet` (5
file excel), `CustomerDossier` (hồ sơ PDF từ ECM), `CashFlowDiagram` (sơ đồ dòng
tiền), và khởi tạo `StrRecord` phần input. Kiểu dữ liệu số (số tiền, số lượng) ở
mức logic; kiểu kỹ thuật cụ thể chốt ở Code Generation.
