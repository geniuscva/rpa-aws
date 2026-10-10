# Performance Requirements — U2 DataEntryAccuity

## Sources
- requirements.md (NFR2).

## Yêu cầu

- **PERF-U2-1:** U2 không có ngưỡng hiệu năng cứng riêng; thời gian tra cứu
  Accuity cho một CIF nằm trong tổng ngân sách ≤ 15 phút/báo cáo (NFR2) của cả
  pipeline.
- **PERF-U2-2:** Thao tác đăng nhập + tra cứu + export PDF trên web Accuity mock
  nên hoàn tất trong vài giây đến dưới một phút ở điều kiện bình thường (ước
  lượng, không phải SLA cứng).
- **PERF-U2-3:** Mỗi thao tác chờ phần tử web có timeout hợp lý để không treo
  pipeline (xem reliability).
