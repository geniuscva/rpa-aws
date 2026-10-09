# Tóm tắt Build and Test

## Trạng thái build

Build thành công (`ruff` sạch) và 24/24 test pass. Phụ thuộc cài bằng `requirements.txt`. Chi tiết: `build-instructions.md`, `test-results.md`.

## Danh mục loại kiểm thử

Chiến lược Minimal: kiểm thử đơn vị/API/giao diện tĩnh đã nằm trong Code Generation (23 test). Build and Test bổ sung 1 test hiệu năng cho NFR1. Ba file hướng dẫn `integration-test-instructions.md`, `performance-test-instructions.md`, `security-test-instructions.md` được tạo ngắn gọn để hoàn tất danh sách sản phẩm của giai đoạn.

## Độ phủ kỳ vọng

Không đặt ngưỡng độ phủ dòng cho phạm vi `express`; mọi FR1-FR5, NFR1-NFR5 đều có ít nhất một test hoặc cơ chế kiểm chứng.

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| NFR1-list | requirements.md NFR1 | Danh sách robot tải < 2 giây với 50 robot và 10.000 bản ghi | Dưới 2 giây (toàn bộ test gồm nạp dữ liệu chạy 0,38 giây) | `tests/test_performance.py` pass | build-and-test | Met |
| NFR1-history | requirements.md NFR1 | Lịch sử chạy (phân trang) tải < 2 giây với 10.000 bản ghi | Dưới 2 giây | `tests/test_performance.py` pass | build-and-test | Met |
| FR2.2-refresh | requirements.md FR2.2 | Giao diện tự cập nhật trạng thái tối đa 5 giây | Chu kỳ làm mới 3 giây | `tests/test_ui.py` pass | build-and-test | Met |
| NFR2-bind | requirements.md NFR2 | Mặc định chỉ lắng nghe `127.0.0.1` | `127.0.0.1` | `tests/test_api.py` pass (kiểm tra cấu hình mặc định) | build-and-test | Met |

## Đánh giá sẵn sàng

- Build-ready: có.
- Test-ready: có.
- Deployment-ready: dùng cục bộ trên máy Windows; không có triển khai lên môi trường chia sẻ.

## Giới hạn và việc còn lại

- Giao diện (JavaScript) chưa được mở thử bằng trình duyệt thật; mới kiểm tra qua HTML tĩnh và API. Nên mở `http://127.0.0.1:8000` một lần để xác nhận bằng mắt.
- Chưa chạy thử với `run.bat` thật của folder `RPA_NHAPBAOCAO_STR`; test dùng robot giả `python -c`.
- Ứng dụng không có đăng nhập (đã chấp nhận trong requirements); phải giữ bind `127.0.0.1`.
- Output của `run.bat` theo codepage OEM có thể hiển thị sai dấu tiếng Việt trong log.
