"""Test BatchStatusReport (U5): file Excel đúng cột (BR5.2).

Dùng FakeWorkbook để kiểm nội dung ghi mà không cần openpyxl thật.
"""
from robot.u5_tonghop.result_builder import ProcessingResult
from robot.u5_tonghop.status_report import COLUMNS, BatchStatusReport


class FakeSheet:
    def __init__(self):
        self.title = ""
        self.rows = []

    def append(self, row):
        self.rows.append(list(row))


class FakeWorkbook:
    def __init__(self):
        self.active = FakeSheet()
        self.saved_to = None

    def save(self, path):
        self.saved_to = path


def _results():
    return [
        ProcessingResult(stt=1, cif="C001", status="Thành công"),
        ProcessingResult(stt=2, cif="C002", status="Lỗi", error_code="ERROR",
                         error_detail="Thiếu Bảng kê"),
    ]


def test_rows_have_correct_columns_and_order():
    rows = BatchStatusReport.rows(_results())
    assert rows[0] == COLUMNS
    assert rows[1] == [1, "C001", "Thành công", "", ""]
    assert rows[2] == [2, "C002", "Lỗi", "ERROR", "Thiếu Bảng kê"]


def test_write_saves_workbook_with_header_and_rows(tmp_path):
    wb = FakeWorkbook()
    report = BatchStatusReport(workbook_factory=lambda: wb)
    path = str(tmp_path / "out" / "TrangThai.xlsx")

    returned = report.write(_results(), path)

    assert returned == path
    assert wb.saved_to == path
    assert wb.active.rows[0] == COLUMNS
    assert len(wb.active.rows) == 3  # header + 2 hàng


def test_empty_batch_writes_header_only(tmp_path):
    wb = FakeWorkbook()
    report = BatchStatusReport(workbook_factory=lambda: wb)
    report.write([], str(tmp_path / "r.xlsx"))
    assert wb.active.rows == [COLUMNS]
