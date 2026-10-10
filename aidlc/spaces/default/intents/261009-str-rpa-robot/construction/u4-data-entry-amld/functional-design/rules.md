# Business Rules — U4 DataEntryAMLD

Quy tắc nghiệp vụ của cấu phần U4. Mỗi quy tắc có id `BRx.y` (nhóm 4).

## Source of truth

```yaml
rules:
  - id: BR4.1
    statement: Bỏ qua record đã dừng xử lý.
    category: policy
    applies_to: StrRecord
    trigger: Khi U4 nhận StrRecord sau khi hội tụ U2 và U3
    logic: >
      IF record.processingStopped = true THEN U4 không nhập AMLD, chuyển nguyên
      record thẳng tới U5.
    violation: N/A (hành vi cô lập lỗi chuẩn của pipeline).
    source: FR12

  - id: BR4.2
    statement: Nhập Mẫu số 01 theo thứ tự Phần I → II → IV → V → VI, KHÔNG điền Phần III.
    category: policy
    applies_to: StrReport
    trigger: Sau khi đăng nhập AMLD Portal và vào tab "Nhập STR" → "Mẫu số 01"
    logic: >
      Nhập và lưu lần lượt Phần I (ĐTBC), Phần II (CN/TC thực hiện GD), Phần IV
      (GD đáng ngờ), Phần V (công việc xử lý), Phần VI (tài liệu đính kèm). Phần
      III không bao giờ được điền.
    violation: Điền Phần III là vi phạm nghiêm trọng — bị cấm tuyệt đối.
    source: FR9.1

  - id: BR4.3
    statement: Phần II rẽ nhánh theo loại khách hàng.
    category: policy
    applies_to: StrReport
    trigger: Khi nhập Phần II (CN/TC thực hiện GD)
    logic: >
      IF LOAIKHACHHANG = KHCN THEN upload ca_nhan_thuc_hien_giao_dich.xlsx và tick
      "Trùng với cá nhân thực hiện" ở mục chủ sở hữu hưởng lợi; ELSE IF KHDN THEN
      upload to_chuc_thuc_hien_giao_dich.xlsx và chọn người đại diện có GTTT ngày
      cấp mới nhất.
    violation: Nhập sai nhánh KHCN/KHDN → dữ liệu sai, phải dừng và báo lỗi.
    source: FR9.3

  - id: BR4.4
    statement: Upload tài liệu Phần VI đúng thứ tự cố định.
    category: constraint
    applies_to: AttachmentItem
    trigger: Khi nhập Phần VI (tài liệu đính kèm)
    logic: >
      Upload theo thứ tự: Bảng kê → Minh Họa Dòng Tiền.pdf → Hồ sơ mở tài khoản
      (HSMTK%) → Hồ sơ khách hàng (Giay phep thanh lap% / GTTT% / …) → Tài liệu
      khác (Tra cứu Accuity% / Tra cứu tình trạng người nộp thuế.pdf). Đếm đúng
      số trang mỗi file; nhiều file cùng loại thì upload lần lượt.
    violation: Sai thứ tự upload → báo cáo không hợp lệ.
    source: FR9.6

  - id: BR4.5
    statement: Quy tắc tick Phần V — 6/7/8 kéo theo 4 và 5.
    category: calculation
    applies_to: SectionTickValue
    trigger: Khi tick các công việc đã thực hiện ở Phần V
    logic: >
      IF tập giá trị tick của Phần V chứa ít nhất một trong {6, 7, 8} THEN mặc
      định tick thêm 4 và 5 trước khi lưu Phần V.
    violation: N/A (quy tắc dẫn xuất bắt buộc).
    source: FR9.5

  - id: BR4.6
    statement: Chặn giá trị tick ngoài tập định nghĩa ở Phần IV/V.
    category: validation
    applies_to: SectionTickValue
    trigger: Trước khi nhập một giá trị tick ở Phần IV hoặc Phần V
    logic: >
      IF value KHÔNG thuộc tập định nghĩa THEN dừng luồng KH đó, ghi BOT_GHICHU
      mô tả giá trị ngoài tập, đặt processingStopped=true và gửi email lỗi (ở U5).
    violation: N/A (đây là hành vi an toàn bắt buộc, tránh nộp dữ liệu sai).
    source: FR10.1

  - id: BR4.7
    statement: Không nộp báo cáo khi thiếu tài liệu bắt buộc.
    category: validation
    applies_to: AttachmentItem
    trigger: Trước khi hoàn tất/nộp Phần VI
    logic: >
      IF thiếu một trong các tài liệu bắt buộc (Bảng kê, Minh Họa Dòng Tiền.pdf,
      Hồ sơ mở tài khoản) THEN KHÔNG nộp báo cáo, ghi BOT_GHICHU, đặt
      processingStopped=true và gửi email FAIL (ở U5).
    violation: N/A (ràng buộc bắt buộc theo rule dự án đã affirmed).
    source: FR9.6, FR13

  - id: BR4.8
    statement: Retry mỗi bước nhập lỗi tối đa 3 lần.
    category: policy
    applies_to: RetryPolicy
    trigger: Khi một bước nhập/tương tác trên AMLD Portal báo lỗi
    logic: >
      Bọc bước nhập dễ lỗi trong RetryPolicy; thử lại tối đa 3 lần. IF vẫn lỗi sau
      3 lần THEN phát tín hiệu thất bại, ghi BOT_ALMD lỗi + BOT_GHICHU, đặt
      processingStopped=true; U5 gửi email báo thất bại (không có robot thứ hai).
    violation: N/A (chính sách độ bền chuẩn).
    source: FR11.1, FR11.2, NFR3

  - id: BR4.9
    statement: Đăng nhập AMLD treo thì reload và thử lại tối đa 3 lần.
    category: policy
    applies_to: AmldSession
    trigger: Khi màn hình đăng nhập AMLD Portal treo
    logic: >
      IF màn hình đăng nhập treo THEN reload và đăng nhập lại; tối đa 3 lần. IF
      quá 3 lần THEN ghi BOT_ALMD lỗi + BOT_GHICHU, đặt processingStopped=true,
      gửi email lỗi (ở U5).
    violation: N/A (xử lý lỗi đăng nhập chuẩn).
    source: FR8.2

  - id: BR4.10
    statement: Ghi kết quả nhập AMLD vào StrRecord.
    category: constraint
    applies_to: StrRecord
    trigger: Khi hoàn tất (hoặc dừng) việc nhập Mẫu số 01 cho một CIF
    logic: >
      Ghi BOT_ALMD (OK/lỗi) và BOT_TINHTRANGTRASOAT; ghi BOT_GHICHU khi có lỗi.
      Chuyển record cho U5.
    violation: N/A.
    source: FR9, FR12.1

  - id: BR4.11
    statement: Không hardcode credentials/endpoint AMLD Portal.
    category: constraint
    applies_to: AmldSession
    trigger: Khi đăng nhập và thao tác trên AMLD Portal
    logic: >
      Username lấy từ StrRecord.USER_ID_NGUOI_LAP_BAO_CAO; password và endpoint
      đọc từ data/config.yaml. Không hardcode trong mã, không log giá trị secret.
    violation: Vi phạm bảo mật (NFR4/US5.1) — không được phép.
    source: NFR4
```

## Tóm tắt quy tắc

| ID | Loại | Nội dung |
|---|---|---|
| BR4.1 | policy | Bỏ qua record đã dừng |
| BR4.2 | policy | Nhập I→II→IV→V→VI, bỏ Phần III |
| BR4.3 | policy | Phần II rẽ nhánh KHCN/KHDN |
| BR4.4 | constraint | Upload Phần VI đúng thứ tự |
| BR4.5 | calculation | Phần V: 6/7/8 kéo theo 4 và 5 |
| BR4.6 | validation | Chặn giá trị tick ngoài tập định nghĩa |
| BR4.7 | validation | Thiếu tài liệu bắt buộc → không nộp, email FAIL |
| BR4.8 | policy | Retry mỗi bước lỗi ≤ 3 lần |
| BR4.9 | policy | Đăng nhập treo → reload ≤ 3 lần |
| BR4.10 | constraint | Ghi BOT_ALMD/BOT_TINHTRANGTRASOAT |
| BR4.11 | constraint | Không hardcode credentials AMLD |
