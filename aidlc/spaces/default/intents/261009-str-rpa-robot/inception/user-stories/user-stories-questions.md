# User Stories — Plan & Questions

Interaction mode: Guide me.

## Kế hoạch đề xuất

- **Persona:** (1) Người lập báo cáo STR (QTRR) — nhận email trạng thái, chịu
  trách nhiệm nghiệp vụ; (2) RPA Ops — vận hành/giám sát robot, xử lý lỗi; (3)
  Trưởng phòng QTRRHĐ & PCRT — chủ quy trình, người duyệt (ưu tiên thấp hơn về
  tương tác trực tiếp).
- **Cách chia story:** theo luồng nghiệp vụ (workflow) end-to-end của robot, bám
  các nhóm FR: nhận việc (Kafka) → đọc & kiểm tra dữ liệu → lấy hồ sơ ECM → tổng
  hợp dòng tiền → tra cứu Accuity/Cục Thuế → nhập AMLD các Phần → retry/lỗi →
  email trạng thái.
- **Định dạng:** "As a ..., I want ..., so that ..." + tiêu chí nghiệm thu
  Given/When/Then; gắn ID US{nhóm}.{thứ tự}, AC ba đoạn; đánh giá INVEST.
- **Ưu tiên:** gán MoSCoW (Must/Should/Could/Won't) theo mức quan trọng; ranh
  giới MVP chốt chính thức ở Delivery Planning.

---

## Q1 — Góc nhìn chủ đạo của story

Story nên viết chủ yếu theo góc nhìn nào?

- A. Theo luồng nghiệp vụ của robot (workflow end-to-end), người lập báo cáo là
  persona hưởng lợi chính (gợi ý)
- B. Theo từng persona riêng (mỗi persona một nhóm story)
- C. Theo nhóm chức năng kỹ thuật (ingest, lookup, portal, email)
- X. Other (please specify)

[Answer]: A

---

## Q2 — Độ mịn (granularity) của story

Mức chi tiết mong muốn?

- A. Vừa phải: mỗi bước nghiệp vụ lớn là một story (khoảng 10–15 story) (gợi ý)
- B. Mịn: tách nhỏ từng thao tác (nhiều story nhỏ)
- C. Thô: gom theo giai đoạn lớn (ít story, mỗi story nhiều AC)
- X. Other (please specify)

[Answer]: A

---

## Q3 — Persona có cần thêm vai trò nào không?

Ngoài 3 persona đề xuất (Người lập báo cáo, RPA Ops, Trưởng phòng QTRRHĐ & PCRT),
có cần thêm không?

- A. Đủ 3 persona như đề xuất (gợi ý)
- B. Chỉ cần Người lập báo cáo + RPA Ops
- C. Thêm persona khác (mô tả)
- X. Other (please specify)

[Answer]: X - 3 persona: Người lập báo cáo, RPA (Ops vận hành robot), Người nhận cảnh báo khi báo cáo chạy lỗi

---

## Q4 — Kịch bản lỗi có cần tách thành story riêng?

Các kịch bản lỗi/thông báo (thiếu file, lỗi tra cứu, retry, email FAIL) nên:

- A. Tách thành story riêng cho rõ tiêu chí nghiệm thu (gợi ý, hợp với TDD)
- B. Gộp làm acceptance criteria trong story luồng chính
- X. Other (please specify)

[Answer]: A
