"""AccuityStage (U2): tra cứu Accuity cho một CIF, cập nhật StrRecord.BOT_ACCUITY.

Độc lập với U3. Chỉ ghi cột BOT_ACCUITY (và BOT_GHICHU khi lỗi).
"""
from __future__ import annotations

import os
from typing import Callable

from robot.models import StrRecord
from robot.pipeline import StageContext
from robot.u2_accuity.accuity_adapter import AccuityClient, AccuityError, AccuityPort


class AccuityStage:
    """Cấu phần U2 trong pipeline."""

    name = "U2-DataEntryAccuity"

    def __init__(self, port_factory: Callable[[StageContext], AccuityPort]) -> None:
        # port_factory(context) -> AccuityPort (cho phép mock trong test)
        self._port_factory = port_factory

    def process(self, record: StrRecord, context: StageContext) -> StrRecord:
        if record.processing_stopped:
            return record

        logger = context.logger
        output_dir = os.path.join(context.config.output_root, record.cif)
        port = self._port_factory(context)
        client = AccuityClient(port, logger, output_dir)

        name = record.ten_khach_hang or record.cif
        try:
            result = client.lookup_customer(record.loai_khach_hang, name)
            record.dossier_pdf_paths = list(record.dossier_pdf_paths) + result.pdf_paths
            record.bot_accuity = f"OK (match={result.match_score})"
            record.written_by = self.name
            logger.info("U2 hoàn tất", cif=record.cif, match=result.match_score)
        except AccuityError as exc:
            logger.error("Lỗi tra cứu Accuity", cif=record.cif, error=str(exc))
            record.bot_accuity = "ERROR"
            record.stop(self.name, f"Loi Accuity: {exc}")
        finally:
            if hasattr(port, 'close'):
                port.close()
        return record
