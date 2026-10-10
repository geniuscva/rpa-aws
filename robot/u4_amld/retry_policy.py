"""RetryPolicy: bọc một bước nhập/tương tác dễ lỗi, thử lại ≤ max_attempts lần
rồi báo thất bại (BR4.8, NFR3).

Khi vẫn lỗi sau max_attempts lần, raise RetryExhausted để stage dừng record và
(ở project local này) email báo thất bại thay cho robot thứ hai.
"""
from __future__ import annotations

from typing import Callable, Optional, TypeVar

T = TypeVar("T")

DEFAULT_MAX_ATTEMPTS = 3


class RetryExhausted(Exception):
    """Vẫn lỗi sau khi đã thử tối đa số lần cho phép."""


class RetryPolicy:
    """Thử lại một thao tác tối đa max_attempts lần (mặc định 3)."""

    def __init__(self, max_attempts: int = DEFAULT_MAX_ATTEMPTS) -> None:
        self.max_attempts = max(1, int(max_attempts))

    def run(self, step: Callable[[], T], description: str = "") -> T:
        """Chạy `step`; nếu raise thì thử lại tới max_attempts lần.

        Trả kết quả của lần thành công đầu tiên; raise RetryExhausted nếu hết lượt.
        """
        last_error: Optional[Exception] = None
        for _ in range(self.max_attempts):
            try:
                return step()
            except Exception as exc:  # noqa: BLE001 - gom mọi lỗi bước để thử lại
                last_error = exc
        raise RetryExhausted(
            f"Thất bại sau {self.max_attempts} lần{': ' + description if description else ''}"
        ) from last_error
