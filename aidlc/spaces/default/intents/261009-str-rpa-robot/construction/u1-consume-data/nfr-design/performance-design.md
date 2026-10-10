# Performance Design — U1 ConsumeData

- Xử lý một CIF tuần tự; không ngưỡng cứng riêng, nằm trong ≤ 15 phút tổng
  (PERF-U1-1).
- `CashFlowCalculator` tính trên dữ liệu bảng kê trong bộ nhớ; với khối lượng GD
  thông thường là nhanh.
- `EcmClientAdapter` có timeout để không treo pipeline (PERF-U1-3).
