"""Test ConsumeDataStage end-to-end với mock ECM và folder tạm."""
from datetime import date

import openpyxl

from robot.config import Config
from robot.logging_setup import StructuredLogger
from robot.models import CustomerType, StrRecord
from robot.pipeline import StageContext
from robot.u1_consume.consume_stage import ConsumeDataStage
from robot.u1_consume.source_folder import (
    INDIVIDUAL_FILE,
    ORG_FILE,
    SourceFolderResolver,
)
from tests.u1_consume.test_ecm_client import FakeTransport
from robot.u1_consume.ecm_client import EcmClientAdapter


def _write_xlsx(path, header, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(header)
    for r in rows:
        ws.append(r)
    wb.save(path)


def _make_folder(tmp_path, cif, customer_file):
    d = date.today()
    folder = tmp_path / d.strftime("%Y%m") / d.strftime("%Y%m%d") / cif
    folder.mkdir(parents=True)
    _write_xlsx(
        folder / "thong_tin_dau_vao_bao_cao_str.xlsx",
        ["STR_TEN_KH", "Ma_So_Doanh_Nghiep", "EMAIL_NGUOI_LAP_BAO_CAO"],
        [["Cong ty ABC", "0101234567", "nguoilap@mbbank.com.vn"]],
    )
    _write_xlsx(
        folder / "bang_ke_giao_dich_tai_khoan_dang_ngo.xlsx",
        ["HUONG_GD", "TK_DOIUNG", "TENKH_DOIUNG", "MA_GD", "SOTIEN_GD_QD"],
        [["C", "A1", "KH1", "G1", "100"], ["D", "B1", "KHX", "G2", "50"]],
    )
    _write_xlsx(folder / "thong_tin_giao_dich_dang_ngo.xlsx", ["X"], [["1"]])
    (folder / customer_file).write_text("x", encoding="utf-8")
    return folder


def _context(tmp_path):
    cfg = Config(source_root=str(tmp_path), output_root=str(tmp_path / "out"))
    logger = StructuredLogger(str(tmp_path / "log.json"), echo_stdout=False)
    return StageContext(config=cfg, logger=logger)


def _stage(tmp_path, transport=None):
    transport = transport or FakeTransport(files_by_code={"mb_smart_channel": [{"doc_id": "d1"}]})

    def factory(cif, output_dir):
        from robot.config import EcmConfig

        return EcmClientAdapter(
            EcmConfig(business_codes=["mb_smart_channel"], retries=1),
            StructuredLogger(str(tmp_path / "log.json"), echo_stdout=False),
            transport,
            output_dir,
        )

    return ConsumeDataStage(ecm_client_factory=factory, resolver=SourceFolderResolver(str(tmp_path)))


def test_happy_path_khdn(tmp_path):
    _make_folder(tmp_path, "6670501", ORG_FILE)
    stage = _stage(tmp_path)
    record = stage.process(StrRecord(cif="6670501"), _context(tmp_path))
    assert record.processing_stopped is False
    assert record.loai_khach_hang == CustomerType.KHDN.value
    assert record.ten_khach_hang == "Cong ty ABC"
    assert record.ma_so_thue == "0101234567"
    assert record.so_tien_giaodich_vao is not None
    assert record.cashflow_pdf_path
    assert record.bot_ecm == "OK"


def test_happy_path_khcn(tmp_path):
    _make_folder(tmp_path, "6670502", INDIVIDUAL_FILE)
    stage = _stage(tmp_path)
    record = stage.process(StrRecord(cif="6670502"), _context(tmp_path))
    assert record.processing_stopped is False
    assert record.loai_khach_hang == CustomerType.KHCN.value


def test_missing_folder_stops(tmp_path):
    stage = _stage(tmp_path)
    record = stage.process(StrRecord(cif="0000000"), _context(tmp_path))
    assert record.processing_stopped is True
    assert "thu muc" in record.bot_ghichu.lower()


def test_ecm_error_stops(tmp_path):
    _make_folder(tmp_path, "6670503", ORG_FILE)
    stage = _stage(tmp_path, transport=FakeTransport(fail_token=True))
    record = stage.process(StrRecord(cif="6670503"), _context(tmp_path))
    assert record.processing_stopped is True
    assert record.bot_ecm == "ERROR"
