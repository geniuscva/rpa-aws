# Practices Discovery — Questions

Interaction mode: Guide me (walk through interactively).

---

## Q1 — Cách làm việc (Way of Working / branching)

Đội muốn quản lý nhánh và merge thế nào?

- A. Trunk-based: nhánh feature ngắn (1-2 ngày), merge vào `main`, squash-merge mỗi đơn vị công việc (gợi ý mặc định)
- B. GitHub Flow: nhánh feature sống lâu hơn, merge qua PR review
- C. Gitflow: develop + release branches
- X. Other (please specify)

[Answer]: C

---

## Q2 — Walking skeleton (lát cắt đầu-cuối mỏng trước)

Có xây một lát cắt chạy xuyên suốt (đọc 1 folder KH → tra cứu → tới bước nhập portal) trước, để chứng minh các mảnh ghép kết nối được, rồi mới làm đầy đủ Phần I-VI và cơ chế retry/failover không? (Walking skeleton = phiên bản tối thiểu chạy hết từ đầu đến cuối, dựng trước để chứng minh các thành phần nối được với nhau.)

- A. Có — xây lát cắt mỏng end-to-end trước (gợi ý mặc định cho dự án mới)
- B. Không — làm thẳng theo từng phần
- X. Other (please specify)

[Answer]:A

---

## Q3 — Cách kiểm thử (Testing Posture)

Viết test theo kiểu nào?

- A. Test-after: làm xong từng lớp rồi viết & chạy test cho lớp đó; sàn coverage 80%, chạy CI trước khi merge (gợi ý mặc định)
- B. TDD: viết test trước, code sau
- C. BDD: kịch bản nghiệp vụ dẫn dắt test
- D. Tối thiểu: mỗi yêu cầu 1 test, không ép sàn coverage
- X. Other (please specify)

[Answer]:B

---

## Q4 — Triển khai (Deployment)

Robot được đưa lên môi trường chạy thế nào?

- A. Deploy khi merge lên môi trường robot-dev/staging; lên production cần phê duyệt thủ công riêng (QTRRHĐ & PCRT + RPA Ops) (gợi ý mặc định)
- B. Deploy thủ công hoàn toàn ở mọi môi trường
- C. Continuous deployment tự động lên production
- X. Other (please specify)

[Answer]:X : chạy trên máy này luôn

---

## Q5 — Quy ước code (Code Style)

Chuẩn code và lint theo cách nào?

- A. Theo chuẩn ngôn ngữ: formatter + linter chạy CI trước merge, lint fail chặn merge; secrets không hardcode (gợi ý mặc định)
- B. Có bộ quy ước riêng của đội (mô tả thêm)
- X. Other (please specify)

[Answer]:A
