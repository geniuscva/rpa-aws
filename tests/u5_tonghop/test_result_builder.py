"""Test ResultBuilder (U5): StrRecord -> ProcessingResult (BR5.1/5.5)."""
from robot.models import StrRecord
from robot.u5_tonghop.result_builder import (
    STATUS_FAIL,
    STATUS_SUCCESS,
    ResultBuilder,
)


def test_success_record_maps_to_success():
    rec = StrRecord(cif="C001", bot_almd="OK", bot_tinhtrangtrasoat="DaTraSoat")
    r = ResultBuilder().build(rec, stt=1)
    assert r.status == STATUS_SUCCESS
    assert r.cif == "C001"
    assert r.error_code == "" and r.error_detail == ""


def test_stopped_record_maps_to_fail_with_detail():
    rec = StrRecord(cif="C002")
    rec.stop("U4-DataEntryAMLD", "Thiếu tài liệu bắt buộc: Bảng kê")
    r = ResultBuilder().build(rec, stt=2)
    assert r.status == STATUS_FAIL
    assert "Bảng kê" in r.error_detail


def test_error_bot_field_maps_to_fail():
    rec = StrRecord(cif="C003", bot_almd="ERROR", bot_tinhtrangtrasoat="ERROR")
    r = ResultBuilder().build(rec, stt=3)
    assert r.status == STATUS_FAIL
    assert r.error_code == "ERROR"


def test_build_batch_numbers_stt_in_order():
    recs = [StrRecord(cif=f"C{i}") for i in range(1, 4)]
    recs[1].stop("U2", "loi")
    results = ResultBuilder().build_batch(recs)
    assert [r.stt for r in results] == [1, 2, 3]
    # KH lỗi vẫn có một hàng (cô lập lỗi BR5.5).
    assert results[1].status == STATUS_FAIL
    assert results[0].status == STATUS_SUCCESS
    assert results[2].status == STATUS_SUCCESS
