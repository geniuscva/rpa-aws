"""Test TaxAuthorityStage (U3) tích hợp pipeline với TaxAuthorityPort mock.

Kịch bản (unit-test-instructions.md):
- KHDN có kết quả → BOT_TRACUUTHE=OK, nối PDF.
- KHCN → BOT_TRACUUTHE=SKIPPED, không tra cứu.
- KHDN không có kết quả → SKIPPED, không in PDF, không lỗi.
- Captcha fail vượt giới hạn → dừng record (processing_stopped).
- Lỗi thao tác web → dừng record.
- KHDN thiếu MST → lỗi, dừng record.
- Record đã dừng từ trước → U3 bỏ qua.
Dùng mock TaxAuthorityPort + CaptchaSolver, không chạm web/ddddocr thật.
"""
from robot.config import Config
from robot.logging_setup import StructuredLogger
from robot.models import CustomerType, StrRecord
from robot.pipeline import StageContext
from robot.u3_tracuuthue.captcha_solver import CaptchaSolver
from robot.u3_tracuuthue.tax_authority_adapter import MockTaxAuthorityPort
from robot.u3_tracuuthue.tax_stage import TaxAuthorityStage


def _context(tmp_path) -> StageContext:
    cfg = Config(source_root=str(tmp_path), output_root=str(tmp_path / "out"))
    logger = StructuredLogger(str(tmp_path / "log.json"), echo_stdout=False)
    return StageContext(config=cfg, logger=logger)


def _solver(outputs=("OK",), max_attempts=3) -> CaptchaSolver:
    class _Engine:
        def classification(self, image: bytes) -> str:
            return outputs[0]

    return CaptchaSolver(engine_factory=lambda: _Engine(), max_attempts=max_attempts)


def _stage(port: MockTaxAuthorityPort, solver: CaptchaSolver = None) -> TaxAuthorityStage:
    return TaxAuthorityStage(
        port_factory=lambda ctx: port,
        captcha_solver_factory=lambda ctx: solver or _solver(),
    )


def test_khdn_with_result_sets_ok_and_appends_pdf(tmp_path):
    port = MockTaxAuthorityPort(has_result=True, accept_after=1)
    stage = _stage(port)
    record = StrRecord(cif="C001", loai_khach_hang=CustomerType.KHDN.value,
                       ma_so_thue="0101234567")

    out = stage.process(record, _context(tmp_path))

    assert out.processing_stopped is False
    assert out.bot_tracuuthe == "OK"
    assert out.written_by == TaxAuthorityStage.name
    assert len(out.dossier_pdf_paths) == 1
    assert out.dossier_pdf_paths[0].endswith("Tra cứu tình trạng người nộp thuế.pdf")


def test_khcn_is_skipped_without_lookup(tmp_path):
    port = MockTaxAuthorityPort(has_result=True)
    stage = _stage(port)
    record = StrRecord(cif="C002", loai_khach_hang=CustomerType.KHCN.value,
                       ma_so_thue="irrelevant")

    out = stage.process(record, _context(tmp_path))

    assert out.processing_stopped is False
    assert out.bot_tracuuthe == "SKIPPED"
    assert out.dossier_pdf_paths == []
    assert out.written_by == TaxAuthorityStage.name


def test_khdn_no_result_is_skipped_no_pdf(tmp_path):
    port = MockTaxAuthorityPort(has_result=False, accept_after=1)
    stage = _stage(port)
    record = StrRecord(cif="C003", loai_khach_hang=CustomerType.KHDN.value,
                       ma_so_thue="0107654321")

    out = stage.process(record, _context(tmp_path))

    assert out.processing_stopped is False
    assert out.bot_tracuuthe == "SKIPPED"
    assert out.dossier_pdf_paths == []


def test_captcha_fail_over_limit_stops_record(tmp_path):
    # Port không bao giờ chấp nhận captcha (accept_after lớn hơn max_attempts).
    port = MockTaxAuthorityPort(has_result=True, accept_after=99)
    stage = _stage(port, solver=_solver(max_attempts=3))
    record = StrRecord(cif="C004", loai_khach_hang=CustomerType.KHDN.value,
                       ma_so_thue="0101111111")

    out = stage.process(record, _context(tmp_path))

    assert out.processing_stopped is True
    assert out.bot_tracuuthe == "ERROR"
    assert out.bot_ghichu
    assert out.written_by == TaxAuthorityStage.name


def test_web_error_stops_record(tmp_path):
    port = MockTaxAuthorityPort(has_result=True, fail_on="open")
    stage = _stage(port)
    record = StrRecord(cif="C005", loai_khach_hang=CustomerType.KHDN.value,
                       ma_so_thue="0102222222")

    out = stage.process(record, _context(tmp_path))

    assert out.processing_stopped is True
    assert out.bot_tracuuthe == "ERROR"
    assert out.bot_ghichu


def test_khdn_missing_mst_stops_record(tmp_path):
    port = MockTaxAuthorityPort(has_result=True)
    stage = _stage(port)
    record = StrRecord(cif="C006", loai_khach_hang=CustomerType.KHDN.value, ma_so_thue="")

    out = stage.process(record, _context(tmp_path))

    assert out.processing_stopped is True
    assert out.bot_tracuuthe == "ERROR"
    assert "mã số thuế" in out.bot_ghichu or "ma so thue" in out.bot_ghichu.lower()


def test_already_stopped_record_is_skipped(tmp_path):
    port = MockTaxAuthorityPort(has_result=True)
    stage = _stage(port)
    record = StrRecord(cif="C007", loai_khach_hang=CustomerType.KHDN.value,
                       ma_so_thue="0103333333")
    record.stop("U1-ConsumeData", "loi upstream")

    out = stage.process(record, _context(tmp_path))

    # U3 không chạm record đã dừng.
    assert out.bot_tracuuthe == ""
    assert out.written_by == "U1-ConsumeData"
