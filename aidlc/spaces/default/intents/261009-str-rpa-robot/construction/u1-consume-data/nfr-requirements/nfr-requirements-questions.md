# NFR Requirements — U1 ConsumeData — Questions

Interaction mode: Guide me.

Đã chốt Python + Playwright/Selenium ở requirements. Cần chốt tech stack cụ thể
cho U1 (và dùng chung cả robot) + vài ngưỡng NFR.

---

## Q1 — Thư viện/công cụ cho U1 (và chung cả robot)

- A. Python 3.11+, kafka-python (consumer), openpyxl/pandas (đọc excel), requests/httpx
  (gọi ECM), reportlab (xuất PDF dòng tiền), pytest (test). Playwright dùng cho các
  Unit web (U2–U4). (gợi ý)
- B. Bộ khác (mô tả)
- X. Other (please specify)

[Answer]: X các thư viện cần dùng tạ requirements.txt

---

## Q2 — Hiệu năng U1

- A. Không ngưỡng cứng riêng cho U1; nằm trong tổng ≤ 15 phút/báo cáo (NFR2) (gợi ý)
- X. Other (please specify)

[Answer]:A

---

## Q3 — Quan sát/log (observability)

- A. Log có cấu trúc theo từng CIF/bước, mức INFO cho tiến trình và ERROR cho lỗi;
  đủ dựng file trạng thái (NFR5) (gợi ý)
- X. Other (please specify)

[Answer]: X - log có dạng: Thời gian/Log Level/	Message và lưu trong file .json

---

## Q4 — Độ tin cậy U1 (reliability)

- A. Lỗi cô lập theo CIF (một CIF lỗi không làm sập consumer); ECM gọi có timeout
  + retry nhẹ; chống trùng theo eventID (gợi ý)
- X. Other (please specify)

[Answer]:A

---

## Q5 — Bảo mật U1 (security)

- A. Credentials ECM đọc từ biến môi trường/secrets manager; không log giá trị
  secret; chỉ đọc thư mục nguồn được cấp (gợi ý)
- X. Other (please specify)

[Answer]:X - user/pass và các cấu hình cần thiết ở 1 file data/config.yaml . không cần load ở biến môi trường
