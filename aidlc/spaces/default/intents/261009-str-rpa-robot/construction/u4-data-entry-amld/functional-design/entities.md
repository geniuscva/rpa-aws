# Entities — U4 DataEntryAMLD

Cấu phần U4 là điểm hội tụ của pipeline: nhận `StrRecord` sau khi U2 (Accuity) và
U3 (Cục Thuế) đã bồi đắp, đăng nhập AMLD Online Portal thật, nhập Mẫu số 01 (Phần
I/II/IV/V/VI, bỏ Phần III), đính kèm tài liệu Phần VI đúng thứ tự, áp retry ≤ 3, và
ghi kết quả vào các cột `BOT_ALMD`, `BOT_TINHTRANGTRASOAT`, `BOT_GHICHU` của
`StrRecord`. Đây là cấu phần phức tạp nhất (complexity XL).

## Source of truth

```yaml
entities:
  - name: AmldSession
    description: Phiên đăng nhập AMLD Online Portal thật cho một người lập báo cáo.
    attributes:
      - { name: username, type: string, required: true, constraint: "từ StrRecord.USER_ID_NGUOI_LAP_BAO_CAO" }
      - { name: password, type: string, required: true, constraint: "từ data/config.yaml, không hardcode, không log" }
      - { name: loginAttempts, type: integer, required: true, default: 0, max: 3 }
      - { name: loggedIn, type: boolean, required: true, default: false }
    constraints:
      - "Đăng nhập lại tối đa 3 lần khi màn hình treo; quá 3 lần → lỗi dừng luồng (BR4.9)"

  - name: StrReport
    description: >
      Báo cáo Mẫu số 01 đang được nhập trên AMLD Portal cho một CIF. Gom tiến độ
      nhập theo từng Phần và trạng thái đính kèm tài liệu.
    attributes:
      - { name: cif, type: string, required: true }
      - { name: customerKind, type: string, required: true, constraint: "KHCN | KHDN, từ StrRecord.LOAIKHACHHANG" }
      - { name: sectionsFilled, type: list, required: true, constraint: "các Phần đã lưu, theo thứ tự I, II, IV, V, VI (KHÔNG có III)" }
      - { name: attachmentsUploaded, type: list, required: false, constraint: "danh sách tài liệu Phần VI đã upload theo thứ tự" }
      - { name: submittedAt, type: string, required: false, constraint: "thời điểm lưu/nộp báo cáo nếu thành công" }
    relationships:
      - "mỗi StrReport thuộc một CIF (một CustomerCase)"
    constraints:
      - "Thứ tự nhập cố định I → II → IV → V → VI; Phần III không bao giờ được điền (BR4.2)"

  - name: SectionTickValue
    description: >
      Một giá trị tick/checkbox được chọn ở Phần IV hoặc Phần V, kiểm tra so với
      tập định nghĩa trước khi nhập.
    attributes:
      - { name: section, type: string, required: true, constraint: "IV | V" }
      - { name: field, type: string, required: true }
      - { name: value, type: string, required: true }
      - { name: inDefinedSet, type: boolean, required: true, constraint: "true nếu value thuộc tập định nghĩa" }
    constraints:
      - "Nếu inDefinedSet = false → dừng luồng KH, gửi email lỗi (BR4.6)"
      - "Phần V: nếu tick có ít nhất một trong 6/7/8 thì mặc định tick thêm 4 và 5 (BR4.5)"

  - name: AttachmentItem
    description: Một tài liệu đính kèm ở Phần VI với vị trí thứ tự upload cố định.
    attributes:
      - { name: category, type: string, required: true, constraint: "BangKe | MinhHoaDongTien | HoSoMoTaiKhoan | HoSoKhachHang | TaiLieuKhac" }
      - { name: filePathPattern, type: string, required: true, constraint: "pattern khớp file nguồn, ví dụ HSMTK%, GTTT%" }
      - { name: uploadOrder, type: integer, required: true, constraint: "1=Bảng kê … 5=Tài liệu khác" }
      - { name: pageCount, type: integer, required: false }
    constraints:
      - "Thứ tự upload cố định: Bảng kê → Minh Họa Dòng Tiền → Hồ sơ mở tài khoản → Hồ sơ KH → Tài liệu khác (BR4.4)"
      - "Thiếu tài liệu bắt buộc (Bảng kê, Minh Họa Dòng Tiền.pdf, Hồ sơ mở tài khoản) → không nộp, email FAIL (BR4.7)"

  - name: RetryPolicy
    description: Chính sách thử lại bọc quanh một bước nhập dễ lỗi trên AMLD Portal.
    attributes:
      - { name: operation, type: string, required: true, constraint: "tên bước nhập được bọc retry" }
      - { name: maxAttempts, type: integer, required: true, default: 3 }
      - { name: attempts, type: integer, required: true, default: 0 }
      - { name: succeeded, type: boolean, required: true, default: false }
    constraints:
      - "Thử lại tối đa 3 lần; vẫn lỗi → phát tín hiệu thất bại, dừng luồng KH (BR4.8)"

  - name: StrRecord
    description: >
      Object pipeline dùng chung (hợp đồng contract-summary.md). U4 đọc dữ liệu
      người lập (USER_ID), loại KH, và dữ liệu các Phần đã do U1 điền; ghi các cột
      BOT_ALMD, BOT_TINHTRANGTRASOAT và BOT_GHICHU (khi lỗi). Không ghi đè cột của
      U1/U2/U3.
    attributes:
      - { name: CIF, type: string, required: true }
      - { name: LOAIKHACHHANG, type: string, required: true, constraint: "KHCN | KHDN" }
      - { name: USER_ID_NGUOI_LAP_BAO_CAO, type: string, required: true }
      - { name: BOT_ALMD, type: string, required: false, constraint: "trạng thái nhập AMLD do U4 ghi" }
      - { name: BOT_TINHTRANGTRASOAT, type: string, required: false, constraint: "trạng thái tra soát do U4 ghi" }
      - { name: BOT_GHICHU, type: string, required: false, constraint: "ghi chú/mã lỗi, U4/U5 ghi" }
      - { name: processing_stopped, type: boolean, required: true }
    constraints:
      - "U4 chỉ ghi BOT_ALMD, BOT_TINHTRANGTRASOAT, BOT_GHICHU; mọi cột khác read-only với U4"
      - "Nếu nhận record với processing_stopped = true → bỏ qua nhập, chuyển nguyên record cho U5 (BR4.1)"
```

## Tóm tắt

U4 làm việc với `AmldSession` (đăng nhập, reload ≤ 3 lần), `StrReport` (tiến độ
nhập Mẫu số 01 theo Phần I/II/IV/V/VI, bỏ III), `SectionTickValue` (kiểm tra giá
trị tick Phần IV/V), `AttachmentItem` (đính kèm Phần VI đúng thứ tự), và
`RetryPolicy` (retry ≤ 3). U4 chỉ ghi các cột `BOT_ALMD`, `BOT_TINHTRANGTRASOAT`,
`BOT_GHICHU` của `StrRecord`. Là điểm hội tụ của hai nhánh tra cứu U2 và U3.
