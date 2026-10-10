<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-09 — U4 (DataEntryAMLD) là điểm hội tụ U2+U3; mô hình hoá đăng nhập (AmldSession, reload <=3), tiến độ nhập Mẫu số 01 (StrReport theo thứ tự I/II/IV/V/VI, bỏ III), kiểm tra tick Phần IV/V (SectionTickValue), đính kèm Phần VI theo thứ tự (AttachmentItem), và retry <=3 (RetryPolicy). Giữ nhất quán format YAML source-of-truth + state machine như U2/U3.
- 2026-10-09 — Áp project rules affirmed: BR4.2 cấm điền Phần III; BR4.7 thiếu tài liệu bắt buộc → email FAIL; BR4.6 chặn tick ngoài tập Phần IV/V; BR4.11 credentials từ data/config.yaml, không hardcode/không log.
- 2026-10-09 — U5 (TongHopVaGuiMail) là chặng cuối, chạy một lần cho cả lô: đọc toàn bộ StrRecord, dựng ProcessingResult/BatchStatusReport (cột STT/STR_CIF/Trạng thái/Mã lỗi/Chi tiết lỗi), gửi một StatusEmail qua mail exchange. KH lỗi sau 3 retry và KH dừng luồng đều là một hàng FAIL trong email lô (cô lập lỗi BR5.5).

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
