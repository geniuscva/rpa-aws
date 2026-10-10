# Code Summary — U4 DataEntryAMLD

## Những gì đã xây

Cài đặt đầy đủ cấu phần U4 (DataEntryAMLD): điểm hội tụ U2+U3, nhập Mẫu số 01 lên
AMLD Online Portal (web thật) cho một CIF, cập nhật `StrRecord.BOT_ALMD` +
`BOT_TINHTRANGTRASOAT`. Dùng khung chung đã có từ U1. Code ở `robot/u4_amld/`.

### Cấu phần U4 (robot/u4_amld/)
- `retry_policy.py` — `RetryPolicy.run(step)` thử ≤ `max_attempts` (mặc định 3);
  vẫn lỗi → `RetryExhausted` để stage dừng record + failover (BR4.8/NFR3).
- `tick_validator.py` — `TickValidator`: `validate_section_iv/v` kiểm giá trị
  tick thuộc tập cho phép, ngoài tập → `TickValueError` (BR4.6, KHÔNG đi tiếp);
  Phần V nếu tập chứa 6/7/8 → tự thêm 4 và 5 (BR4.5).
- `attachment_uploader.py` — `AttachmentUploader`: `check_required` chặn nộp khi
  thiếu tài liệu bắt buộc (Bảng kê, Minh Họa Dòng Tiền.pdf, Hồ sơ mở tài khoản
  HSMTK) → `MissingAttachmentError` (BR4.7); `ordered` sắp xếp upload Phần VI
  đúng thứ tự cố định (BR4.4).
- `amld_portal_adapter.py` — `AmldPortalPort` (Protocol: login, open_form,
  fill_section, set_ticks, upload, submit), `AmldSession` (username từ record,
  password/endpoint từ config — BR4.11, không log secret), `MockAmldPortalPort`
  (test/dev, ghi dấu vết Phần đã nhập, mô phỏng treo/lỗi), `PlaywrightAmldPortalPort`
  (production). Cả mock và Playwright đều **raise khi bị gọi với Phần III** (BR4.2).
- `amld_stage.py` — `AmldStage.process(record, context) -> record`:
  - BR4.1: bỏ qua record đã dừng.
  - BR4.7: kiểm tài liệu bắt buộc TRƯỚC khi nộp — thiếu → dừng record, KHÔNG nộp.
  - BR4.9: đăng nhập, treo thì reload ≤ 3 lần; quá → dừng record.
  - BR4.2: nhập I→II→IV→V→VI, **KHÔNG điền Phần III**; Phần II rẽ nhánh KHCN/KHDN
    (BR4.3). Mỗi bước bọc `RetryPolicy` (BR4.8).
  - BR4.6/4.5: tick Phần IV/V qua `TickValidator` (ngoài tập → dừng; 6/7/8→+4,5).
  - BR4.4: upload Phần VI theo thứ tự `AttachmentUploader.ordered`.
  - BR4.10: thành công → `BOT_ALMD=OK` + `BOT_TINHTRANGTRASOAT`; lỗi/thiếu tài
    liệu/tick ngoài tập → `BOT_ALMD=ERROR` + `BOT_TINHTRANGTRASOAT=ERROR` +
    `stop()` (processing_stopped + BOT_GHICHU) để U5 gửi email FAIL.

## Test
- 23 test (pytest), tất cả PASS. Mock `AmldPortalPort`; không chạm AMLD Portal thật.
- Phủ (retry): thành công lần đầu, thành công trong giới hạn, fail quá 3 lần.
- Phủ (tick): hợp lệ qua, ngoài tập → lỗi (IV và V), Phần V 6/7/8 → +4,5 (không trùng).
- Phủ (attachment): đủ tài liệu qua, thiếu → lỗi + liệt kê thiếu, thứ tự Phần VI đúng,
  file lạ xếp cuối.
- Phủ (stage): happy KHCN & KHDN → OK và khẳng định `sections_filled == [I,II,IV,V,VI]`
  (KHÔNG có III); thiếu tài liệu → dừng, không nộp; tick ngoài tập → dừng, không đi
  tiếp (Phần V không nhập); Phần V 6/7/8 → tick có 4,5,6; bước nhập lỗi quá 3 → dừng;
  đăng nhập treo quá 3 → dừng; treo trong giới hạn → phục hồi OK; record đã dừng → bỏ qua.
- Lệnh: `.venv/bin/pytest tests/u4_amld` → `23 passed`. Toàn bộ suite:
  `.venv/bin/pytest` → `72 passed` (25 U1 + 12 U2 + 12 U3 + 23 U4).

## Lưu ý (ràng buộc project.md đã tuân thủ)
- KHÔNG điền Phần III (BR4.2) — mock/Playwright raise nếu bị gọi với "III";
  thứ tự nhập không chứa III; test khẳng định.
- KHÔNG nộp khi thiếu đính kèm bắt buộc → email FAIL ở U5 (BR4.7).
- KHÔNG đi tiếp khi giá trị tick Phần IV/V ngoài tập cho phép (BR4.6).
- Credentials/endpoint AMLD đọc từ `data/config.yaml`, không hardcode, không log
  secret (BR4.11/NFR4). Hiện thực Playwright thật gắn ở bước chạy thật; test chạy
  hoàn toàn trên mock.
