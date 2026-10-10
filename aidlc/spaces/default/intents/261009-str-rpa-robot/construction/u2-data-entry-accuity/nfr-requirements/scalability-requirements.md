# Scalability Requirements — U2 DataEntryAccuity

## Sources
- requirements.md (NFR7, OQ3 — số liệu tải để trống trong tài liệu).

## Yêu cầu

- **SCAL-U2-1:** U2 xử lý tuần tự từng CIF trong lô (một phiên tra cứu Accuity
  mỗi lần). Không yêu cầu tra cứu đồng thời nhiều CIF ở phạm vi này (chạy local).
- **SCAL-U2-2:** Phiên trình duyệt Accuity có thể tái sử dụng giữa các CIF trong
  cùng lô để giảm chi phí đăng nhập lặp (tối ưu, không bắt buộc).
- **SCAL-U2-3:** Số liệu tải thực tế (số CIF/ngày) chưa có (OQ3); xử lý song song
  là tối ưu tương lai, ngoài phạm vi hiện tại.
