# Scalability Design — U1 ConsumeData

- Consumer xử lý tuần tự từng message (một CIF) (SCAL-U1-1/2).
- Không xử lý song song ở phạm vi này; nếu cần mở rộng, có thể tăng số consumer
  theo partition Kafka trong tương lai (ngoài phạm vi).
