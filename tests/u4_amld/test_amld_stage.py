"""Test AmldStage (U4) tích hợp pipeline với AmldPortalPort mock.

Kịch bản (unit-test-instructions.md + project.md):
- KHCN/KHDN đủ tài liệu → BOT_ALMD=OK, nhập I→II→IV→V→VI, KHÔNG có Phần III.
- Thiếu tài liệu bắt buộc → không nộp, dừng record (BR4.7).
- Tick ngoài tập → dừng record, không đi tiếp (BR4.6).
- Phần V có 6/7/8 → tự tick thêm 4,5 (BR4.5).
- Bước nhập lỗi quá 3 lần → dừng record (BR4.8).
- Đăng nhập treo quá 3 lần → dừng record (BR4.9).
- Record đã dừng từ trước → U4 bỏ qua.
Mock AmldPortalPort; không chạm AMLD Portal thật.
"""
from robot.config import Config
from robot.logging_setup import StructuredLogger
from robot.models import CustomerType, StrRecord
from robot.pipeline import StageContext
from robot.u4_amld.amld_portal_adapter import MockAmldPortalPort
from robot.u4_amld.amld_stage import AmldStage
from robot.u4_amld.retry_policy import RetryPolicy
from robot.u4_amld.tick_validator import TickValidator

REQUIRED_PDFS = [
    "/out/C/Bảng kê.pdf",
    "/out/C/Minh Họa Dòng Tiền.pdf",
    "/out/C/HSMTK_001.pdf",
]


def _context(tmp_path) -> StageContext:
    cfg = Config(source_root=str(tmp_path), output_root=str(tmp_path / "out"))
    logger = StructuredLogger(str(tmp_path / "log.json"), echo_stdout=False)
    return StageContext(config=cfg, logger=logger)


def _record(**kw) -> StrRecord:
    base = dict(
        cif="C001",
        loai_khach_hang=CustomerType.KHCN.value,
        user_id_nguoi_lap_bao_cao="user01",
        dossier_pdf_paths=list(REQUIRED_PDFS),
    )
    base.update(kw)
    return StrRecord(**base)


def test_khcn_happy_path_sets_ok_and_skips_section_iii(tmp_path):
    port = MockAmldPortalPort(trasoat_status="DaTraSoat")
    stage = AmldStage(port_factory=lambda ctx: port)
    out = stage.process(_record(), _context(tmp_path))

    assert out.processing_stopped is False
    assert out.bot_almd == "OK"
    assert out.bot_tinhtrangtrasoat == "DaTraSoat"
    assert out.written_by == AmldStage.name
    # BR4.2: nhập I→II→IV→V→VI, KHÔNG có Phần III.
    assert port.sections_filled == ["I", "II", "IV", "V", "VI"]
    assert "III" not in port.sections_filled
    assert port.submitted is True


def test_khdn_happy_path(tmp_path):
    port = MockAmldPortalPort()
    stage = AmldStage(port_factory=lambda ctx: port)
    out = stage.process(_record(cif="C002", loai_khach_hang=CustomerType.KHDN.value),
                        _context(tmp_path))
    assert out.bot_almd == "OK"
    assert "III" not in port.sections_filled


def test_missing_required_attachment_stops_without_submit(tmp_path):
    port = MockAmldPortalPort()
    stage = AmldStage(port_factory=lambda ctx: port)
    # Thiếu Minh Họa Dòng Tiền.pdf.
    record = _record(dossier_pdf_paths=["/out/C/Bảng kê.pdf", "/out/C/HSMTK_001.pdf"])
    out = stage.process(record, _context(tmp_path))

    assert out.processing_stopped is True
    assert out.bot_almd == "ERROR"
    assert out.bot_tinhtrangtrasoat == "ERROR"
    assert out.bot_ghichu
    assert port.submitted is False  # BR4.7: không nộp khi thiếu đính kèm


def test_tick_outside_set_stops_flow(tmp_path):
    port = MockAmldPortalPort()
    # Phần IV trả giá trị ngoài tập (99) → dừng, không đi tiếp.
    stage = AmldStage(
        port_factory=lambda ctx: port,
        tick_validator=TickValidator(allowed_section_iv=range(1, 9), allowed_section_v=range(1, 9)),
        section_iv_ticks=lambda r: [1, 99],
    )
    out = stage.process(_record(), _context(tmp_path))

    assert out.processing_stopped is True
    assert out.bot_almd == "ERROR"
    assert port.submitted is False
    # Phần V không được nhập sau khi Phần IV lỗi (không đi tiếp).
    assert "V" not in port.sections_filled


def test_section_v_trigger_adds_4_and_5(tmp_path):
    port = MockAmldPortalPort()
    stage = AmldStage(
        port_factory=lambda ctx: port,
        section_v_ticks=lambda r: [6],
    )
    out = stage.process(_record(), _context(tmp_path))

    assert out.bot_almd == "OK"
    assert set(port.ticks["V"]) >= {4, 5, 6}  # BR4.5


def test_step_failure_over_retry_limit_stops(tmp_path):
    # open_form luôn lỗi → RetryPolicy hết lượt → dừng record (BR4.8).
    port = MockAmldPortalPort(fail_on="open_form")
    stage = AmldStage(port_factory=lambda ctx: port, retry_policy=RetryPolicy(max_attempts=3))
    out = stage.process(_record(), _context(tmp_path))

    assert out.processing_stopped is True
    assert out.bot_almd == "ERROR"
    assert out.bot_ghichu


def test_login_hang_over_limit_stops(tmp_path):
    # Đăng nhập treo 4 lần > giới hạn 3 → dừng record (BR4.9).
    port = MockAmldPortalPort(login_hangs=4)
    stage = AmldStage(port_factory=lambda ctx: port)
    out = stage.process(_record(), _context(tmp_path))

    assert out.processing_stopped is True
    assert out.bot_almd == "ERROR"
    assert port.submitted is False


def test_login_hang_within_limit_recovers(tmp_path):
    # Treo 2 lần rồi vào được → OK.
    port = MockAmldPortalPort(login_hangs=2)
    stage = AmldStage(port_factory=lambda ctx: port)
    out = stage.process(_record(), _context(tmp_path))
    assert out.bot_almd == "OK"


def test_already_stopped_record_is_skipped(tmp_path):
    port = MockAmldPortalPort()
    stage = AmldStage(port_factory=lambda ctx: port)
    record = _record(cif="C099")
    record.stop("U3-DataEntryTraCuuThue", "loi upstream")
    out = stage.process(record, _context(tmp_path))

    # U4 không chạm record đã dừng.
    assert out.bot_almd == ""
    assert out.written_by == "U3-DataEntryTraCuuThue"
    assert port.submitted is False
