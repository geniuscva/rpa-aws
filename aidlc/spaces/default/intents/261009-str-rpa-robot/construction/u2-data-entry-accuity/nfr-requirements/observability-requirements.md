# Observability Requirements — U2 DataEntryAccuity

## Sources
- requirements.md (NFR5), quyết định logging của người dùng.

## Yêu cầu

- **OBS-U2-1:** Dùng chung logger JSON của robot. Mỗi bản ghi log gồm: **Thời
  gian (timestamp)**, **Log Level**, **Message** (append JSON lines).
- **OBS-U2-2:** Ghi log ở các mốc chính của U2 theo từng CIF: bắt đầu tra cứu
  Accuity, loại entity type, kết quả export PDF, Match Score, và kết quả (thành
  công/lỗi + mã lỗi).
- **OBS-U2-3:** Log đủ chi tiết để U5 dựng file trạng thái lô (CIF, trạng thái,
  mã lỗi, chi tiết lỗi khi tra cứu Accuity thất bại).
- **OBS-U2-4:** Không log giá trị secret (password Accuity).
