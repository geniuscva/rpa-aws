# External Dependency Map

Các phụ thuộc ngoài (hệ thống/dịch vụ không do bản build này tạo) và Bolt tiêu
thụ chúng. Dự án chạy local; các mock chạy sẵn trên máy theo
`docs/SERVICES_CONNECTION_INFO.md`.

| Phụ thuộc | Loại | Chủ sở hữu | Bolt tiêu thụ | Thời gian/điều kiện | Nếu trễ/thiếu |
|---|---|---|---|---|---|
| Kafka (localhost:9092, topic RPA_STR_NHNN_INPUT) | queue | Hạ tầng local | Bolt 1 (U1) | Chạy sẵn trên máy | Robot không nhận việc; cần khởi động broker |
| ECM mock (localhost:8831) | REST API (mock) | Hạ tầng local | Bolt 1 (U1) | Chạy sẵn trên máy | Không lấy được hồ sơ PDF; U1 báo lỗi |
| Accuity mock web | web (mock) | Hạ tầng local | Bolt 2 (U2) | Mock cần dựng | Không tra cứu được; cần mock web |
| Web Cục Thuế (thật) | web thật | Cục Thuế / Bộ Tài Chính | Bolt 3 (U3) | Phụ thuộc hạ tầng ngoài, captcha | Dùng mock trong test; chạy thật khi có kết nối; fail thì bỏ qua |
| AMLD Online Portal (thật) | web thật | NHNN | Bolt 4 (U4) | Credentials nghiệp vụ cấp sau | Dùng mock trong test; chạy thật khi có credentials |
| Mail exchange | mail | Hạ tầng local/tổ chức | Bolt 5 (U5) | Cần cấu hình gửi mail | Không gửi được email trạng thái; cần cấu hình SMTP/exchange |

Ghi chú:
- Trong giai đoạn này, các hệ thống thật (Cục Thuế, AMLD) được mock/stub khi
  test; chạy thật cần credentials/kết nối do nghiệp vụ cấp sau.
- Accuity luôn mock (theo yêu cầu).
- Credentials của mọi hệ thống đọc từ biến môi trường/secrets manager (không
  hardcode).
