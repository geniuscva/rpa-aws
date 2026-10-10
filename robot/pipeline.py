"""Hợp đồng pipeline: interface chung cho mỗi cấu phần U1..U5.

Mỗi cấu phần hiện thực PipelineStage.process(record, context) -> record.
Khi record.processing_stopped là True, cấu phần bỏ qua xử lý và trả nguyên record
(trừ cấu phần tổng hợp cuối U5).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from robot.config import Config
from robot.logging_setup import StructuredLogger
from robot.models import StrRecord


@dataclass
class StageContext:
    """Ngữ cảnh dùng chung truyền vào mỗi cấu phần."""

    config: Config
    logger: StructuredLogger


class PipelineStage(Protocol):
    """Interface mỗi cấu phần pipeline phải hiện thực."""

    name: str

    def process(self, record: StrRecord, context: StageContext) -> StrRecord:
        """Nhận record, xử lý, cập nhật cột của mình, trả record cho cấu phần sau."""
        ...


def run_pipeline(record: StrRecord, context: StageContext, stages: list[PipelineStage]) -> StrRecord:
    """Chạy record tuần tự qua các cấu phần. Cấu phần sau bỏ qua record đã dừng
    (trừ cấu phần cuối cùng, thường là tổng hợp/thông báo)."""
    last_index = len(stages) - 1
    for i, stage in enumerate(stages):
        if record.processing_stopped and i != last_index:
            context.logger.info(
                "Bỏ qua cấu phần do record đã dừng",
                stage=stage.name,
                cif=record.cif,
            )
            continue
        record = stage.process(record, context)
    return record
