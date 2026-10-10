"""Test AccuityStage (U2) tích hợp pipeline với AccuityPort mock.

Kịch bản: KHCN/KHDN thành công cập nhật BOT_ACCUITY và nối dossier PDF;
lỗi login/lookup -> dừng record (processing_stopped) và ghi BOT_GHICHU;
record đã dừng từ trước -> U2 bỏ qua.
"""
from typing import Any

from robot.config import Config
from robot.logging_setup import StructuredLogger
from robot.models import CustomerType, StrRecord
from robot.pipeline import StageContext
from robot.u2_accuity.accuity_stage import AccuityStage


class FakeAccuityPort:
    def __init__(self, lookup_result=None, fail_on=None):
        self.lookup_result = lookup_result if lookup_result is not None else {"match_score": 80}
        self.fail_on = fail_on

    def login(self) -> None:
        if self.fail_on == "login":
            raise RuntimeError("login that bai")

    def lookup(self, entity_type: str, name: str) -> dict[str, Any]:
        if self.fail_on == "lookup":
            raise RuntimeError("lookup loi")
        return dict(self.lookup_result)

    def export_result_pdf(self, output_path: str) -> str:
        return output_path

    def export_record_pdf(self, output_path: str) -> str:
        return output_path


def _context(tmp_path) -> StageContext:
    cfg = Config(source_root=str(tmp_path), output_root=str(tmp_path / "out"))
    logger = StructuredLogger(str(tmp_path / "log.json"), echo_stdout=False)
    return StageContext(config=cfg, logger=logger)


def _stage(port: FakeAccuityPort) -> AccuityStage:
    return AccuityStage(port_factory=lambda ctx: port)


def test_khcn_success_updates_bot_accuity(tmp_path):
    port = FakeAccuityPort(lookup_result={"match_score": 90})
    stage = _stage(port)
    record = StrRecord(cif="C001", ten_khach_hang="Nguyen Van A",
                       loai_khach_hang=CustomerType.KHCN.value)

    out = stage.process(record, _context(tmp_path))

    assert out.processing_stopped is False
    assert "OK" in out.bot_accuity
    assert "match=90" in out.bot_accuity
    assert out.written_by == AccuityStage.name
    assert len(out.dossier_pdf_paths) == 1


def test_khdn_full_match_appends_two_pdfs(tmp_path):
    port = FakeAccuityPort(lookup_result={"match_score": 100})
    stage = _stage(port)
    record = StrRecord(cif="C002", ten_khach_hang="Cong ty ABC",
                       loai_khach_hang=CustomerType.KHDN.value,
                       dossier_pdf_paths=["existing.pdf"])

    out = stage.process(record, _context(tmp_path))

    assert out.processing_stopped is False
    # giữ file cũ + 2 file mới (tra cứu + hồ sơ)
    assert len(out.dossier_pdf_paths) == 3
    assert "existing.pdf" in out.dossier_pdf_paths


def test_login_failure_stops_record(tmp_path):
    port = FakeAccuityPort(fail_on="login")
    stage = _stage(port)
    record = StrRecord(cif="C003", ten_khach_hang="X",
                       loai_khach_hang=CustomerType.KHCN.value)

    out = stage.process(record, _context(tmp_path))

    assert out.processing_stopped is True
    assert out.bot_accuity == "ERROR"
    assert "Accuity" in out.bot_ghichu
    assert out.written_by == AccuityStage.name


def test_lookup_failure_stops_record(tmp_path):
    port = FakeAccuityPort(fail_on="lookup")
    stage = _stage(port)
    record = StrRecord(cif="C004", ten_khach_hang="Y",
                       loai_khach_hang=CustomerType.KHDN.value)

    out = stage.process(record, _context(tmp_path))

    assert out.processing_stopped is True
    assert out.bot_accuity == "ERROR"
    assert out.bot_ghichu


def test_already_stopped_record_is_skipped(tmp_path):
    port = FakeAccuityPort(lookup_result={"match_score": 100})
    stage = _stage(port)
    record = StrRecord(cif="C005", loai_khach_hang=CustomerType.KHCN.value)
    record.stop("U1-ConsumeData", "loi upstream")

    out = stage.process(record, _context(tmp_path))

    # U2 không chạm vào record đã dừng
    assert out.bot_accuity == ""
    assert out.written_by == "U1-ConsumeData"


def test_name_falls_back_to_cif_when_no_customer_name(tmp_path):
    port = FakeAccuityPort(lookup_result={"match_score": 70})
    stage = _stage(port)
    record = StrRecord(cif="C006", ten_khach_hang="",
                       loai_khach_hang=CustomerType.KHCN.value)

    out = stage.process(record, _context(tmp_path))
    assert out.processing_stopped is False
    assert "OK" in out.bot_accuity
