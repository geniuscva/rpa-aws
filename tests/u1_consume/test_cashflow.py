"""Test CashFlowCalculator: công thức dòng tiền theo US2."""
from decimal import Decimal

from robot.u1_consume.cashflow import CashFlowCalculator, CashFlowPdfRenderer


def _rows():
    return [
        {"HUONG_GD": "C", "TK_DOIUNG": "A1", "TENKH_DOIUNG": "KH1", "MA_GD": "G1", "SOTIEN_GD_QD": "100"},
        {"HUONG_GD": "C", "TK_DOIUNG": "A1", "TENKH_DOIUNG": "KH1", "MA_GD": "G2", "SOTIEN_GD_QD": "50"},
        {"HUONG_GD": "C", "TK_DOIUNG": "A2", "TENKH_DOIUNG": "KH2", "MA_GD": "G3", "SOTIEN_GD_QD": "25"},
        {"HUONG_GD": "D", "TK_DOIUNG": "B1", "TENKH_DOIUNG": "KHX", "MA_GD": "G4", "SOTIEN_GD_QD": "200"},
    ]


def test_inflow_computation():
    inflow, _ = CashFlowCalculator.compute(_rows())
    assert inflow.customer_count == 2  # (A1|KH1), (A2|KH2)
    assert inflow.transaction_count == 3
    assert inflow.amount == Decimal("175")


def test_outflow_computation():
    _, outflow = CashFlowCalculator.compute(_rows())
    assert outflow.customer_count == 1
    assert outflow.transaction_count == 1
    assert outflow.amount == Decimal("200")


def test_empty_statement():
    inflow, outflow = CashFlowCalculator.compute([])
    assert inflow.customer_count == 0
    assert inflow.amount == Decimal("0")
    assert outflow.transaction_count == 0


def test_invalid_amount_treated_as_zero():
    rows = [{"HUONG_GD": "C", "TK_DOIUNG": "A", "TENKH_DOIUNG": "K", "MA_GD": "G", "SOTIEN_GD_QD": "abc"}]
    inflow, _ = CashFlowCalculator.compute(rows)
    assert inflow.amount == Decimal("0")


def test_pdf_renderer_writes_file(tmp_path):
    inflow, outflow = CashFlowCalculator.compute(_rows())
    renderer = CashFlowPdfRenderer(str(tmp_path))
    path = renderer.render("Cong ty ABC", inflow, outflow)
    assert path.endswith("Minh Họa Dòng Tiền.pdf")
    import os

    assert os.path.isfile(path)
