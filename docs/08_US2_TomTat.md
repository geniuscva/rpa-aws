# US2 — Xây dựng robot tự động nhập liệu báo cáo giao dịch đáng ngờ (STR) trên web portal NHNN

---

## 1. Overview

### 1.1. Thông tin yêu cầu

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên yêu cầu** | Xây dựng chức năng báo cáo giao dịch đáng ngờ (STR) tự động tuân thủ yêu cầu giám sát giao dịch, phòng chống rửa tiền từ NHNN |
| **Loại yêu cầu** | Phát triển MỚI tính năng/sản phẩm |
| **Jira** | FCRM-6209 — Xây dựng Robot báo cáo STR tự động |
| **Trạng thái Jira** | ⚠️ Cancelled |
| **Người yêu cầu** | Ngô Vũ Hoàng Minh |
| **SA/DEV Lead** | Nguyen Chi Nghiep |
| **BA** | Phạm Minh Đức |
| **Phiên bản tài liệu** | v1.3 (05/10/2026) |
| **Ngày áp dụng** | 18 Nov 2025 |
| **Tài liệu tham chiếu** | US1 (KDL xuất file), US3 (Call API ECM), EPIC (Ứng dụng RPA nhập báo cáo STR) |

### 1.2. Bối cảnh & Lý do

- **Hiện trạng:** Việc xây hệ thống báo cáo giao dịch đáng ngờ (STR) tự động **chưa được triển khai tại MB**.
- **Nguyên nhân:** Platform báo cáo GD đáng ngờ của NHNN mới đi vào hoạt động từ **tháng 9/2025**.
- **Mong muốn:** "Là người dùng, tôi muốn xây dựng robot để phục vụ tự động báo cáo giao dịch đáng ngờ (STR) lên cổng portal của NHNN."

### 1.3. Phạm vi

#### Trong phạm vi (In-scope)
- Đọc & tổng hợp 5 file nguồn từ KDL (folder `\10.1.18.197\tt35 share\QTRR\...`)
- Kiểm tra đủ file bắt buộc & log hoàn thành (LOG_DONE)
- Tra cứu đối chiếu: **Accuity** + **Cục Thuế** (KHDN)
- Nhập liệu & upload lên **AMLD Online Portal NHNN** (Phần I, II, IV, V, VI)
- Cơ chế **retry (3 lần)** + chuyển robot dự phòng khi lỗi kéo dài
- **Gửi email** thông báo trạng thái từng KH trong lô

#### Ngoài phạm vi (Out-of-scope)
- Xuất file báo cáo từ KDL (đã có **US1** riêng)
- Gọi API lấy hồ sơ KH từ ECM/FCRM (đã có **US3** riêng)
- Thiết kế lại quy trình pháp lý/quy định của NHNN (chỉ tuân thủ)

### 1.4. Vai trò trong chuỗi (liên hệ với EPIC/US1/US3)

```
┌────────────────────────────────────────────────────┐
│      EPIC: ỨNG DỤNG RPA TRONG QUY TRÌNH NHẬP STR  │
└────────────────────────────────────────────────────┘
          │                      │                     │
   ┌──────▼──────┐        ┌──────▼──────┐      ┌──────▼──────┐
   │ US1 (KDL)   │──────▶ │  US2 (ROBOT)│◀─────│ US3 (ECM)   │
   │ 5 file excel│  đầu   │  nhập liệu  │  hồ   │ call API    │
   │             │  vào   │  STR        │  sơ   │ lấy hồ sơ   │
   │             │        │  ⭐ use case│  PDF  │ KH          │
   └─────────────┘        └─────────────┘      └─────────────┘
```

> **US2 là use case trung tâm** của đội tại Workshop AI-DLC — nhận đầu vào từ US1 (dữ liệu) và US3 (hồ sơ PDF), thực hiện tự động hóa nhập liệu lên portal NHNN.

### 1.5. Các nguồn dữ liệu đầu vào

| Nguồn | File | Mô tả | Từ tài liệu |
|-------|------|-------|-------------|
| **KDL** | `thong_tin_dau_vao_bao_cao_str.xlsx` | Thông tin đầu vào báo cáo STR | US1 |
| **KDL** | `ca_nhan_thuc_hien_giao_dich.xlsx` | Cá nhân thực hiện GD (KHCN) | US1 |
| **KDL** | `to_chuc_thuc_hien_giao_dich.xlsx` | Tổ chức thực hiện GD (KHDN) | US1 |
| **KDL** | `bang_ke_giao_dich_tai_khoan_dang_ngo.xlsx` | Bảng kê GD tài khoản đáng ngờ | US1 |
| **KDL** | `thong_tin_giao_dich_dang_ngo.xlsx` | Thông tin GD đáng ngờ | US1 |
| **ECM/FCRM** | File PDF dạng `HSMTK%`, `GTTT%`, `Giay phep thanh lap%`... | Hồ sơ khách hàng | US3 |

### 1.6. Stakeholders

| Stakeholder | Vai trò |
|-------------|---------|
| **Người lập báo cáo (QTRR)** | Người nhận email trạng thái, chịu trách nhiệm nghiệp vụ |
| **Phòng QTRRHĐ & PCRT** | Đơn vị sở hữu quy trình, người duyệt |
| **KDL (Kho dữ liệu)** | Cung cấp 5 file excel nguồn (US1) |
| **FCRM / ECM** | Cung cấp hồ sơ khách hàng (US3) |
| **NHNN (AMLD Portal)** | Cổng nhận báo cáo, không do MB kiểm soát |
| **RPA Team / Ops** | Vận hành robot, xử lý lỗi |

---

## 2. Problem Statement

> *(Phiên bản 2–3 câu, dùng cho phần AS-IS / mở đầu)*

**Tiếng Việt:**
Hiện nay, việc lập và nộp báo cáo giao dịch đáng ngờ (STR) cho NHNN tại MB Bank vẫn được thực hiện thủ công, tốn nhiều thời gian (trung bình hơn 15 phút/báo cáo) và dễ xảy ra sai sót do nhập liệu nhiều phần trên cổng AMLD Online Portal. Chúng tôi muốn xây dựng một robot (RPA/AI-agent) tự động đọc dữ liệu từ các nguồn (KDL, FCRM, ECM), tra cứu đối chiếu trên các hệ thống ngoài (Accuity, Cục Thuế) và nhập liệu hoàn chỉnh lên portal NHNN — đảm bảo tính đầy đủ, chính xác ≥ 90% và rút thời gian hoàn thiện xuống ≤ 15 phút/báo cáo.

**Tiếng Anh (dùng khi trình bày có lãnh đạo):**
MB Bank currently prepares Suspicious Transaction Reports (STR) for the State Bank of Vietnam manually — taking over 15 minutes per report and risking data-entry errors across multiple sections of the AMLD Online Portal. We want to build an AI-driven automation robot that reads source data, cross-checks external references (Accuity, Tax Authority), and fills the STR forms end-to-end, achieving ≥ 90% data accuracy and completing each report within 15 minutes.

### Giá trị kinh doanh

| Tiêu chí | Hiện trạng (AS-IS) | Mục tiêu (TO-BE) |
|----------|-------------------|------------------|
| Thời gian hoàn thiện 1 báo cáo | > 15 phút | **≤ 15 phút** |
| Độ đầy đủ/chính xác dữ liệu | Thủ công, phụ thuộc con người | **≥ 90%** |
| Khối lượng xử lý | Giới hạn theo năng suất con người | **Tự động hóa toàn bộ lô** |
| Tuân thủ phòng chống rửa tiền | Rủi ro chậm/sai | **Tuân thủ đúng thời hạn NHNN** |

---

## 3. Mục tiêu và Tiêu chí đo lường

### 3.1. Mục tiêu thực hiện (CARD)

| Yếu tố | Nội dung |
|--------|----------|
| **C** (Current - Hiện trạng) | Chưa có hệ thống báo cáo GD đáng ngờ tự động tại MB |
| **A** (Action - Hành động) | Xây dựng robot RPA/AI-agent tự động nhập liệu STR |
| **R** (Result - Kết quả) | Tự động hóa toàn bộ chu trình báo cáo lên portal NHNN |
| **D** (Desire - Mong muốn) | Robot đọc dữ liệu nguồn, tra cứu đối chiếu, nhập liệu hoàn chỉnh, gửi thông báo |

### 3.2. Tiêu chí đo lường hiệu quả kinh doanh/nghiệp vụ

| Tiêu chí | Cách thức đo lường | Thời gian đo | Kết quả đăng ký |
|----------|--------------------|--------------|-----------------|
| Tính đầy đủ, chính xác của dữ liệu | So khớp thông tin KH với hệ thống T24 của mỗi báo cáo | 1 tháng từ ngày golive, hàng tháng | **≥ 90%** |

### 3.3. Tiêu chí đo lường mức độ sử dụng

| Tiêu chí | Cách thức đo lường | Thời gian đo | Kết quả đăng ký |
|----------|--------------------|--------------|-----------------|
| Thời gian trung bình hoàn thiện 1 báo cáo | Nghiệp vụ lưu lại mốc thời gian hoàn thiện báo cáo | 1 tháng từ ngày golive, hàng tháng | **≤ 15 phút/báo cáo** |

---

## 4. Quy trình xử lý

### 4.1. Sơ đồ quy trình tổng quan

```
Bắt đầu
   │
   ▼
B7. Đẩy file hồ sơ từng KH vào folder CIF  (Hệ thống NHNN)
   │
   ▼
B8. Kiểm tra luồng lấy thông tin KH hoàn thành  (RPA)
   │  Kiểm tra 2 file LOG_DONE
   ├── Đủ 2 file ──▶ B9
   └── Thiếu 2 file ──▶ Kết thúc
   │
   ▼
B9. Kiểm tra đủ file bắt buộc trong folder CIF  (RPA)
   ├── Đủ ──▶ B10
   └── Thiếu ──▶ B15 (tổng hợp lỗi)
   │
   ▼
B10. Tổng hợp sơ đồ dòng tiền  (RPA)  ──▶ B11
   ▼
B11. Tra cứu tình trạng người nộp thuế (KHDN)  (RPA)
   ├── Thành công ──▶ B12
   └── Lỗi ──▶ B15
   ▼
B12. Đăng nhập Accuity, tổng hợp kết quả tra cứu  (RPA)
   ├── Thành công ──▶ B13
   └── Lỗi ──▶ B15
   ▼
B13. Đăng nhập AMLD Online Portal NHNN  (RPA)
   ├── Thành công ──▶ B14
   └── Lỗi ──▶ B15
   ▼
B14. Nhập thông tin, upload file vào các mục báo cáo  (RPA)
   │  Phần I, II, IV, V, VI
   │  Retry ≤ 3 lần; vẫn lỗi ──▶ chuyển robot dự phòng
   ├── Thành công ──▶ B16
   └── Lỗi ──▶ B15
   ▼
B15. Tổng hợp lỗi từng KH + dừng luồng KH  (RPA)
   │
   ▼
B16. Gửi email thông báo trạng thái từng KH trong lô  (RPA)
   │
   ▼
Kết thúc
```

### 4.2. Diễn giải quy trình (16 bước)

| Bước | Đơn vị | Mô tả nghiệp vụ/Phân tích chi tiết | Tham chiếu |
|------|--------|-----------------------------------|------------|
| **7** | Hệ thống NHNN | Đẩy các file hồ sơ từng KH thành folder tại `\10.1.18.197\tt35 share\QTRR\YYYYMM\YYYYMMDD\CUS.T24.CIF` gồm: 5 file excel (từ US1-KDL) + file PDF hồ sơ (từ US3-FCRM/ECM). Cấp quyền truy cập cho `rpa_it@mbbank.com.vn` | US1, US3 |
| **8** | RPA | Kiểm tra luồng lấy thông tin KH hoàn thành: mỗi ngày 2 lượt quét folder, kiểm tra 2 file log của 2 nguồn (ECM + excel). Đủ 2 file → bước 11; thiếu → kết thúc luồng | 3.1.3.1 |
| **9** | RPA | Kiểm tra folder CIF KH có đủ file bắt buộc: Đủ → bước 10; thiếu → bước 15 | 3.1.3.2 |
| **10** | RPA | Tổng hợp file minh họa sơ đồ dòng tiền | 3.1.3.3 bước 1 |
| **11** | RPA | Tra cứu tình trạng người nộp thuế (áp dụng KHDN). Lỗi (timeout, lỗi Robot) → bước 15; thành công → bước 12 | 3.1.3.3 bước 3 |
| **12** | RPA | Đăng nhập web Accuity, tổng hợp kết quả tra cứu KH với danh sách Accuity. Lỗi → bước 15; thành công → bước 13 | 3.1.3.3 bước 2 |
| **13** | RPA | Đăng nhập AMLD Online Portal NHNN, nhập thông tin/upload file vào các mục báo cáo: Phần I - ĐTBC, Phần II - CN/TC thực hiện GD, Phần IV - Thông tin GD đáng ngờ, Phần V - Công việc xử lý. Cơ chế retry ≤ 3 lần; vẫn lỗi → chuyển robot khác. Thành công → bước 14 | 3.1.3.3 bước 4,5,6,7,8,9,10 |
| **14** | RPA | Tổng hợp trạng thái thành công của KH | — |
| **15** | RPA | Tổng hợp lỗi của từng luồng cho từng KH + dừng luồng KH | — |
| **16** | RPA | Gửi email thông báo trạng thái xử lý từng KH trong cả lô | 3.1.3.4 |

---

## 5. Tham chiếu chi tiết

### 5.1. Robot kiểm tra file ghi log hoàn thành của các hệ thống nguồn (3.1.3.1)

- **Nhận diện folder:** Theo ngày hiện tại. VD: ngày 30/07/2026 → quét `\10.1.18.197\tt35 share\QTRR\202607\20260730`, các folder con = 1 KH (CIF).
- **Nhận diện nguồn hoàn thành khi có file log `LOG_DONE`**:
  - File log excel: `LOG_DONE` tại folder cha (cùng cấp với folder CIF) — excel lấy đủ cả lô.
  - File log hồ sơ: `LOG_DONE` trong từng folder CIF — hồ sơ KH lấy đủ từng KH.
- Nếu nguồn chưa hoàn thành → **Robot không thực hiện**.

### 5.2. Robot kiểm tra đủ file bắt buộc trong folder CIF (3.1.3.2)

Nguồn đã đủ file khi folder `...\CUS.T24.CIF` gồm **đồng thời**:
- `ca_nhan_thuc_hien_giao_dich.xlsx` **hoặc** `to_chuc_thuc_hien_giao_dich.xlsx` + file PDF dạng `HSMTK%`
- `bang_ke_giao_dich_tai_khoan_dang_ngo.xlsx`
- `thong_tin_giao_dich_dang_ngo.xlsx`
- `thong_tin_dau_vao_bao_cao_str.xlsx`

> Nếu thiếu file → ghi nhận tên file thiếu, gửi mail theo template lỗi (3.1.3.4).

### 5.3. RPA thực hiện nhập báo cáo đáng ngờ (3.1.3.3)

Thực hiện theo thứ tự sau:

| STT | Website | Mô tả bước thao tác |
|-----|---------|--------------------|
| **1** | — | Vẽ minh họa sơ đồ dòng tiền, lưu PDF tên `Minh Họa Dòng Tiền.pdf`. Tính toán từ `bang_ke_giao_dich_tai_khoan_dang_ngo.xlsx`: <br>• **Shape 1 (trái):** Số lượng KH gửi vào = count distinct(TK_DOIUNG + TENKH_DOIUNG) với HUONG_GD=C; Số GD vào = count(MA_GD) với HUONG_GD=C; Số tiền vào = sum(SOTIEN_GD_QD) với HUONG_GD=C<br>• **Shape 2 (giữa):** Tên ĐTBC từ `thong_tin_dau_vao_bao_cao_str.xlsx` (STR_TEN_KH)<br>• **Shape 3 (phải):** Tương tự shape 1 nhưng HUONG_GD=D |
| **2** | `accuity.worldcompliance.com` | **Case 1 (đăng nhập thành công):** <br>• 2.1: Đăng nhập (user/password nghiệp vụ cung cấp)<br>• 2.2: Chọn Entity Type: Individual (KHCN) / Organization (KHDN)<br>• 2.3: Chọn Single, nhập tên từ STR_TEN_KH<br>• 2.4: Submit<br>• 2.5: Print kết quả → `Tra cứu Accuity.pdf`<br>• 2.6: Nếu Match Score = 100 → click bản ghi<br>• 2.7: Print hồ sơ → `Tra cứu Accuity(n).pdf`<br>**Case 2 (đăng nhập thất bại):** Lưu địa chỉ web + gửi email lỗi |
| **3** | Cục Thuế - Bộ Tài Chính | Chỉ tìm khi KH là **KHDN**:<br>• 3.1: Chọn tab "Thông tin về người nộp thuế"<br>• 3.2: Nhập mã số thuế (từ `Ma_So_Doanh_Nghiep`)<br>• 3.3: Đọc & nhập mã xác nhận (captcha)<br>• 3.4: Tra cứu<br>• 3.5: Không có kết quả → bỏ qua; có kết quả → print `Tra cứu tình trạng người nộp thuế.pdf` |
| **4** | AMLD Online Portal | Đăng nhập: Username = USER_ID_NGUOI_LAP_BAO_CAO, Password = PASSWORD_NGUOI_LAP_BAO_CAO. Treo màn hình → reload tối đa 3 lần → gửi email lỗi |
| **5** | AMLD Portal | Click tab "Nhập STR" → "Mẫu số 01". Thứ tự ưu tiên: Phần I → II → IV → V → VI. **Không điền Phần III**. Thiếu thông tin → gửi email FAIL |
| **6** | AMLD Portal | **Phần I - ĐTBC:** Nhập thông tin đối tượng báo cáo, Lưu phần I, OK popup |
| **7** | AMLD Portal | **Phần II - CN/TC thực hiện GD:** KHCN → upload file cá nhân, tick "Trùng"; KHDN → upload file tổ chức, chọn người đại diện có GTTT ngày cấp mới nhất |
| **8** | AMLD Portal | **Phần IV - Thông tin GD đáng ngờ:** Tick loại báo cáo, dấu hiệu, nhập mô tả, cơ sở nghi ngờ, loại tội phạm. Lưu phần IV |
| **9** | AMLD Portal | **Phần V - Công việc xử lý:** Tick công việc, Lưu phần V |
| **10** | AMLD Portal | **Phần VI - Tài liệu đính kèm:** Upload theo thứ tự: Bảng kê → Minh họa dòng tiền → Hồ sơ ECM → Tài liệu khác |

### 5.4. RPA gửi email thông báo trạng thái (3.1.3.4)

Mẫu mail khi RPA đã nhập đủ thông tin báo cáo của 1 lô:

| Mục | Nội dung chi tiết | Nguồn |
|-----|-------------------|-------|
| **From** | `rpa_it@mbbank.com.vn` | — |
| **To** | Email người lập báo cáo | `EMAIL_NGUOI_LAP_BAO_CAO` |
| **Cc** | `qtrrhd@mbbank.com.vn`, `tamdp.ho@mbbank.com.vn`, `hanhnt1.ho@mbbank.com.vn` | — |
| **Bcc** | Không | — |
| **Đính kèm** | File excel: STT, STR_CIF, Trạng thái (Thành công/Lỗi), Mã lỗi, Chi tiết lỗi | — |
| **Tiêu đề** | "Thông báo trạng thái báo cáo GD đáng ngờ lô ngày <...>" | — |
| **Nội dung** | "Kính gửi Anh/Chị, RPA đã hoàn thành nhập liệu báo cáo lô ngày <...>. Trạng thái: Hoàn thành. Chi tiết theo file đính kèm. Trân trọng." | — |

---

## 6. Nhập liệu portal (chi tiết từng Phần)

### 6.1. Phần I — ĐTBC

| Trường | M/O | Editable | Định dạng | Mapping/Giá trị |
|--------|-----|----------|-----------|-----------------|
| Mã báo cáo nội bộ | M | Y | Textbox | STR_MA_BAO_CAO |
| Ngày báo cáo | M | N | Textbox | Hệ thống tự sinh |
| Số báo cáo | M | N | Textbox | Hệ thống tự sinh |
| Báo cáo bổ sung/thay thế | M | Y | Drop-down | Mặc định "Không" |
| **a. Tên đối tượng báo cáo** | M | N | Textbox | Mặc định "Ngân hàng TMCP Quân Đội" |
| **b. Mã đối tượng báo cáo** | M | N | Textbox | Mặc định "01311001" |
| **c. Địa chỉ (số nhà/đường phố)** | M | N | Textbox | Giá trị mặc định |
| Điện thoại | M | N | Textbox | Mặc định "904836646" |
| **d. Địa điểm phát sinh** | M | — | — | — |
| - Tên địa điểm | M | Y | Textbox | TEN_CHI_NHANH |
| - Địa chỉ | M | Y | Textbox | SO_NHA_DUONG_PHO_CHI_NHANH |
| - Phường/Xã | M | Y | Textbox | PHUONG/XA_CHI_NHANH |
| - Tỉnh/TP | M | Y | Textbox | TINH/THANH_PHO_CHI_NHANH |
| - Điện thoại | M | Y | Textbox | SDT_CHI_NHANH |
| **e. Địa chỉ email đơn vị** | M | Y | Textbox | Mặc định `qtrrhd@mbbank.com.vn` |
| **Người chịu trách nhiệm PCRT** | M | Y | Textbox | Mặc định: Phạm Thị Trung Hà, 024.6266.1088, Phó Tổng giám đốc |
| **Người lập báo cáo** | M | Y | Textbox | TEN_NGUOI_LAP_BAO_CAO, SDT_LAM_VIEC, SDT_DD; Bộ phận mặc định "Phòng QTRRHĐ & PCRT - Khối QTRR" |

### 6.2. Phần II — CN/TC thực hiện giao dịch

**Pre-condition:** Kiểm tra loại KH từ file KDL trả về.

**TH1 — KHCN** (file `ca_nhan_thuc_hien_giao_dich.xlsx`):
- B7.1: Upload file excel cá nhân thực hiện GD
- B7.2: Scroll xuống mục 3.2 "Danh sách chủ sở hữu hưởng lợi", tick checkbox "Trùng với cá nhân thực hiện"
- B7.3: Lưu phần II → B7.4 OK popup → B7.5 sang Phần IV

**TH2 — KHDN** (file `to_chuc_thuc_hien_giao_dich.xlsx`):
- B7.1: Upload file excel tổ chức thực hiện GD
- B7.2: Scroll xuống mục 3.3 "Danh sách chủ sở hữu hưởng lợi"
- B7.3: Chọn drop-list "Trùng với cá nhân..." = Tên người đại diện + Số GTTT ngày cấp mới nhất
  - Cách 1 (upload excel fail): check sheet `NDD_Thong_Tin_Dinh_Danh` → chọn So_Dinh_Danh có Ngay_Cap mới nhất
  - Cách 2 (upload thành công): click "Xem" người đại diện → chọn GTTT ngày cấp mới nhất
- B7.4: Lưu phần II → B7.5 OK popup → B7.6 sang Phần IV

### 6.3. Phần IV — Thông tin GD đáng ngờ

| Mục | Mapping | Logic/Giá trị |
|-----|---------|---------------|
| **1.1 Loại báo cáo GD đáng ngờ** | PHAN_IV_LOẠI_BAO_CAO_DANG_NGO | Checkbox A/B/C/D (hiện chỉ giá trị **B**) |
| **1.2 Dấu hiệu đáng ngờ** | PHAN_IV_DAU_HIEU_DANG_NGO | Checkbox 1–23 (theo Điều 27/28 Luật PCRT) |
| **2.1 Trạng thái GD** | — | Mặc định "Giao dịch đã được thực hiện" |
| **2.2a Thời gian GD** | NGAY_BAT_DAU / NGAY_KET_THUC | min/max ngày GD |
| **2.2b Tổng số tiền nguyên tệ** | LOAITIEN, SOTIEN_GD | sum(SOTIEN_GD) group theo LOAITIEN |
| **2.2c Tổng số tiền VNĐ** | — | Hệ thống tự tính từ bảng dòng tiền |
| **2.2d Mô tả bảng dòng tiền** | `thong_tin_giao_dich_dang_ngo.xlsx` | Upload template |
| **3. Mô tả lý do báo cáo** | PHAN_IV_3_PHAN_TICH_LY_DO_BAO_CAO | Textbox |
| **4. Cơ sở hợp lý để nghi ngờ** | PHAN_IV_CO_SO_HOP_LY_DE_NGHI_NGO | Textbox |
| **5. Loại tội phạm** | PHAN_IV_NHAN_DINH_LOAI_TOI_PHAM | Checkbox 1–30 (nếu chọn 30 → "Chưa xác định") |
| **5. Ngày phát hiện GD đáng ngờ** | — | Lấy theo ngày nhập liệu hệ thống |

> Nếu các mục tick chọn có giá trị không nằm trong định nghĩa → **dừng luồng và email thông báo lỗi**.

### 6.4. Phần V — Công việc xử lý

| Mục | Mapping | Logic |
|-----|---------|-------|
| Liệt kê công việc đã thực hiện | PHAN_V_CONG_VIEC_XU_LY | Checkbox 1–9. Nếu data chứa ít nhất 1 giá trị 6/7/8 → mặc định tick thêm **4 và 5** |

Các giá trị: 1. Từ chối thực hiện · 2. Tạm khóa tài khoản · 3. Chấm dứt giao dịch · 4. Giám sát sau giao dịch · 5. Đưa vào hệ thống cảnh báo · 6. Đã có công văn gửi CQNN · 7. Nhận công văn CQNN · 8. Công việc khác · 9. Tạm ngừng DV NH điện tử

### 6.5. Phần VI — Tài liệu đính kèm

**Thứ tự upload ưu tiên:**

| Loại tài liệu | Số trang | Nguồn file | Bắt buộc | Lưu ý |
|---------------|----------|------------|----------|-------|
| **Bảng kê** | 1 | `bang_ke_giao_dich_tai_khoan_dang_ngo.xlsx` | ✅ x | — |
| **Minh họa dòng tiền** | 1 | `Minh Họa Dòng Tiền.pdf` (bước 1) | ✅ x | — |
| **Hồ sơ mở tài khoản** | Đếm đúng số trang | file dạng `HSMTK%` | ✅ x | Nhiều file → làm lần lượt |
| **Hồ sơ khách hàng** | Đếm đúng số trang | `Giay phep thanh lap%` / `GTTT%` / `Cap nhat thong tin%` / `Thong tin KH%` | — | Nhiều file → làm lần lượt |
| **Tài liệu khác** | Đếm đúng số trang | `Tra cứu Accuity%`, `Tra cứu tình trạng người nộp thuế.pdf` | — | Nhiều file → làm lần lượt |

> Thiếu 3 file: Bảng kê / Minh họa dòng tiền.pdf / Hồ sơ mở tài khoản → gửi mail trạng thái **FAIL**.

---

## 7. Yêu cầu phi chức năng

| Mục | Yêu cầu | Ghi chú |
|-----|---------|---------|
| **4.1 An ninh/bảo mật & phân quyền** | Không phát sinh thêm | Tham chiếu tài liệu thiết kế gốc |
| **4.2 Mã hóa dữ liệu** | Không phát sinh thêm | Tham chiếu tài liệu thiết kế gốc |
| **4.3 Quản lý vận hành & lưu vết (logs)** | Không có | — |
| **4.4 Khả năng chịu tải** | Chưa điền chi tiết | Cần ước lượng: tăng trưởng KH, truy cập đồng thời, volume giao dịch |
| **4.5 Chính sách lưu trữ dữ liệu** | Không có | — |
| **4.6 Yêu cầu khác** | Không có | — |

---

## 8. Tiêu chí nghiệm thu

> *Ghi chú: Tài liệu US2 v1.3 hiện **chưa điền tiêu chí nghiệm thu cụ thể** — mục V còn để template mẫu (Given-When-Then). Dưới đây là gợi ý để đội tham khảo/hoàn thiện.*

| STT | Scenario (kịch bản) | Given (trạng thái) | When (điều kiện) | Then (kết quả mong muốn) |
|-----|---------------------|--------------------|--------------------|---------------------------|
| 1 | Robot nhập báo cáo thành công | Folder CIF có đủ 5 file + HSMTK + LOG_DONE | Robot chạy luồng xử lý | Báo cáo nhập đầy đủ Phần I–VI, gửi email trạng thái "Hoàn thành" |
| 2 | Robot xử lý khi thiếu file | Folder CIF thiếu 1 file bắt buộc | Robot kiểm tra đủ file | Ghi nhận tên file thiếu, gửi email cảnh báo, dừng KH |
| 3 | Robot xử lý khi chưa đủ log | Chưa đủ 2 file LOG_DONE | Robot kiểm tra log | Kết thúc luồng, không xử lý |
| 4 | Robot xử lý lỗi đăng nhập Accuity | User/password sai hoặc treo màn hình | Robot đăng nhập Accuity | Gửi email lỗi, chuyển bước 15 |
| 5 | Robot retry khi nhập báo cáo lỗi | Robot lỗi khi nhập | Robot thử lại | Thử tối đa 3 lần |
| 6 | Robot vẫn lỗi sau retry | Lỗi kéo dài sau 3 lần | Robot dừng | Chuyển sang robot dự phòng |
| 7 | Gửi email trạng thái lô | RPA hoàn thành 1 lô | Gửi mail | To = người lập, Cc = qtrrhd/tamdp/hanhnt, đính kèm file trạng thái |

---

## 9. Lưu ý (nếu có)

### 9.1. Rủi ro & Giả định

| Loại | Nội dung |
|------|----------|
| ⚠️ **Rủi ro** | Portal NHNN thay đổi giao diện → robot phải cập nhật selector |
| ⚠️ **Rủi ro** | Web Accuity/Cục Thuế timeout, captcha → cần retry & fallback |
| ⚠️ **Rủi ro** | Jira FCRM-6209 đang **Cancelled** → cần xác nhận lại phạm vi với nghiệp vụ |
| ✅ **Giả định** | Các file nguồn đã đủ & đúng định dạng khi robot chạy |
| ✅ **Giả định** | Quyền truy cập network & credentials được cấp trước |

### 9.2. Quy cách đặt tên file trên thư mục share (mục 6.1)

| File | Tên trên thư mục share |
|------|------------------------|
| Cá nhân | `STR_CN_GD_<Ngày xuất file>_CUS.T24.<Code KH>.xlsx` |
| Tổ chức | `STR_TC_GD_<Ngày xuất file>_CUS.T24.<Code KH>.xlsx` |
| Bảng kê | `STR_<Ngày xuất file>_CUS.T24.<Code KH>.xlsx` |
| Thông tin GD | `STR_INFO_FRAUD_<Ngày xuất file>_CUS.T24.<Code KH>.xlsx` |
| Đầu vào | `STR_INPUT_<Ngày xuất file>_CUS.T24.<Code KH>.xlsx` |

### 9.3. Cơ chế retry & chuyển robot
- Mỗi bước nhập báo cáo: retry tối đa **3 lần**.
- Vẫn lỗi sau 3 lần → **đẩy sang robot khác** tiếp tục công việc.
- Treo màn hình đăng nhập → reload & đăng nhập lại tối đa 3 lần, quá 3 lần → gửi email lỗi.

### 9.4. Lịch sử cập nhật tài liệu

| Ngày | Phiên bản | Thay đổi | Người sửa |
|------|-----------|----------|-----------|
| — | v1.0 | Tạo mới | ducpm2 |
| — | v1.1 | Update nội dung | lanltp |
| 21/09/2026 | v1.2 | Update template Bảng kê; chuyển file đính kèm xuống phụ lục | toanhv |
| 05/10/2026 | v1.3 | Bổ sung mô tả tên file trên thư mục share của KDL xuất | toanhv |

---

*Nguồn: Tài liệu US2 v1.3 (05/10/2026) — Xây dựng robot tự động nhập liệu báo cáo giao dịch đáng ngờ (STR) trên web portal của NHNN.*