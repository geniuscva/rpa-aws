# Logical Components — U5 TongHopVaGuiMail (NFR Design)

| Thành phần | Trách nhiệm | NFR |
|---|---|---|
| ErrorAggregator | Thu thập StrRecord mọi CIF, dựng ProcessingResult theo KH | REL-U5-1 |
| StatusReportBuilder | Dựng file excel trạng thái (STT/STR_CIF/Trạng thái/Mã lỗi/Chi tiết lỗi) | REL-U5-3 |
| EmailSender | Gửi email qua SMTP mail exchange, có xử lý lỗi | REL-U5-2 |
| TongHopStage | process cả lô: tổng hợp + gửi một email | — |
| StructuredLogger (dùng chung) | Log JSON | OBS-U5-1 |

SMTP/cấu hình từ config.yaml, không hardcode.
