# Logical Components — U4 DataEntryAMLD (NFR Design)

| Thành phần | Trách nhiệm | NFR |
|---|---|---|
| AmldPortalAdapter | Interface tới AMLD Portal thật (login, nhập các Phần, upload) — mock trong test | NFR6 |
| AmldLoginStep | Đăng nhập; treo màn hình → reload ≤3 | REL-U4-2 |
| SectionFiller (I/II/IV/V/VI) | Nhập từng Phần; bỏ Phần III; rẽ nhánh KHCN/KHDN ở Phần II; quy tắc Phần V (6/7/8→+4,5) | — |
| TickValidator | Chặn giá trị tick ngoài tập Phần IV/V | REL-U4-3 |
| AttachmentUploader | Upload Phần VI đúng thứ tự; thiếu bắt buộc → FAIL | REL-U4-4 |
| RetryPolicy (dùng chung) | Bọc retry ≤3 cho các bước nhập | REL-U4-1 |
| AmldStage | process(record,context): ghi BOT_ALMD/BOT_TINHTRANGTRASOAT | REL-U4-5 |

Adapter ẩn AMLD; test mock. Credentials từ config.yaml. U4 hội tụ U2+U3.
