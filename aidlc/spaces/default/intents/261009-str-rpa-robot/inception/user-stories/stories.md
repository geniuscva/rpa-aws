# User Stories — Robot RPA nhập liệu STR

Story viết theo luồng nghiệp vụ end-to-end của robot. Mỗi story có ID US{nhóm}.{thứ tự},
tiêu chí nghiệm thu Given/When/Then với ID AC ba đoạn, ưu tiên MoSCoW, ghi chú INVEST,
và truy vết tới yêu cầu (FR/NFR).

---

## Nhóm US1 — Nhận việc & chuẩn bị dữ liệu

### US1.1 — Nhận việc qua Kafka
**As a** RPA Ops, **I want** robot chạy thường trực và nhận message việc từ Kafka,
**so that** mỗi lô/khách hàng được xử lý ngay khi có tín hiệu, không chờ lịch.
Ưu tiên: **Must Have**. Truy vết: FR1.
- **AC1.1.1** — Given robot đang chạy và kết nối Kafka `localhost:9092` (PLAINTEXT)
  topic `RPA_STR_NHNN_INPUT`, When có message hợp lệ, Then robot bắt đầu xử lý
  lô/khách hàng tương ứng.
- **AC1.1.2** — Given một message không hợp lệ, When robot nhận, Then ghi log lỗi
  và tiếp tục nhận message kế tiếp mà không dừng consumer.
- INVEST: độc lập, kiểm thử được bằng mock Kafka.

### US1.2 — Nhận diện thư mục nguồn theo ngày
**As a** RPA Ops, **I want** robot tự xác định thư mục nguồn theo ngày,
**so that** đúng dữ liệu của lô được đọc.
Ưu tiên: **Must Have**. Truy vết: FR2.
- **AC1.2.1** — Given ngày hiện tại, When robot xử lý lô, Then nó đọc thư mục
  `/Users/hainguyen/Projects/RPA/AMLD/YYYYMM/YYYYMMDD`, mỗi thư mục con là một CIF.
- **AC1.2.2** — Given robot chạy local, When truy cập thư mục, Then có quyền
  đọc/ghi mặc định (không cần cấp quyền thủ công).

### US1.3 — Kiểm tra đủ file excel bắt buộc trong folder CIF
**As a** Người lập báo cáo, **I want** robot kiểm tra đủ file excel bắt buộc,
**so that** chỉ xử lý khi dữ liệu đầy đủ.
Ưu tiên: **Must Have**. Truy vết: FR3.1, FR3.3.
- **AC1.3.1** — Given folder CIF, When kiểm tra, Then xác nhận có đủ: (cá nhân
  hoặc tổ chức), bảng kê, thông tin GD đáng ngờ, thông tin đầu vào STR.
- **AC1.3.2** — Given thiếu file bắt buộc, When kiểm tra, Then ghi nhận tên file
  thiếu, dừng luồng KH đó và chuyển sang tổng hợp lỗi (US6.1).

### US1.4 — Lấy hồ sơ khách hàng qua ECM mock
**As a** Người lập báo cáo, **I want** robot lấy file PDF hồ sơ KH từ ECM mock,
**so that** có đủ tài liệu đính kèm cho báo cáo.
Ưu tiên: **Must Have**. Truy vết: FR3.2, FR14.
- **AC1.4.1** — Given ECM mock `http://localhost:8831`, When robot cần hồ sơ, Then
  nó lấy token (client_credentials) → search file theo customerCode → tải PDF theo
  doc_id.
- **AC1.4.2** — Given gọi ECM lỗi hoặc thiếu hồ sơ bắt buộc, When xử lý, Then
  chuyển tổng hợp lỗi (US6.1) và gửi email FAIL (US6.2).
- **AC1.4.3** — Given credentials ECM, When gọi, Then đọc từ cấu hình/biến môi
  trường, không hardcode.

### US1.5 — Phân loại khách hàng KHCN/KHDN
**As a** Người lập báo cáo, **I want** robot tự phân loại KHCN/KHDN,
**so that** các bước phụ thuộc loại KH rẽ nhánh đúng.
Ưu tiên: **Must Have**. Truy vết: FR4.
- **AC1.5.1** — Given dữ liệu file nguồn, When phân loại, Then xác định đúng KHCN
  hay KHDN.
- **AC1.5.2** — Given loại KH, When xử lý Phần II và tra cứu Cục Thuế, Then rẽ
  nhánh theo loại (KHDN mới tra Cục Thuế).

---

## Nhóm US2 — Tổng hợp & tra cứu đối chiếu

### US2.1 — Tổng hợp sơ đồ dòng tiền
**As a** Người lập báo cáo, **I want** robot vẽ sơ đồ dòng tiền từ bảng kê,
**so that** có tài liệu minh họa đính kèm đúng số liệu.
Ưu tiên: **Must Have**. Truy vết: FR5.
- **AC2.1.1** — Given bảng kê GD, When tổng hợp, Then tính shape tiền vào
  (HUONG_GD=C): số KH gửi vào, số GD, tổng tiền; và shape tiền ra (HUONG_GD=D)
  tương tự; shape giữa là tên ĐTBC từ STR_TEN_KH.
- **AC2.1.2** — Given tính xong, When xuất, Then lưu `Minh Họa Dòng Tiền.pdf`.

### US2.2 — Tra cứu Accuity (mock)
**As a** Người lập báo cáo, **I want** robot tra cứu KH trên web Accuity mock,
**so that** có kết quả đối chiếu danh sách cảnh báo.
Ưu tiên: **Must Have**. Truy vết: FR6.
- **AC2.2.1** — Given web Accuity mock có login, When robot đăng nhập và tra cứu
  theo Entity Type + tên STR_TEN_KH, Then export `Tra cứu Accuity.pdf`.
- **AC2.2.2** — Given Match Score = 100, When có bản ghi, Then print hồ sơ
  `Tra cứu Accuity(n).pdf`.

### US2.3 — Tra cứu tình trạng người nộp thuế (Cục Thuế, chỉ KHDN)
**As a** Người lập báo cáo, **I want** robot tra cứu Cục Thuế cho KHDN với captcha
tự động, **so that** bổ sung thông tin người nộp thuế vào hồ sơ.
Ưu tiên: **Should Have**. Truy vết: FR7.
- **AC2.3.1** — Given KH là KHDN, When tra cứu Cục Thuế thật, Then nhập mã số thuế
  và giải captcha bằng ddddocr.
- **AC2.3.2** — Given có kết quả, When tra cứu xong, Then print
  `Tra cứu tình trạng người nộp thuế.pdf`; nếu không có kết quả thì bỏ qua.

---

## Nhóm US3 — Nhập liệu AMLD Portal

### US3.1 — Đăng nhập AMLD Portal
**As a** Người lập báo cáo, **I want** robot đăng nhập AMLD Portal thật,
**so that** truy cập được form nhập STR.
Ưu tiên: **Must Have**. Truy vết: FR8.
- **AC3.1.1** — Given credentials người lập báo cáo, When đăng nhập, Then vào được
  portal.
- **AC3.1.2** — Given màn hình treo, When đăng nhập, Then reload & thử lại tối đa
  3 lần; quá 3 lần thì gửi email lỗi.

### US3.2 — Nhập Mẫu số 01 đầy đủ các Phần
**As a** Người lập báo cáo, **I want** robot nhập Phần I, II, IV, V, VI đúng thứ tự,
**so that** báo cáo đầy đủ và hợp lệ.
Ưu tiên: **Must Have**. Truy vết: FR9.
- **AC3.2.1** — Given đã đăng nhập, When nhập liệu, Then theo thứ tự I → II → IV →
  V → VI và KHÔNG điền Phần III.
- **AC3.2.2** — Given Phần II, When loại KH là KHCN/KHDN, Then upload file tương
  ứng và chọn người đại diện/chủ sở hữu đúng quy tắc.
- **AC3.2.3** — Given Phần V có giá trị 6/7/8, When tick, Then mặc định tick thêm
  4 và 5.
- **AC3.2.4** — Given Phần VI, When đính kèm, Then upload đúng thứ tự: Bảng kê →
  Minh Họa Dòng Tiền → Hồ sơ mở tài khoản → Hồ sơ KH → Tài liệu khác.

### US3.3 — Chặn giá trị tick ngoài định nghĩa
**As a** Người lập báo cáo, **I want** robot dừng khi gặp giá trị tick ngoài tập
định nghĩa ở Phần IV/V, **so that** không nộp dữ liệu sai.
Ưu tiên: **Must Have**. Truy vết: FR10.
- **AC3.3.1** — Given một giá trị tick không thuộc tập định nghĩa, When nhập Phần
  IV/V, Then dừng luồng KH đó và gửi email lỗi.

---

## Nhóm US4 — Xử lý lỗi & độ bền (tách story riêng)

### US4.1 — Retry khi bước nhập lỗi
**As a** RPA Ops, **I want** robot tự thử lại bước nhập bị lỗi tối đa 3 lần,
**so that** lỗi tạm thời không làm hỏng báo cáo.
Ưu tiên: **Must Have**. Truy vết: FR11.1, NFR3.
- **AC4.1.1** — Given một bước nhập lỗi, When xảy ra, Then robot retry tối đa 3 lần.

### US4.2 — Thông báo thất bại sau 3 lần retry
**As a** Người nhận cảnh báo khi báo cáo chạy lỗi, **I want** nhận email báo lỗi
khi robot vẫn thất bại sau 3 lần retry, **so that** xử lý nghiệp vụ bù kịp thời.
Ưu tiên: **Must Have**. Truy vết: FR11.2.
- **AC4.2.1** — Given đã retry 3 lần vẫn lỗi, When vượt ngưỡng, Then gửi email báo
  thất bại qua mail exchange (không chuyển robot thứ hai).

### US4.3 — Cô lập lỗi theo khách hàng
**As a** RPA Ops, **I want** lỗi một KH không làm hỏng cả lô,
**so that** các KH còn lại vẫn được xử lý.
Ưu tiên: **Must Have**. Truy vết: FR12, NFR3.
- **AC4.3.1** — Given một KH gặp lỗi dừng luồng, When xảy ra, Then robot ghi nhận
  (mã lỗi + chi tiết + CIF) và chuyển sang KH kế tiếp.

---

## Nhóm US5 — Bảo mật & lưu vết

### US5.1 — Không hardcode secrets
**As a** RPA Ops, **I want** mọi credentials đọc từ biến môi trường/secrets manager,
**so that** bí mật không lộ trong mã nguồn.
Ưu tiên: **Must Have**. Truy vết: NFR4.
- **AC5.1.1** — Given cần credentials (AMLD, Accuity, Cục Thuế, ECM, mail), When
  robot dùng, Then đọc từ cấu hình/biến môi trường, không hardcode.

### US5.2 — Lưu vết xử lý
**As a** RPA Ops, **I want** robot ghi log từng bước và kết quả theo KH,
**so that** truy vết được và dựng file trạng thái.
Ưu tiên: **Should Have**. Truy vết: NFR5.
- **AC5.2.1** — Given xử lý một KH, When mỗi bước chạy, Then ghi log kết quả
  (thành công/lỗi + mã lỗi) đủ để dựng file trạng thái đính kèm email.

---

## Nhóm US6 — Thông báo trạng thái lô

### US6.1 — Tổng hợp trạng thái lô
**As a** Người lập báo cáo, **I want** robot tổng hợp trạng thái từng KH trong lô,
**so that** có bức tranh đầy đủ sau khi xử lý.
Ưu tiên: **Must Have**. Truy vết: FR12.1.
- **AC6.1.1** — Given xử lý xong lô, When tổng hợp, Then có bảng STT, STR_CIF,
  Trạng thái, Mã lỗi, Chi tiết lỗi.

### US6.2 — Gửi email trạng thái lô
**As a** Người lập báo cáo, **I want** nhận email trạng thái lô kèm file chi tiết,
**so that** biết kết quả mà không cần kiểm tra portal.
Ưu tiên: **Must Have**. Truy vết: FR13.
- **AC6.2.1** — Given lô xử lý xong, When gửi email, Then From/Cc =
  `nguyendinhhai1996@hotmail.com`, To = email người lập báo cáo, đính kèm file
  excel trạng thái, tiêu đề/nội dung theo template.
- **AC6.2.2** — Given gửi email, When thực hiện, Then qua hệ thống mail exchange.

---

## Ghi chú ưu tiên

- Must Have: US1.1–US1.5, US2.1, US2.2, US3.1, US3.2, US3.3, US4.1, US4.2, US4.3,
  US5.1, US6.1, US6.2.
- Should Have: US2.3 (Cục Thuế), US5.2 (lưu vết).
- Ranh giới MVP chính thức chốt ở Delivery Planning.
