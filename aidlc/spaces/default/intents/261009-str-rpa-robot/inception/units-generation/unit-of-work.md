# Units of Work — Robot RPA nhập liệu STR

Pipeline tuần tự 5 cấu phần. Robot là một ứng dụng chạy nền duy nhất; các Unit là
module trong cùng một process, chạy nối tiếp theo đúng thứ tự pipeline. Không có
walking skeleton riêng — mỗi cấu phần là một chặng xử lý thực của pipeline.

Dữ liệu truyền giữa các cấu phần là một object tổng hợp theo CIF — `StrRecord`
(định nghĩa ở cuối file). `StrRecord` là **data object được truyền qua lại và cập
nhật tuần tự** suốt pipeline từ U1 đến U5: mỗi cấu phần nhận object từ cấu phần
trước, xử lý, ghi (update) kết quả của mình vào object, rồi chuyển tiếp cho cấu
phần sau. Đây là trạng thái dùng chung duy nhất chảy xuyên suốt U1 → U2 → U3 →
U4 → U5.

Đây là mô tả topology (ai phụ thuộc ai), không phải thứ tự thi công kinh tế — Bolt
sequence do Delivery Planning quyết định.

## Bảng Unit

| Unit ID | Directory | Tên | Kind | Complexity |
|---|---|---|---|---|
| U1 | u1-consume-data | ConsumeData | service | L |
| U2 | u2-data-entry-accuity | DataEntryAccuity | service | M |
| U3 | u3-data-entry-tracuuthue | DataEntryTraCuuThue | service | M |
| U4 | u4-data-entry-amld | DataEntryAMLD | service | XL |
| U5 | u5-tonghop-guimail | TongHopVaGuiMail | service | M |

## U1 — ConsumeData (xử lý input)

- **Mô tả:** Nhận việc từ queue Kafka, đọc 5 file excel nguồn của từng CIF, phân
  loại KHCN/KHDN, call service ECM (mock) lấy hồ sơ PDF, tạo file minh họa dòng
  tiền, và tổng hợp dữ liệu đầu vào thành `StrRecord` cho các cấu phần sau.
- **Component (Domain Design):** KafkaConsumer, Orchestrator (khung điều phối +
  mô hình dữ liệu), SourceDataReader, EcmClient, CashFlowDiagramBuilder.
- **Trách nhiệm:** get queue Kafka; đọc & kiểm tra excel; phân loại KH; call ECM;
  tạo `Minh Họa Dòng Tiền.pdf`; khởi tạo & điền phần đầu của `StrRecord`
  (CIF, loại KH, mã số thuế, số liệu dòng tiền, thông tin người lập, các cột
  Phần IV/V lấy từ file nguồn).
- **Deployment:** module (shared). **Phụ thuộc:** không.
- **Output:** `StrRecord` (đã điền phần input) + các file PDF (dòng tiền, hồ sơ
  ECM).

## U2 — DataEntryAccuity

- **Mô tả:** Truy cập hệ thống Accuity mock web, tra cứu theo tên KH, xuất file
  `Tra cứu Accuity.pdf`; cập nhật kết quả vào `StrRecord` (BOT_ACCUITY).
- **Component:** AccuityLookup.
- **Deployment:** module (shared). **Phụ thuộc:** U1 (cần `StrRecord` + tên KH).
- **Output:** `StrRecord` (bổ sung BOT_ACCUITY) + `Tra cứu Accuity.pdf`.

## U3 — DataEntryTraCuuThue

- **Mô tả:** Truy cập web Cục Thuế thật, nhập mã số thuế, giải captcha bằng
  ddddocr, lấy thông tin tình trạng người nộp thuế (chỉ áp dụng KHDN), xuất
  `Tra cứu tình trạng người nộp thuế.pdf`; cập nhật `StrRecord` (BOT_TRACUUTHE).
- **Component:** TaxAuthorityLookup, CaptchaSolver.
- **Deployment:** module (shared). **Phụ thuộc:** U1 (độc lập với U2, chạy song song được).
- **Output:** `StrRecord` (bổ sung BOT_TRACUUTHE) + PDF (nếu có).

## U4 — DataEntryAMLD

- **Mô tả:** Nhập thông tin báo cáo trên web NHNN thật (AMLD Online Portal):
  đăng nhập, nhập Phần I/II/IV/V/VI (bỏ III), rẽ nhánh KHCN/KHDN, chặn giá trị
  tick ngoài định nghĩa, đính kèm tài liệu Phần VI đúng thứ tự; áp retry ≤ 3; cập
  nhật `StrRecord` (BOT_ALMD, BOT_TINHTRANGTRASOAT, BOT_GHICHU).
- **Component:** AmldPortalFiller, RetryManager.
- **Deployment:** module (shared). **Phụ thuộc:** U2 và U3 (điểm hội tụ).
- **Output:** `StrRecord` (bổ sung trạng thái nhập AMLD).

## U5 — TongHopVaGuiMail

- **Mô tả:** Tổng hợp `StrRecord` của tất cả KH trong lô thành bảng trạng thái,
  dựng file excel đính kèm, và gửi email qua mail exchange (To người lập, Cc
  nguyendinhhai1996@hotmail.com), gồm cả email báo thất bại sau 3 lần retry.
- **Component:** ErrorAggregator, EmailNotifier.
- **Deployment:** module (shared). **Phụ thuộc:** U4.
- **Output:** file excel trạng thái + email đã gửi.

---

## Object dữ liệu truyền giữa các cấu phần — `StrRecord`

Một bản ghi theo CIF, được U1 khởi tạo và các cấu phần sau bồi đắp dần. Các cột:

| Cột | Nguồn/ghi bởi | Ý nghĩa |
|---|---|---|
| CIF | U1 | Mã CIF khách hàng (khóa) |
| NGAYTIEPNHAN | U1 | Ngày tiếp nhận |
| EMAIL_NGUOI_LAP_BAO_CAO | U1 | Email người lập (To email ở U5) |
| USER_ID_NGUOI_LAP_BAO_CAO | U1 | Username đăng nhập AMLD (dùng ở U4) |
| BOT_ECM | U1 | Trạng thái lấy hồ sơ ECM |
| BOT_ALMD | U4 | Trạng thái nhập AMLD |
| TENKHACHHANG | U1 | Tên khách hàng |
| LOAIKHACHHANG | U1 | KHCN / KHDN |
| MASOTHUE | U1 | Mã số thuế (KHDN) |
| SOLUONG_KH_THUHUONG | U1 | Số lượng KH thụ hưởng |
| SOLUONG_GIAODICHRA | U1 | Số GD ra (dòng tiền) |
| SOTIEN_GIAODICHRA | U1 | Số tiền GD ra |
| SOLUONG_KH_GUITIENVAO | U1 | Số KH gửi tiền vào |
| SOLUONG_GIAODICHVAO | U1 | Số GD vào |
| SOTIEN_GIAODICHVAO | U1 | Số tiền GD vào |
| STR_STK | U1 | Số tài khoản STR |
| LOAITIEN_SOTIEN | U1 | Loại tiền & số tiền |
| STR_MA_BAO_CAO | U1 | Mã báo cáo nội bộ |
| TEN_CHI_NHANH | U1 | Tên chi nhánh |
| SO_NHA_DUONG_PHO_CHI_NHANH | U1 | Địa chỉ chi nhánh |
| PHUONG/XA_CHI_NHANH | U1 | Phường/xã chi nhánh |
| TINH/THANH_PHO_CHI_NHANH | U1 | Tỉnh/TP chi nhánh |
| TEN_NGUOI_LAP_BAO_CAO | U1 | Tên người lập |
| SDT_LAM_VIEC_NGUOI_LAP_BAO_CAO | U1 | SĐT làm việc người lập |
| SDT_DD_NGUOI_LAP_BAO_CAO | U1 | SĐT di động người lập |
| PHAN_IV_LOẠI_BAO_CAO_DANG_NGO | U1 | Phần IV - loại báo cáo đáng ngờ |
| PHAN_IV_DAU_HIEU_DANG_NGO | U1 | Phần IV - dấu hiệu đáng ngờ |
| NGAY_BAT_DAU | U1 | Thời gian GD bắt đầu |
| NGAY_KET_THUC | U1 | Thời gian GD kết thúc |
| PHAN_IV_3_PHAN_TICH_LY_DO_BAO_CAO | U1 | Phần IV.3 - lý do báo cáo |
| PHAN_IV_CO_SO_HOP_LY_DE_NGHI_NGO | U1 | Phần IV - cơ sở nghi ngờ |
| PHAN_IV_NHAN_DINH_LOAI_TOI_PHAM | U1 | Phần IV - loại tội phạm |
| PHAN_V_CONG_VIEC_XU_LY | U1 | Phần V - công việc xử lý |
| BOT_TINHTRANGTRASOAT | U4 | Trạng thái tra soát của bot |
| BOT_TRACUUTHE | U3 | Kết quả tra cứu thuế |
| BOT_ACCUITY | U2 | Kết quả tra cứu Accuity |
| BOT_GHICHU | U4/U5 | Ghi chú/mã lỗi của bot |
| SDT_CHI_NHANH | U1 | SĐT chi nhánh |

Quy ước: cấu phần sau chỉ đọc/ghi các cột thuộc trách nhiệm của mình; U5 đọc toàn
bộ `StrRecord` của mọi CIF để tổng hợp và dựng file trạng thái.
