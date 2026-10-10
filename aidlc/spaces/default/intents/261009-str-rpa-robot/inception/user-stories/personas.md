# Personas

## P1 — Người lập báo cáo STR (QTRR) — ưu tiên cao nhất

- **Vai trò:** Cán bộ nghiệp vụ phòng QTRR, chịu trách nhiệm pháp lý về báo cáo
  STR nộp lên NHNN.
- **Mục tiêu:** Báo cáo được nhập đầy đủ, chính xác, đúng hạn lên AMLD Portal mà
  không phải nhập tay; nắm được trạng thái từng khách hàng trong lô.
- **Pain point:** Nhập thủ công tốn > 15 phút/báo cáo, dễ sai sót ở nhiều Phần;
  khó theo dõi khối lượng lớn.
- **Bối cảnh:** Nhận email trạng thái lô kèm file excel chi tiết; là người To
  trong email thông báo.

## P2 — RPA Ops (vận hành robot) — ưu tiên cao

- **Vai trò:** Kỹ sư/cán bộ vận hành robot RPA.
- **Mục tiêu:** Robot chạy ổn định, nhận việc từ Kafka, tự xử lý lỗi (retry) và
  báo khi vượt ngưỡng; dễ theo dõi log để truy vết.
- **Pain point:** Lỗi hệ thống ngoài (timeout, captcha, treo màn hình); cần biết
  nhanh khi nào robot dừng và vì sao.
- **Bối cảnh:** Theo dõi robot, log, hàng đợi Kafka; can thiệp khi cần.

## P3 — Người nhận cảnh báo khi báo cáo chạy lỗi — ưu tiên trung bình

- **Vai trò:** Người/nhóm nhận email cảnh báo khi một báo cáo/khách hàng xử lý
  lỗi (có thể trùng người lập báo cáo hoặc là đầu mối giám sát).
- **Mục tiêu:** Được thông báo kịp thời, rõ ràng khi có lỗi (thiếu file, lỗi tra
  cứu, thất bại sau 3 lần retry) để xử lý nghiệp vụ bù.
- **Pain point:** Nếu không được báo lỗi rõ ràng, báo cáo lỗi có thể bị bỏ sót,
  ảnh hưởng tuân thủ.
- **Bối cảnh:** Nhận email FAIL/cảnh báo kèm mã lỗi và chi tiết.

## Quan hệ & thứ tự ưu tiên

P1 (Người lập báo cáo) là persona hưởng lợi chính và là trung tâm của giá trị
nghiệp vụ. P2 (RPA Ops) đảm bảo robot vận hành. P3 (Người nhận cảnh báo) là
người tiêu thụ thông tin lỗi; trong nhiều trường hợp P3 trùng P1.
