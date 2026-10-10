"""Test TongHopStage (U5): tổng hợp lô + gửi email lô (BR5.1-5.7).

Mock EmailPort + workbook; không gửi mail/ghi Excel thật.
"""
from robot.config import Config
from robot.logging_setup import StructuredLogger
from robot.models import StrRecord
from robot.pipeline import StageContext
from robot.u5_tonghop.email_sender import MockEmailPort
from robot.u5_tonghop.status_report import BatchStatusReport
from robot.u5_tonghop.tonghop_stage import TongHopStage


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


def _context(tmp_path) -> StageContext:
    cfg = Config(source_root=str(tmp_path), output_root=str(tmp_path / "out"))
    logger = StructuredLogger(str(tmp_path / "log.json"), echo_stdout=False)
    return StageContext(config=cfg, logger=logger)


def _stage(port: MockEmailPort) -> TongHopStage:
    return TongHopStage(
        email_port_factory=lambda ctx: port,
        status_report=BatchStatusReport(workbook_factory=FakeWorkbook),
    )


def _records():
    ok = StrRecord(cif="C001", email_nguoi_lap_bao_cao="lap@bank.vn",
                   bot_almd="OK", bot_tinhtrangtrasoat="DaTraSoat")
    fail = StrRecord(cif="C002", email_nguoi_lap_bao_cao="lap@bank.vn")
    fail.stop("U4-DataEntryAMLD", "Thiếu tài liệu bắt buộc")
    return [ok, fail]


def test_batch_all_success_sends_one_email(tmp_path):
    port = MockEmailPort()
    recs = [StrRecord(cif="C001", email_nguoi_lap_bao_cao="lap@bank.vn",
                      bot_almd="OK", bot_tinhtrangtrasoat="OK")]
    out = _stage(port).process_batch(recs, _context(tmp_path))

    assert out.sent is True
    assert out.sent_at
    assert out.success_count == 1 and out.fail_count == 0
    assert len(port.sent) == 1
    assert port.sent[0].to == "lap@bank.vn"
    assert port.sent[0].attachment_path.endswith("TrangThaiXuLyLo.xlsx")


def test_batch_with_failures_still_one_email_all_rows(tmp_path):
    port = MockEmailPort()
    out = _stage(port).process_batch(_records(), _context(tmp_path))

    # Cô lập lỗi: một email lô, đủ 2 hàng (1 OK + 1 FAIL) — BR5.4/5.5.
    assert out.sent is True
    assert out.success_count == 1 and out.fail_count == 1
    assert len(out.results) == 2
    assert len(port.sent) == 1


def test_email_send_failure_keeps_report(tmp_path):
    port = MockEmailPort(fail=True)
    out = _stage(port).process_batch(_records(), _context(tmp_path))

    # Gửi lỗi → report vẫn dựng, không raise (BR5.3).
    assert out.sent is False
    assert out.error
    assert out.report_path.endswith("TrangThaiXuLyLo.xlsx")
    assert len(out.results) == 2
