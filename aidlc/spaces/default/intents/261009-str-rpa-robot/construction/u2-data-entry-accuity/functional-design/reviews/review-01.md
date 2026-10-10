## Review

**Reviewer:** aidlc-architecture-reviewer-agent
**Verdict:** READY
**Iteration:** 1

Thiết kế chức năng U2 DataEntryAccuity nhất quán với hợp đồng pipeline. entities.md
mô tả đúng AccuityQuery (entityType suy từ LOAIKHACHHANG, searchName từ TENKHACHHANG,
Single), AccuityLookupResult (resultPdfPath, matchScore 0..100, profilePdfPaths khi
match=100) và phần StrRecord U2 chỉ ghi BOT_ACCUITY/BOT_GHICHU — tôn trọng quy ước
sở hữu cột ở contract-summary.md. rules.md có BR2.1–BR2.7 rõ ràng, phủ: bỏ qua record
đã dừng (cô lập lỗi FR12), chọn Entity Type theo loại KH, đăng nhập + export
`Tra cứu Accuity.pdf`, in thêm hồ sơ khi Match Score=100, xử lý lỗi ghi StrRecord +
dừng, không hardcode credentials (NFR4). functional-spec.md có workflow 10 bước, state
machine StrRecord phạm vi U2, ER diagram dẫn xuất, và scenarios happy/unhappy phủ cả
KHCN/KHDN, match-100, lỗi đăng nhập, và record đã dừng. traceability.json phủ AC2.2.1
(BR2.2, BR2.3) và AC2.2.2 (BR2.4), reverse giải thích các BR hành vi/ràng buộc. Web
Accuity được trừu tượng hóa sau adapter (NFR6) để mock trong test. Các điểm dưới là
gợi ý cho Code Generation.

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Low | BR2.4 | Quy ước đặt tên `Tra cứu Accuity(n).pdf` khi nhiều bản ghi match=100 nên chốt cách đánh số n ở Code Generation. | Chốt quy ước đặt tên file ở Code Generation. | New |
| R-02 | Low | AccuityLookupResult.matchScore | Nguồn/cách đọc matchScore từ web mock (text/thuộc tính) để mức logic; làm rõ khi hiện thực adapter mock. | Làm rõ ở Code Generation/test fixtures. | New |
