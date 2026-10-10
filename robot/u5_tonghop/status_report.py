"""BatchStatusReport: dựng file Excel trạng thái lô đúng cột (BR5.2).

Cột: STT, STR_CIF, Trạng thái, Mã lỗi, Chi tiết lỗi. Mỗi hàng là một
ProcessingResult theo thứ tự STT. openpyxl được import trễ để test mock/kiểm
tra được mà không bắt buộc có thư viện ở mọi môi trường.
"""
from __future__ import annotations

import os
from typing import Any, Callable, Optional

from robot.u5_tonghop.result_builder import ProcessingResult

COLUMNS = ["STT", "STR_CIF", "Trạng thái", "Mã lỗi", "Chi tiết lỗi"]


def _default_workbook_factory() -> Any:
    """Dựng workbook openpyxl thật. Import trễ để test mock được."""
    from openpyxl import Workbook  # type: ignore

    return Workbook()


class BatchStatusReport:
    """Dựng file Excel trạng thái cho cả lô."""

    def __init__(self, workbook_factory: Callable[[], Any] = _default_workbook_factory) -> None:
        self._workbook_factory = workbook_factory

    @staticmethod
    def rows(results: list[ProcessingResult]) -> list[list]:
        """Trả các hàng (gồm header) đúng thứ tự cột — thuần, test được."""
        data: list[list] = [list(COLUMNS)]
        for r in results:
            data.append([r.stt, r.cif, r.status, r.error_code, r.error_detail])
        return data

    def write(self, results: list[ProcessingResult], path: str) -> str:
        """Ghi file Excel ra `path`, trả đường dẫn. Dựng đúng cột (BR5.2)."""
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        wb = self._workbook_factory()
        ws = wb.active
        ws.title = "TrangThai"
        for row in self.rows(results):
            ws.append(row)
        wb.save(path)
        return path
