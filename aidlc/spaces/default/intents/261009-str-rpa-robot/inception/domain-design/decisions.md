# Architecture Decision Records — Domain Design

## ADR-001: Phân rã theo chức năng nghiệp vụ (~11 component)

- **Context:** Robot STR có luồng nghiệp vụ nhiều bước, nhiều hệ thống ngoài,
  nhiều nhánh xử lý lỗi, và cần mock từng hệ thống ngoài trong test (NFR6, TDD).
- **Decision:** Phân rã thành các component theo chức năng: Orchestrator,
  KafkaConsumer, SourceDataReader, EcmClient, CashFlowDiagramBuilder,
  AccuityLookup, TaxAuthorityLookup, CaptchaSolver, AmldPortalFiller,
  RetryManager, ErrorAggregator, EmailNotifier.
- **Consequences:** (+) Mỗi khối test độc lập, dễ mock hệ thống ngoài, nhịp thay
  đổi tách biệt (portal đổi giao diện chỉ chạm AmldPortalFiller). (−) Nhiều
  component hơn nên cần Orchestrator điều phối rõ ràng.
- **Alternatives Rejected:** Gộp thô (DataIngestion/ExternalLookups/
  PortalAutomation/Notification) — giảm khả năng test độc lập và mock từng hệ
  thống. Tách mịn từng Phần Mẫu số 01 — phân mảnh không cần thiết vì các Phần dùng
  chung session trình duyệt.

## ADR-002: Lớp adapter cho mỗi hệ thống ngoài

- **Context:** NFR6 yêu cầu test tự động với mock; Accuity luôn mock, AMLD/Cục
  Thuế mock khi test và thật khi production.
- **Decision:** Mỗi hệ thống ngoài ẩn sau một adapter/interface riêng
  (AccuityAdapter, TaxAuthorityAdapter, AmldPortalAdapter, EcmClient). Code
  nghiệp vụ phụ thuộc interface, không phụ thuộc hiện thực cụ thể.
- **Consequences:** (+) Thay mock/real bằng cấu hình, test không chạm hệ thống
  thật. (−) Thêm một lớp trừu tượng.
- **Alternatives Rejected:** Gọi trực tiếp web/API — không thể mock sạch, test
  phụ thuộc hệ thống ngoài.

## ADR-003: Xử lý tuần tự từng khách hàng trong lô

- **Context:** Tương tác portal AMLD dựa trên session trình duyệt; cần truy vết rõ
  theo từng KH; cô lập lỗi theo KH.
- **Decision:** Orchestrator xử lý tuần tự từng CustomerCase trong một BatchJob.
- **Consequences:** (+) Đơn giản, dễ truy vết, tránh tranh chấp session portal.
  (−) Thông lượng thấp hơn song song; chấp nhận được với yêu cầu ≤ 15 phút/báo cáo
  và chạy local.
- **Alternatives Rejected:** Xử lý song song nhiều KH — phức tạp quản lý session
  portal và tài nguyên, rủi ro tranh chấp; chưa cần ở phạm vi này.

## ADR-004: Captcha tách thành component riêng (CaptchaSolver, ddddocr)

- **Context:** Tra cứu Cục Thuế cần giải captcha; ddddocr là lựa chọn đã chốt;
  giải captcha dễ fail và có thể cần thử lại/đổi cách.
- **Decision:** Tách CaptchaSolver dùng ddddocr, chỉ phục vụ TaxAuthorityLookup.
- **Consequences:** (+) Dễ thay đổi/thử nghiệm độc lập, test riêng. (−) Thêm một
  phụ thuộc nội bộ.
- **Alternatives Rejected:** Nhúng giải captcha thẳng trong TaxAuthorityLookup —
  khó test và khó thay thế.

## ADR-005: RetryManager là policy cross-cutting

- **Context:** Nhiều bước (nhập Phần, tương tác web) cần retry ≤ 3 lần rồi báo
  thất bại.
- **Decision:** Tách RetryManager làm policy dùng chung, bọc quanh thao tác dễ
  lỗi.
- **Consequences:** (+) Chính sách retry nhất quán, một chỗ sửa. (−) Các component
  gọi phải qua lớp bọc.
- **Alternatives Rejected:** Nhúng retry lặp lại trong từng component — trùng lặp,
  khó đảm bảo nhất quán ngưỡng 3 lần.
