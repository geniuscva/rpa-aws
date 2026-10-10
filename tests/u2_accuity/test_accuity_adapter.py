"""Test AccuityClient orchestration qua AccuityPort mock (NFR6).

Kiểm tra: login + lookup + export PDF; mapping loại KH -> entity_type;
export PDF thứ hai khi match_score=100; gom lỗi cổng thành AccuityError.
"""
from typing import Any

import pytest

from robot.config import Config
from robot.logging_setup import StructuredLogger
from robot.models import CustomerType
from robot.u2_accuity.accuity_adapter import (
    AccuityClient,
    AccuityError,
    AccuityResult,
)


class FakeAccuityPort:
    """Mock AccuityPort ghi lại các lời gọi; cấu hình được kết quả lookup và lỗi."""

    def __init__(self, lookup_result=None, fail_on=None):
        self.lookup_result = lookup_result if lookup_result is not None else {"match_score": 80}
        self.fail_on = fail_on  # "login" | "lookup" | None
        self.calls: list[str] = []
        self.exported: list[str] = []

    def login(self) -> None:
        self.calls.append("login")
        if self.fail_on == "login":
            raise RuntimeError("login that bai")

    def lookup(self, entity_type: str, name: str) -> dict[str, Any]:
        self.calls.append(f"lookup:{entity_type}:{name}")
        if self.fail_on == "lookup":
            raise RuntimeError("lookup loi")
        return dict(self.lookup_result)

    def export_result_pdf(self, output_path: str) -> str:
        self.calls.append("export_result_pdf")
        self.exported.append(output_path)
        return output_path

    def export_record_pdf(self, output_path: str) -> str:
        self.calls.append("export_record_pdf")
        self.exported.append(output_path)
        return output_path


def _logger(tmp_path) -> StructuredLogger:
    return StructuredLogger(str(tmp_path / "log.json"), echo_stdout=False)


def test_entity_type_mapping():
    assert AccuityClient.entity_type_for(CustomerType.KHCN.value) == "Individual"
    assert AccuityClient.entity_type_for(CustomerType.KHDN.value) == "Organization"


def test_lookup_khcn_happy_path(tmp_path):
    port = FakeAccuityPort(lookup_result={"match_score": 80})
    client = AccuityClient(port, _logger(tmp_path), str(tmp_path / "out"))

    result = client.lookup_customer(CustomerType.KHCN.value, "Nguyen Van A")

    assert isinstance(result, AccuityResult)
    assert result.match_score == 80
    # match < 100 -> chỉ 1 PDF kết quả tra cứu
    assert len(result.pdf_paths) == 1
    assert port.calls == ["login", "lookup:Individual:Nguyen Van A", "export_result_pdf"]


def test_lookup_khdn_full_match_exports_second_pdf(tmp_path):
    port = FakeAccuityPort(lookup_result={"match_score": 100})
    client = AccuityClient(port, _logger(tmp_path), str(tmp_path / "out"))

    result = client.lookup_customer(CustomerType.KHDN.value, "Cong ty ABC")

    assert result.match_score == 100
    # match = 100 -> xuất thêm PDF hồ sơ (2 file)
    assert len(result.pdf_paths) == 2
    assert "export_record_pdf" in port.calls
    assert "lookup:Organization:Cong ty ABC" in port.calls


def test_login_failure_raises_accuity_error(tmp_path):
    port = FakeAccuityPort(fail_on="login")
    client = AccuityClient(port, _logger(tmp_path), str(tmp_path / "out"))

    with pytest.raises(AccuityError) as exc:
        client.lookup_customer(CustomerType.KHCN.value, "X")
    assert "Accuity lookup" in str(exc.value)


def test_lookup_failure_raises_accuity_error(tmp_path):
    port = FakeAccuityPort(fail_on="lookup")
    client = AccuityClient(port, _logger(tmp_path), str(tmp_path / "out"))

    with pytest.raises(AccuityError):
        client.lookup_customer(CustomerType.KHDN.value, "Y")


def test_missing_match_score_defaults_to_zero(tmp_path):
    port = FakeAccuityPort(lookup_result={})
    client = AccuityClient(port, _logger(tmp_path), str(tmp_path / "out"))

    result = client.lookup_customer(CustomerType.KHCN.value, "Z")
    assert result.match_score == 0
    assert len(result.pdf_paths) == 1
