"""TickValidator: kiểm giá trị tick Phần IV/V thuộc tập cho phép (BR4.6) và áp
quy tắc Phần V 6/7/8 → tự tick thêm 4 và 5 (BR4.5).

Giá trị ngoài tập cho phép → raise TickValueError để stage dừng luồng KH, KHÔNG
đi tiếp (BR4.6 — hành vi an toàn bắt buộc).
"""
from __future__ import annotations

from typing import Iterable


class TickValueError(Exception):
    """Có giá trị tick nằm ngoài tập định nghĩa (Phần IV/V)."""


class TickValidator:
    """Kiểm tra và chuẩn hoá tập giá trị tick Phần IV/V.

    `allowed_section_iv` / `allowed_section_v`: tập giá trị hợp lệ (do cấu hình/
    đặc tả cung cấp). Mặc định dùng tập số thứ tự công việc 1..8 cho Phần V.
    """

    #: Phần V — quy tắc BR4.5: tập chứa bất kỳ 6/7/8 thì mặc định thêm 4 và 5.
    SECTION_V_TRIGGER = frozenset({6, 7, 8})
    SECTION_V_IMPLIED = frozenset({4, 5})

    def __init__(
        self,
        allowed_section_iv: Iterable,
        allowed_section_v: Iterable,
    ) -> None:
        self.allowed_section_iv = frozenset(allowed_section_iv)
        self.allowed_section_v = frozenset(allowed_section_v)

    def validate_section_iv(self, values: Iterable) -> list:
        """Kiểm mỗi giá trị tick Phần IV thuộc tập cho phép; trả list đã kiểm.

        Raise TickValueError nếu có giá trị ngoài tập (BR4.6).
        """
        return self._validate(values, self.allowed_section_iv, "IV")

    def validate_section_v(self, values: Iterable) -> list:
        """Kiểm giá trị tick Phần V thuộc tập cho phép, rồi áp quy tắc 6/7/8→+4,5.

        Raise TickValueError nếu có giá trị ngoài tập (BR4.6). Trả list cuối cùng
        (đã thêm 4 và 5 khi cần, không trùng lặp, giữ thứ tự ổn định).
        """
        checked = self._validate(values, self.allowed_section_v, "V")
        result = list(checked)
        if self.SECTION_V_TRIGGER & set(result):
            for implied in sorted(self.SECTION_V_IMPLIED):
                if implied not in result:
                    result.append(implied)
        return result

    @staticmethod
    def _validate(values: Iterable, allowed: frozenset, section: str) -> list:
        checked = list(values)
        outside = [v for v in checked if v not in allowed]
        if outside:
            raise TickValueError(
                f"Phần {section} có giá trị tick ngoài tập cho phép: {outside}"
            )
        return checked
