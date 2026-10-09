# Kết quả build và kiểm thử

## Build

- `python -m ruff check .` → `All checks passed!` (thành công).

## Kiểm thử đơn vị / tích hợp

Lệnh duy nhất (lấy từ `construction/code-generation/unit-test-instructions.md`, chạy một lần):

```
python -m pytest tests -q
```

| Tổng | Pass | Fail | Bỏ qua | Thời gian |
|---|---|---|---|---|
| 24 | 24 | 0 | 0 | 4,59 giây |

- 1 cảnh báo `StarletteDeprecationWarning` (dùng `httpx` với `starlette.testclient`); không ảnh hưởng kết quả.
- 23 test do Code Generation tạo + 1 test hiệu năng `tests/test_performance.py` do Build and Test thêm để kiểm chứng NFR1.
- Lần chạy đầu của test hiệu năng mất 165 giây vì nạp dữ liệu từng dòng; đã sửa sang chèn hàng loạt trong một transaction (không đổi ngưỡng 2 giây), sau đó cả bộ test chạy trong 4,59 giây.

## Độ phủ

Phạm vi `express` không có ngưỡng độ phủ dòng; không đo độ phủ.

## Ma trận xác minh mục tiêu

Xem `## Target Verification Matrix` trong `build-and-test-summary.md`.

## Loop-Back Log

Không có loop-back.
