# Performance Requirements — U1 ConsumeData

## Sources
- requirements.md (NFR2).

## Yêu cầu

- **PERF-U1-1:** U1 không có ngưỡng hiệu năng cứng riêng; thời gian xử lý một CIF
  ở U1 nằm trong tổng ngân sách ≤ 15 phút/báo cáo (NFR2) của cả pipeline.
- **PERF-U1-2:** Đọc 5 file excel và gọi ECM cho một CIF nên hoàn tất trong vài
  giây đến dưới một phút ở điều kiện bình thường (ước lượng, không phải SLA cứng).
- **PERF-U1-3:** Gọi ECM có timeout hợp lý để không treo pipeline (xem reliability).
