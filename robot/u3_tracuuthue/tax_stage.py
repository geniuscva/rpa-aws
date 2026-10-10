"""TaxAuthorityStage (U3): tra cứu Cục Thuế cho một CIF, cập nhật
StrRecord.BOT_TRACUUTHE.

Chỉ tra cứu khi KHDN (BR3.2); KHCN hoặc không có kết quả → BOT_TRACUUTHE=SKIPPED
(BR3.4); có kết quả → in PDF + OK (BR3.4); lỗi/captcha fail → dừng record (BR3.6).
Độc lập với U2. Chỉ ghi cột BOT_TRACUUTHE (và BOT_GHICHU khi lỗi).
"""
from __future__ import annotations

import os
from typing import Callable, Optional

from robot.models import CustomerType, StrRecord
from robot.pipeline import StageContext
from robot.u3_tracuuthue.captcha_solver import CaptchaSolver
from robot.u3_tracuuthue.tax_authority_adapter import (
    TaxAuthorityClient,
    TaxAuthorityError,
    TaxAuthorityPort,
)

RESULT_OK = "OK"
RESULT_SKIPPED = "SKIPPED"
RESULT_ERROR = "ERROR"


class TaxAuthorityStage:
    """Cấu phần U3 trong pipeline."""

    name = "U3-DataEntryTraCuuThue"

    def __init__(
        self,
        port_factory: Callable[[StageContext], TaxAuthorityPort],
        captcha_solver_factory: Optional[Callable[[StageContext], CaptchaSolver]] = None,
    ) -> None:
        # port_factory(context) -> TaxAuthorityPort (cho phép mock trong test).
        self._port_factory = port_factory
        self._captcha_solver_factory = captcha_solver_factory or (lambda ctx: CaptchaSolver())

    def process(self, record: StrRecord, context: StageContext) -> StrRecord:
        # BR3.1: bỏ qua record đã dừng.
        if record.processing_stopped:
            return record

        logger = context.logger

        # BR3.2: chỉ tra cứu khi KHDN; KHCN → SKIPPED.
        if record.loai_khach_hang == CustomerType.KHCN.value:
            record.bot_tracuuthe = RESULT_SKIPPED
            record.written_by = self.name
            logger.info("U3 bỏ qua (KHCN)", cif=record.cif)
            return record

        # KHDN: cần mã số thuế (BR3.2 → lỗi khi rỗng, BR3.6).
        tax_code = (record.ma_so_thue or "").strip()
        if not tax_code:
            record.bot_tracuuthe = RESULT_ERROR
            record.stop(self.name, "Thiếu mã số thuế (KHDN) để tra cứu Cục Thuế")
            logger.error("U3 lỗi: KHDN thiếu MST", cif=record.cif)
            return record

        output_dir = os.path.join(context.config.output_root, record.cif)
        port = self._port_factory(context)
        captcha_solver = self._captcha_solver_factory(context)
        client = TaxAuthorityClient(port, captcha_solver, logger, output_dir)

        try:
            result = client.lookup(tax_code)
        except TaxAuthorityError as exc:
            # BR3.6: lỗi tra cứu → dừng record.
            record.bot_tracuuthe = RESULT_ERROR
            record.stop(self.name, f"Loi tra cuu Cuc Thue: {exc}")
            logger.error("U3 lỗi tra cứu Cục Thuế", cif=record.cif, error=str(exc))
            return record
        finally:
            if hasattr(port, 'close'):
                port.close()

        if result.found:
            # BR3.4: có kết quả → in PDF, OK.
            if result.pdf_path:
                record.dossier_pdf_paths = list(record.dossier_pdf_paths) + [result.pdf_path]
            record.bot_tracuuthe = RESULT_OK
        else:
            # BR3.4: không có kết quả → SKIPPED (không coi là lỗi).
            record.bot_tracuuthe = RESULT_SKIPPED

        record.written_by = self.name
        logger.info("U3 hoàn tất", cif=record.cif, bot_tracuuthe=record.bot_tracuuthe)
        return record
