# Requirements — Robot RPA nhập liệu báo cáo STR lên AMLD Portal NHNN

## Sources

- `docs/08_US2_TomTat.md` — Tài liệu US2 v1.3 (05/10/2026), nguồn nghiệp vụ chính.
- `docs/SERVICES_CONNECTION_INFO.md` — Thông tin kết nối môi trường dev local (Mock Server ECM, Kafka, RabbitMQ).
- `aidlc/spaces/default/intents/261009-str-rpa-robot/inception/requirements-analysis/requirements-analysis-questions.md` — 8 quyết định làm rõ với người yêu cầu.
- `aidlc/spaces/default/memory/team.md`, `project.md` — thực hành & ràng buộc đã chốt ở giai đoạn trước.

## Phân tích mục tiêu (Intent)

Người dùng nghiệp vụ (Phòng QTRRHĐ & PCRT) muốn tự động hóa toàn bộ chu trình lập
và nộp báo cáo giao dịch đáng ngờ (STR) lên cổng AMLD Online Portal của NHNN.
Hiện quy trình làm thủ công, mất hơn 15 phút/báo cáo và dễ sai sót khi nhập nhiều
phần. Mục tiêu là một robot (RPA/AI-agent) đọc dữ liệu nguồn, tra cứu đối chiếu
trên hệ thống ngoài, nhập liệu đầy đủ các Phần của Mẫu số 01, đính kèm tài liệu,
và gửi email trạng thái — đạt độ chính xác dữ liệu ≥ 90% và rút thời gian hoàn
thiện xuống ≤ 15 phút/báo cáo.

Giá trị cốt lõi là **tuân thủ** (nộp đúng, đủ, đúng hạn theo yêu cầu phòng chống
rửa tiền của NHNN) và **giảm công sức/sai sót thủ công**.

## Yêu cầu chức năng (Functional Requirements)

### FR1 — Kích hoạt & nhận việc theo hàng đợi Kafka
- FR1.1 — Robot chạy thường trực như một consumer của Kafka tại `localhost:9092`
  (PLAINTEXT), topic `RPA_STR_NHNN_INPUT`. Cổng 9092 không yêu cầu
  user/password.
- FR1.2 — Mỗi message mô tả một lô (hoặc một khách hàng) cần xử lý; khi nhận
  message hợp lệ, robot bắt đầu xử lý ngay, không chờ lịch cố định.
- FR1.3 — Message lỗi hoặc không hợp lệ được ghi log và không làm dừng consumer;
  robot tiếp tục nhận message kế tiếp.

### FR2 — Nhận diện thư mục nguồn theo ngày
- FR2.1 — Robot nhận diện thư mục nguồn theo ngày hiện tại, dạng
  `/Users/hainguyen/Projects/RPA/AMLD/YYYYMM/YYYYMMDD`; mỗi thư mục con là một
  khách hàng (CIF). Robot chạy local nên mặc định có quyền đọc/ghi thư mục này.
- FR2.2 — Không có cơ chế LOG_DONE: robot không chờ file hoàn thành nguồn; việc
  một lô sẵn sàng được báo qua message Kafka (FR1).

### FR3 — Thu thập & kiểm tra đủ dữ liệu đầu vào trong folder CIF
- FR3.1 — Với mỗi folder CIF, robot đọc 5 file excel nguồn từ thư mục local:
  - `ca_nhan_thuc_hien_giao_dich.xlsx` **hoặc** `to_chuc_thuc_hien_giao_dich.xlsx`,
  - `bang_ke_giao_dich_tai_khoan_dang_ngo.xlsx`,
  - `thong_tin_giao_dich_dang_ngo.xlsx`,
  - `thong_tin_dau_vao_bao_cao_str.xlsx`.
- FR3.2 — PDF hồ sơ khách hàng (hồ sơ mở tài khoản `HSMTK%`, giấy tờ tùy thân,
  giấy phép thành lập...) được lấy qua **ECM mock API** (xem FR14), không đọc từ
  thư mục local.
- FR3.3 — Nếu thiếu file excel bắt buộc hoặc không lấy được hồ sơ PDF cần thiết:
  ghi nhận tên (các) mục thiếu, chuyển sang luồng tổng hợp lỗi của khách hàng đó
  (FR12) và gửi email trạng thái FAIL (FR13), dừng luồng khách hàng đó.

### FR4 — Phân loại khách hàng
- FR4.1 — Robot xác định loại khách hàng (KHCN hay KHDN) từ dữ liệu file nguồn.
- FR4.2 — Robot xử lý được cả KHCN và KHDN ngay từ đầu; các bước phụ thuộc loại
  khách hàng (tra cứu Cục Thuế, Phần II) rẽ nhánh theo loại.

### FR5 — Tổng hợp sơ đồ dòng tiền
- FR5.1 — Từ `bang_ke_giao_dich_tai_khoan_dang_ngo.xlsx`, robot tính và vẽ sơ đồ
  minh họa dòng tiền, lưu thành `Minh Họa Dòng Tiền.pdf`.
- FR5.2 — Shape bên trái (tiền vào, HUONG_GD=C): số lượng KH gửi vào =
  count distinct(TK_DOIUNG + TENKH_DOIUNG); số GD vào = count(MA_GD); số tiền vào
  = sum(SOTIEN_GD_QD).
- FR5.3 — Shape giữa: tên ĐTBC lấy từ `thong_tin_dau_vao_bao_cao_str.xlsx`
  (STR_TEN_KH).
- FR5.4 — Shape bên phải (tiền ra, HUONG_GD=D): tính tương tự FR5.2 với
  HUONG_GD=D.

### FR6 — Tra cứu Accuity (web mock)
- FR6.1 — Robot thao tác với một **web Accuity mô phỏng (mock)**: có trang
  đăng nhập (user/password) và nút export sinh file PDF kết quả tra cứu.
- FR6.2 — Chọn Entity Type theo loại KH (Individual cho KHCN, Organization cho
  KHDN), chọn Single, nhập tên từ STR_TEN_KH, submit.
- FR6.3 — Export/print kết quả tra cứu ra `Tra cứu Accuity.pdf`; khi Match Score
  = 100 thì mở bản ghi và print hồ sơ ra `Tra cứu Accuity(n).pdf`.
- FR6.4 — Nếu đăng nhập/thao tác Accuity thất bại: lưu địa chỉ web, chuyển luồng
  tổng hợp lỗi (FR12) và gửi email lỗi (FR13).

### FR7 — Tra cứu tình trạng người nộp thuế (Cục Thuế, web thật — chỉ KHDN)
- FR7.1 — Chỉ thực hiện khi khách hàng là KHDN.
- FR7.2 — Robot thao tác với **web thật của Cục Thuế**: mở tab "Thông tin về
  người nộp thuế", nhập mã số thuế (từ `Ma_So_Doanh_Nghiep`).
- FR7.3 — Robot đọc và nhập captcha bằng framework **ddddocr**.
- FR7.4 — Nếu không có kết quả: bỏ qua; nếu có kết quả: print
  `Tra cứu tình trạng người nộp thuế.pdf`.
- FR7.5 — Nếu bước tra cứu lỗi (timeout, lỗi robot): chuyển luồng tổng hợp lỗi
  (FR12).

### FR8 — Đăng nhập AMLD Online Portal (web thật)
- FR8.1 — Robot đăng nhập **AMLD Online Portal thật** với Username =
  USER_ID_NGUOI_LAP_BAO_CAO, Password = PASSWORD_NGUOI_LAP_BAO_CAO.
- FR8.2 — Nếu treo màn hình đăng nhập: reload và đăng nhập lại tối đa 3 lần;
  quá 3 lần thì gửi email lỗi (FR13).

### FR9 — Nhập liệu Mẫu số 01 trên AMLD Portal
- FR9.1 — Vào tab "Nhập STR" → "Mẫu số 01"; nhập theo thứ tự ưu tiên Phần I → II
  → IV → V → VI. **Không điền Phần III.**
- FR9.2 — **Phần I (ĐTBC):** nhập thông tin đối tượng báo cáo theo bảng mapping
  (mục 6.1 tài liệu), lưu Phần I, xác nhận popup. Các trường mặc định (tên/mã
  ĐTBC, email đơn vị, người chịu trách nhiệm PCRT) điền theo giá trị cố định; các
  trường địa điểm phát sinh và người lập lấy từ dữ liệu nguồn.
- FR9.3 — **Phần II (CN/TC thực hiện GD):**
  - KHCN: upload `ca_nhan_thuc_hien_giao_dich.xlsx`, tick "Trùng với cá nhân
    thực hiện" ở mục chủ sở hữu hưởng lợi, lưu.
  - KHDN: upload `to_chuc_thuc_hien_giao_dich.xlsx`, chọn người đại diện có GTTT
    ngày cấp mới nhất (từ sheet `NDD_Thong_Tin_Dinh_Danh` hoặc từ màn hình "Xem"),
    lưu.
- FR9.4 — **Phần IV (Thông tin GD đáng ngờ):** tick loại báo cáo, dấu hiệu đáng
  ngờ, trạng thái GD, thời gian GD (min/max), tổng tiền nguyên tệ (sum theo
  LOAITIEN), mô tả bảng dòng tiền (upload `thong_tin_giao_dich_dang_ngo.xlsx`),
  mô tả lý do, cơ sở nghi ngờ, loại tội phạm; lưu Phần IV.
- FR9.5 — **Phần V (Công việc xử lý):** tick các công việc đã thực hiện
  (checkbox 1–9); nếu dữ liệu có ít nhất một trong giá trị 6/7/8 thì mặc định
  tick thêm 4 và 5; lưu Phần V.
- FR9.6 — **Phần VI (Tài liệu đính kèm):** upload theo thứ tự: Bảng kê → Minh Họa
  Dòng Tiền.pdf → Hồ sơ mở tài khoản (`HSMTK%`) → Hồ sơ khách hàng
  (`Giay phep thanh lap%`/`GTTT%`/...) → Tài liệu khác (`Tra cứu Accuity%`,
  `Tra cứu tình trạng người nộp thuế.pdf`). Đếm đúng số trang mỗi file; nhiều
  file cùng loại thì upload lần lượt.

### FR10 — Kiểm tra giá trị tick ngoài định nghĩa
- FR10.1 — Nếu một mục tick chọn ở Phần IV/V có giá trị không nằm trong tập định
  nghĩa: dừng luồng khách hàng đó và gửi email thông báo lỗi (FR13).

### FR11 — Retry và thông báo thất bại
- FR11.1 — Mỗi bước nhập báo cáo lỗi được retry tối đa 3 lần.
- FR11.2 — Nếu vẫn thất bại sau 3 lần retry: robot gửi email báo thất bại qua
  mail exchange (không có cơ chế robot thứ hai trong phạm vi code này).

### FR12 — Tổng hợp lỗi theo khách hàng
- FR12.1 — Mọi lỗi của một khách hàng (thiếu file, lỗi tra cứu, lỗi nhập, giá
  trị ngoài định nghĩa) được ghi nhận: mã lỗi + chi tiết lỗi + CIF.
- FR12.2 — Khi một khách hàng gặp lỗi dừng luồng, robot dừng xử lý khách hàng đó
  và chuyển sang khách hàng kế tiếp trong lô.

### FR13 — Gửi email trạng thái lô
- FR13.1 — Sau khi xử lý xong một lô, robot gửi email trạng thái:
  - From: `nguyendinhhai1996@hotmail.com`
  - To: email người lập báo cáo (`EMAIL_NGUOI_LAP_BAO_CAO`)
  - Cc: `nguyendinhhai1996@hotmail.com`
  - Đính kèm: file excel trạng thái (STT, STR_CIF, Trạng thái, Mã lỗi, Chi tiết lỗi)
  - Tiêu đề/nội dung theo template mục 5.4 tài liệu.
- FR13.2 — Email được gửi qua hệ thống mail exchange.

### FR14 — Lấy hồ sơ khách hàng qua ECM mock API
- FR14.1 — Robot lấy file PDF hồ sơ khách hàng qua **ECM mock API**
  (`http://localhost:8831`, mô tả tại `docs/SERVICES_CONNECTION_INFO.md`).
- FR14.2 — Luồng gọi: lấy token qua endpoint auth (client_credentials) → search
  file theo `customerCode` tại `/ecm-core-v1.0/businesses/{business_code}/files/search`
  → tải nội dung file theo `doc_id` tại `/ecm-core-v1.0/files/{doc_id}/content`
  (trả về PDF).
- FR14.3 — Credentials/token của ECM đọc từ cấu hình/biến môi trường, không
  hardcode (NFR4).
- FR14.4 — Nếu gọi ECM lỗi hoặc không có hồ sơ bắt buộc: chuyển luồng tổng hợp
  lỗi (FR12) và gửi email FAIL (FR13).

## Yêu cầu phi chức năng (Non-Functional Requirements)

- **NFR1 — Độ chính xác dữ liệu:** Dữ liệu nhập lên portal so khớp với hệ thống
  T24 đạt ≥ 90% (đo hàng tháng từ ngày golive).
- **NFR2 — Thời gian xử lý:** Thời gian trung bình hoàn thiện một báo cáo ≤ 15
  phút/báo cáo.
- **NFR3 — Độ bền với lỗi hệ thống ngoài:** Mọi tương tác web/API/hệ thống ngoài
  phải có xử lý lỗi (timeout, treo màn hình, captcha fail): retry ≤ 3 lần cho
  bước nhập, reload ≤ 3 lần cho đăng nhập, rồi gửi email lỗi; không để lỗi một
  khách hàng làm hỏng cả lô.
- **NFR4 — Bảo mật/credentials:** Credentials của AMLD Portal, Accuity, Cục Thuế,
  ECM và mail không được hardcode; đọc từ biến môi trường hoặc secrets manager.
- **NFR5 — Lưu vết (logging):** Mỗi bước xử lý theo khách hàng và kết quả (thành
  công/lỗi, mã lỗi) được ghi log đủ để truy vết và dựng file trạng thái đính kèm
  email.
- **NFR6 — Khả năng kiểm thử:** Các hệ thống ngoài phải trừu tượng hóa sau một
  lớp giao tiếp để thay bằng mock/fixtures trong test tự động (Accuity luôn mock;
  ECM dùng mock server local; AMLD/Cục Thuế mock trong test, thật khi chạy
  production).
- **NFR7 — Môi trường vận hành:** Robot chạy local trên máy này; không có pipeline
  nhiều môi trường. Kafka (`localhost:9092`) là nguồn kích hoạt công việc; ECM
  mock server và dữ liệu local là nguồn dữ liệu.

## Ràng buộc (Constraints)

- **C1** — Ngôn ngữ/nền tảng: Python + Playwright/Selenium (điều khiển trình
  duyệt, xử lý excel/PDF).
- **C2** — Captcha Cục Thuế: dùng framework ddddocr.
- **C3** — Accuity là web mock (login user/pass + nút export PDF kết quả); AMLD
  Portal và Cục Thuế là web thật khi chạy production.
- **C4** — Dữ liệu nguồn: 5 file excel đọc từ thư mục local
  `/Users/hainguyen/Projects/RPA/AMLD/YYYYMM/YYYYMMDD`; PDF hồ sơ KH lấy qua ECM
  mock API `http://localhost:8831`.
- **C5** — Thứ tự nhập Mẫu số 01: I → II → IV → V → VI, không điền Phần III.
- **C6** — Thứ tự upload Phần VI cố định như FR9.6.
- **C7** — Chạy local; kích hoạt qua Kafka `localhost:9092` (PLAINTEXT) topic
  `RPA_STR_NHNN_INPUT` (không user/pass); gửi mail qua mail exchange.
- **C8** — Không có cơ chế LOG_DONE: tín hiệu một lô sẵn sàng đến từ message
  Kafka.

## Giả định (Assumptions)

- **A1** — Các file nguồn đã đủ và đúng định dạng khi robot nhận việc (robot vẫn
  kiểm tra sự hiện diện và file bắt buộc, nhưng không kiểm định sâu nội dung ngoài
  các phép tính được mô tả).
- **A2** — Robot chạy local nên mặc định có quyền đọc/ghi thư mục nguồn
  `/Users/hainguyen/Projects/RPA/AMLD/YYYYMM/YYYYMMDD`; ECM mock server và Kafka
  chạy sẵn trên máy (theo `docs/SERVICES_CONNECTION_INFO.md`).
- **A3** — Giao diện/selector của AMLD Portal và Cục Thuế đủ ổn định để tự động
  hóa; nếu đổi giao diện cần cập nhật selector (rủi ro R1).
- **A4** — Mẫu Phần IV/V dùng tập giá trị checkbox như tài liệu mô tả (loại báo
  cáo, dấu hiệu 1–23, công việc 1–9, loại tội phạm 1–30).
- **A5** — Message Kafka chứa đủ thông tin để robot xác định lô/ngày/khách hàng
  cần xử lý (schema message sẽ chốt ở giai đoạn thiết kế).

## Ngoài phạm vi (Out of Scope)

- **O1** — Xuất 5 file excel nguồn từ KDL (thuộc US1); trong phạm vi dự án này
  các file được coi là có sẵn trong thư mục local.
- **O2** — ECM/FCRM thật: trong phạm vi dự án này dùng ECM **mock server** local
  (`docs/SERVICES_CONNECTION_INFO.md`), không tích hợp ECM/FCRM production.
- **O3** — Thiết kế lại quy trình pháp lý/quy định của NHNN (robot chỉ tuân thủ).
- **O4** — Cài đặt instance robot thứ hai và cơ chế bàn giao giữa các robot
  (chỉ gửi email báo thất bại sau 3 lần retry).
- **O5** — Môi trường test/sandbox của NHNN (chưa có; chạy thật dùng credentials
  nghiệp vụ cấp sau).

## Assumptions & Open Questions

- **OQ1** — Schema cụ thể của message Kafka (định dạng payload, cách map
  message → thư mục ngày/CIF) — chốt ở giai đoạn thiết kế.
- **OQ2** — Chi tiết các giá trị mặc định đầy đủ của Phần I (địa chỉ, điện thoại
  cố định) — lấy từ bảng mapping mục 6.1; cần xác nhận giá trị production.
- **OQ3** — Yêu cầu khả năng chịu tải (số lô/ngày, số KH đồng thời) — tài liệu để
  trống (mục 4.4); sẽ ước lượng ở giai đoạn NFR.
- **OQ4** — Cách map `customerCode`/`business_code` của ECM mock sang từng khách
  hàng CIF và từng loại hồ sơ PDF — chốt ở giai đoạn thiết kế.

Các giả định (A1–A5) và câu hỏi mở (OQ1–OQ4) ở trên là những điểm chưa chắc chắn
được chuyển tiếp cho các giai đoạn sau. Không có mâu thuẫn chưa giải quyết nào
còn tồn đọng giữa các yêu cầu.
