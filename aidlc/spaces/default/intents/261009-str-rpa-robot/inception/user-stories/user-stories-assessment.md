# User Stories — Assessment

## Decision

Execute.

## Rationale

Dự án có nhiều vai trò người dùng/stakeholder (người lập báo cáo QTRR, phòng
QTRRHĐ & PCRT, RPA Ops) và nghiệp vụ phức tạp (quy trình nhiều bước, nhiều hệ
thống ngoài, nhiều nhánh xử lý lỗi). User stories giúp làm rõ giá trị theo góc
nhìn người dùng và tạo tiêu chí nghiệm thu kiểm thử được — phù hợp với posture
TDD đã chốt.

## Factors considered

- Loại dự án: tự động hóa nghiệp vụ (RPA), có người dùng cuối rõ ràng.
- Phạm vi hướng người dùng: người lập báo cáo nhận email trạng thái, chịu trách
  nhiệm nghiệp vụ; Ops vận hành robot.
- Tín hiệu phức tạp: 14 nhóm FR, 3 hệ thống ngoài, cơ chế retry/thông báo lỗi,
  rẽ nhánh KHCN/KHDN.

## Key areas where stories add the most value

- Luồng xử lý thành công end-to-end theo lô/khách hàng.
- Các kịch bản lỗi và thông báo (thiếu file, lỗi tra cứu, retry, email FAIL).
- Rẽ nhánh KHCN vs KHDN.
- Nhận việc qua Kafka và lấy hồ sơ qua ECM mock.
