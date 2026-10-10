"""ExcelReader: đọc các file excel nguồn của một CIF.

Trả dữ liệu dạng list[dict] cho mỗi sheet quan tâm. Ẩn chi tiết openpyxl để test
có thể mock. Import openpyxl tại chỗ.
"""
from __future__ import annotations

import os
from typing import Any

from robot.u1_consume.source_folder import (
    INDIVIDUAL_FILE,
    ORG_FILE,
)

STATEMENT_FILE = "bang_ke_giao_dich_tai_khoan_dang_ngo.xlsx"
SUSPICIOUS_FILE = "thong_tin_giao_dich_dang_ngo.xlsx"
INPUT_STR_FILE = "thong_tin_dau_vao_bao_cao_str.xlsx"


def read_xlsx_rows(path: str) -> list[dict[str, Any]]:
    """Đọc sheet đầu tiên của file xlsx thành list[dict], key là header hàng đầu.

    Raise FileNotFoundError nếu thiếu file. Import openpyxl tại chỗ.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    import openpyxl

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        ws = wb.worksheets[0]
        rows_iter = ws.iter_rows(values_only=True)
        try:
            header = [str(h) if h is not None else "" for h in next(rows_iter)]
        except StopIteration:
            return []
        result: list[dict[str, Any]] = []
        for raw in rows_iter:
            if raw is None:
                continue
            record = {header[i]: raw[i] for i in range(min(len(header), len(raw)))}
            if any(v is not None for v in record.values()):
                result.append(record)
        return result
    finally:
        wb.close()


class ExcelReader:
    """Đọc các file excel của một folder CIF."""

    def __init__(self, folder: str) -> None:
        self.folder = folder

    def _read(self, filename: str) -> list[dict[str, Any]]:
        return read_xlsx_rows(os.path.join(self.folder, filename))

    def read_statement(self) -> list[dict[str, Any]]:
        return self._read(STATEMENT_FILE)

    def read_suspicious(self) -> list[dict[str, Any]]:
        return self._read(SUSPICIOUS_FILE)

    def read_input_str(self) -> list[dict[str, Any]]:
        return self._read(INPUT_STR_FILE)

    def read_individual(self) -> list[dict[str, Any]]:
        return self._read(INDIVIDUAL_FILE)

    def read_org(self) -> list[dict[str, Any]]:
        return self._read(ORG_FILE)
