# Risk & Sequencing Rationale

## Vì sao thứ tự này

Thứ tự Bolt bám đúng DAG phụ thuộc tuyến tính U1 → U2 → U3 → U4 → U5 (từ Units
Generation). Vì pipeline phụ thuộc tuyến tính (mỗi cấu phần cần `StrRecord` từ cấu
phần trước), không có nhiều đường đi kinh tế khác — thứ tự gần như bị ép bởi
topology. Đây là lập luận **dependency-first**: tôn trọng ràng buộc kỹ thuật
trước, không thể đảo thứ tự mà vẫn so khớp dữ liệu.

Không dùng mô hình chấm điểm hình thức (như WSJF) vì chuỗi tuyến tính không để
lại tự do sắp xếp đáng kể.

## Rủi ro & cách xử lý

| Rủi ro | Mức | Ở Bolt | Cách xử lý |
|---|---|---|---|
| Selector web thật đổi (AMLD) | Cao | Bolt 4 | Trừu tượng hóa qua AmldPortalAdapter; test với mock; dễ cập nhật selector |
| Captcha Cục Thuế giải sai (ddddocr) | Cao | Bolt 3 | CaptchaSolver tách riêng; định ngưỡng số lần thử; fallback bỏ qua khi fail |
| Treo màn hình đăng nhập AMLD | Trung bình | Bolt 4 | Reload & thử lại ≤ 3 lần rồi email lỗi |
| ECM mock đổi shape response | Thấp | Bolt 1 | Hợp đồng ECM pin theo tài liệu; mock ổn định |
| Ghi đè cột StrRecord sai | Thấp | Mọi Bolt | Quy ước ai-ghi-cột-nào + control field processingStopped |

Rủi ro cao nhất tập trung ở tương tác web thật (U3 captcha, U4 portal). Vì không
đảo được thứ tự, chiến lược giảm rủi ro là **trừu tượng hóa qua adapter + test
bằng mock** trước khi chạm hệ thống thật, và dồn chú ý/test cho Bolt 3, Bolt 4.

## Phát triển song song

Runtime tuần tự, nhưng nhờ hợp đồng `StrRecord` + interface `process()`, các cấu
phần có thể được phát triển và test song song bằng `StrRecord` giả làm input, rồi
ghép (so khớp) ở bước tích hợp dựa trên cùng schema.

## Heuristic tham chiếu

Dependency-first (topological) sequencing — thứ tự theo DAG của Units Generation,
không phải mô hình giá trị/kích thước, vì chuỗi tuyến tính không có nhiều lựa chọn
sắp xếp.
