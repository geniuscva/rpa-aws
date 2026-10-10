# Unit Dependency DAG

5 cấu phần với một nhánh song song: U1 trước, rồi U2 (Accuity) và U3 (Cục Thuế)
độc lập chạy song song, U4 hội tụ cả hai, U5 cuối. Dữ liệu truyền là object
`StrRecord` theo CIF. Đây là topology, không phải thứ tự thi công kinh tế.

## DAG (prose)

- **U1 (ConsumeData)** — không phụ thuộc Unit nào. Nhận Kafka, đọc excel, phân
  loại KH, call ECM, tạo file dòng tiền; khởi tạo `StrRecord`.
- **U2 (DataEntryAccuity)** depends on **U1** — cần `StrRecord` (tên KH, loại KH).
- **U3 (DataEntryTraCuuThue)** depends on **U1** — chỉ cần mã số thuế + loại KH từ
  U1; độc lập với U2 (chỉ xử lý thực khi KHDN). Có thể chạy song song với U2.
- **U4 (DataEntryAMLD)** depends on **U2 và U3** — điểm hội tụ: cần cả kết quả tra
  cứu Accuity (U2) và kết quả tra cứu thuế (U3), cùng các file đính kèm, để nhập
  AMLD.
- **U5 (TongHopVaGuiMail)** depends on **U4** — tổng hợp `StrRecord` của cả lô và
  gửi email.

### Điểm tích hợp giữa các Unit

- Hợp đồng dữ liệu chung giữa mọi cấu phần là object `StrRecord` (xem
  unit-of-work.md). Mỗi cấu phần bồi đắp các cột thuộc trách nhiệm của mình.
- U1 → U2: `StrRecord` (phần input) + file dòng tiền + hồ sơ ECM.
- U1 → U3: `StrRecord` (mã số thuế + loại KH).
- U2 → U4: `StrRecord` (+ BOT_ACCUITY) + `Tra cứu Accuity.pdf`.
- U3 → U4: `StrRecord` (+ BOT_TRACUUTHE) + PDF tra cứu thuế (nếu có).
- U4 → U5: `StrRecord` (+ BOT_ALMD, BOT_TINHTRANGTRASOAT, BOT_GHICHU).

### Phát triển song song

Sau khi U1 xong, **U2 (Accuity) và U3 (Cục Thuế) độc lập với nhau** — cả hai chỉ
cần output của U1 (tên KH, loại KH, mã số thuế), không cần output của nhau. Chúng
là hai nhánh tra cứu riêng và tạo thành một **batch chạy song song** sau U1. U4
hội tụ cả hai. Hợp đồng `StrRecord` (mỗi cấu phần ghi cột riêng: U2 ghi
BOT_ACCUITY, U3 ghi BOT_TRACUUTHE) đảm bảo hai nhánh không ghi đè nhau khi hợp
nhất.

### Walking skeleton

Không áp dụng cho phân rã này: không có Unit skeleton riêng. Mỗi cấu phần là một
chặng xử lý thực của pipeline; lát cắt chạy được sớm nhất là U1 (ConsumeData) tạo
`StrRecord` và file dòng tiền.

## Pipeline flow (mermaid)

```mermaid
flowchart TD
    K[(Kafka topic<br/>RPA_STR_NHNN_INPUT)] --> U1

    subgraph U1[U1 - ConsumeData]
        A1[Get queue Kafka] --> A2[Đọc 5 file excel từ thư mục ngày/CIF]
        A2 --> A3[Phân loại KHCN/KHDN]
        A3 --> A4[Call ECM mock - lấy hồ sơ PDF]
        A4 --> A5[Tạo Minh Hoa Dong Tien.pdf]
        A5 --> A6[Khởi tạo StrRecord - phần input]
    end

    U1 -->|StrRecord + PDF dòng tiền + hồ sơ ECM| U2

    subgraph U2[U2 - DataEntryAccuity]
        B1[Đăng nhập Accuity mock] --> B2[Tra cứu theo tên KH]
        B2 --> B3[Xuất Tra cuu Accuity.pdf]
        B3 --> B4[Cập nhật BOT_ACCUITY]
    end

    U1 -->|StrRecord + mã số thuế/loại KH| U3

    subgraph U3[U3 - DataEntryTraCuuThue]
        C0{KHDN?}
        C0 -->|Có| C1[Mở web Cục Thuế thật]
        C1 --> C2[Nhập MST + giải captcha ddddocr]
        C2 --> C3[Xuất Tra cuu nguoi nop thue.pdf]
        C3 --> C4[Cập nhật BOT_TRACUUTHE]
        C0 -->|KHCN| C5[Bỏ qua tra cứu thuế]
    end

    U2 -->|StrRecord + Accuity.pdf| U4
    U3 -->|StrRecord + PDF thuế| U4

    subgraph U4[U4 - DataEntryAMLD]
        D1[Đăng nhập AMLD Portal thật] --> D2[Nhập Phần I - II - IV - V - VI<br/>bỏ Phần III]
        D2 --> D3[Chặn giá trị tick ngoài định nghĩa]
        D3 --> D4[Đính kèm tài liệu Phần VI]
        D4 --> D5[Retry &lt;= 3 lần]
        D5 --> D6[Cập nhật BOT_ALMD, BOT_TINHTRANGTRASOAT]
    end

    U4 -->|StrRecord - đã nhập/trạng thái| U5

    subgraph U5[U5 - TongHopVaGuiMail]
        E1[Tổng hợp StrRecord mọi CIF trong lô] --> E2[Dựng file excel trạng thái]
        E2 --> E3[Gửi email qua mail exchange<br/>To người lập, Cc nguyendinhhai1996]
    end

    U5 --> END[Kết thúc lô]

    D5 -. lỗi sau 3 lần retry .-> E3
```

## Edge block (machine-readable)

```yaml
units:
  - name: u1-consume-data
    kind: service
    depends_on: []
  - name: u2-data-entry-accuity
    kind: service
    depends_on: [u1-consume-data]
  - name: u3-data-entry-tracuuthue
    kind: service
    depends_on: [u1-consume-data]
  - name: u4-data-entry-amld
    kind: service
    depends_on: [u2-data-entry-accuity, u3-data-entry-tracuuthue]
  - name: u5-tonghop-guimail
    kind: service
    depends_on: [u4-data-entry-amld]
```
