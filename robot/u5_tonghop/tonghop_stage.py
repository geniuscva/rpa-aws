"""TongHopStage (U5): chặng cuối pipeline, chạy MỘT LẦN cho cả lô.

Tổng hợp trạng thái mọi CIF (gồm KH lỗi/dừng luồng — BR5.1/5.5), dựng file Excel
trạng thái (BR5.2), dựng + gửi một email lô kèm đính kèm (BR5.3/5.4). Lỗi gửi mail
→ ghi log, giữ nguyên report (BR5.3). Thông tin mail đọc từ config (BR5.7).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, Optional

from robot.models import StrRecord
from robot.pipeline import StageContext
from robot.u5_tonghop.email_sender import (
    EmailPort,
    EmailSender,
    MailConfig,
    build_status_email,
)
from robot.u5_tonghop.result_builder import ProcessingResult, ResultBuilder
from robot.u5_tonghop.status_report import BatchStatusReport

REPORT_FILENAME = "TrangThaiXuLyLo.xlsx"


@dataclass
class BatchResult:
    """Kết quả chạy U5 cho cả lô."""

    results: list[ProcessingResult]
    report_path: str
    sent: bool
    sent_at: str = ""
    error: str = ""
    success_count: int = 0
    fail_count: int = 0


class TongHopStage:
    """Cấu phần U5 trong pipeline (xử lý theo lô, không theo từng record)."""

    name = "U5-TongHopVaGuiMail"

    def __init__(
        self,
        email_port_factory: Callable[[StageContext], EmailPort],
        result_builder: Optional[ResultBuilder] = None,
        status_report: Optional[BatchStatusReport] = None,
    ) -> None:
        self._email_port_factory = email_port_factory
        self._results = result_builder or ResultBuilder()
        self._report = status_report or BatchStatusReport()

    def process_batch(self, records: list[StrRecord], context: StageContext) -> BatchResult:
        logger = context.logger

        # BR5.1/5.5: tổng hợp trạng thái mọi CIF (cô lập lỗi theo khách hàng).
        results = self._results.build_batch(records)
        success = sum(1 for r in results if not r.is_fail)
        fail = sum(1 for r in results if r.is_fail)

        # BR5.2: dựng file Excel trạng thái.
        report_path = os.path.join(context.config.output_root, REPORT_FILENAME)
        self._report.write(results, report_path)
        logger.info("Đã dựng báo cáo trạng thái lô", path=report_path,
                    success=success, fail=fail)

        # BR5.3/5.4: dựng + gửi một email lô. To = người lập báo cáo (lấy từ record
        # đầu có email; cả lô cùng người lập trong phạm vi một lô).
        mail_cfg = self._mail_config(context)
        to = self._report_author_email(records)
        email = build_status_email(mail_cfg, to=to, attachment_path=report_path)
        sender = EmailSender(self._email_port_factory(context), logger)
        send = sender.send(email)

        return BatchResult(
            results=results,
            report_path=report_path,
            sent=send.ok,
            sent_at=send.sent_at,
            error=send.error,
            success_count=success,
            fail_count=fail,
        )

    @staticmethod
    def _report_author_email(records: list[StrRecord]) -> str:
        for r in records:
            if r.email_nguoi_lap_bao_cao:
                return r.email_nguoi_lap_bao_cao
        return ""

    @staticmethod
    def _mail_config(context: StageContext) -> MailConfig:
        cfg = getattr(context.config, "mail", None)
        if cfg is None:
            return MailConfig()
        return MailConfig(
            sender=getattr(cfg, "sender", ""),
            cc=list(getattr(cfg, "cc", []) or []),
            host=getattr(cfg, "host", ""),
            port=int(getattr(cfg, "port", 25)),
            username=getattr(cfg, "username", ""),
            password=getattr(cfg, "password", ""),
        )
