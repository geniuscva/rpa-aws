"""ResultBuilder: dẫn xuất ProcessingResult cho từng StrRecord (BR5.1, BR5.5).

Mỗi CIF (gồm cả KH lỗi/dừng luồng) đều có một ProcessingResult: status FAIL khi
processingStopped=true hoặc có BOT_* lỗi, ngược lại SUCCESS. errorCode lấy từ
BOT_TINHTRANGTRASOAT, errorDetail từ BOT_GHICHU. Cô lập lỗi theo khách hàng.
"""
from __future__ import annotations

from dataclasses import dataclass

from robot.models import StrRecord

STATUS_SUCCESS = "Thành công"
STATUS_FAIL = "Lỗi"

# Các giá trị BOT_* biểu thị lỗi.
_ERROR_MARKERS = ("ERROR", "LỖI", "LOI", "FAIL")


@dataclass
class ProcessingResult:
    """Một hàng trạng thái cho một CIF."""

    stt: int
    cif: str
    status: str
    error_code: str = ""
    error_detail: str = ""

    @property
    def is_fail(self) -> bool:
        return self.status == STATUS_FAIL


def _looks_like_error(value: str) -> bool:
    v = (value or "").upper()
    return any(marker in v for marker in _ERROR_MARKERS)


class ResultBuilder:
    """Dựng ProcessingResult từ StrRecord."""

    def build(self, record: StrRecord, stt: int) -> ProcessingResult:
        failed = record.processing_stopped or _looks_like_error(record.bot_almd) or _looks_like_error(
            record.bot_tinhtrangtrasoat
        )
        if failed:
            return ProcessingResult(
                stt=stt,
                cif=record.cif,
                status=STATUS_FAIL,
                error_code=record.bot_tinhtrangtrasoat or "ERROR",
                error_detail=record.bot_ghichu,
            )
        return ProcessingResult(stt=stt, cif=record.cif, status=STATUS_SUCCESS)

    def build_batch(self, records: list[StrRecord]) -> list[ProcessingResult]:
        """Dựng ProcessingResult cho cả lô, đánh STT theo thứ tự (BR5.1/5.5)."""
        return [self.build(record, i + 1) for i, record in enumerate(records)]
