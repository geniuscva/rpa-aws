"""Log có cấu trúc dạng JSON lines: mỗi dòng gồm Thời gian / Log Level / Message.

Không ghi giá trị secret. Dùng cho toàn bộ pipeline.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Optional


class StructuredLogger:
    """Ghi log JSON lines ra file và (tùy chọn) stdout."""

    LEVELS = {"DEBUG": 10, "INFO": 20, "ERROR": 40}

    def __init__(self, file_path: str, level: str = "INFO", echo_stdout: bool = True) -> None:
        self.file_path = file_path
        self.level = level.upper()
        self._threshold = self.LEVELS.get(self.level, 20)
        self.echo_stdout = echo_stdout
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def _write(self, level: str, message: str, extra: Optional[dict[str, Any]] = None) -> None:
        if self.LEVELS.get(level, 20) < self._threshold:
            return
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
        }
        if extra:
            record.update(extra)
        line = json.dumps(record, ensure_ascii=False)
        with open(self.file_path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        if self.echo_stdout:
            print(line)

    def info(self, message: str, **extra: Any) -> None:
        self._write("INFO", message, extra or None)

    def error(self, message: str, **extra: Any) -> None:
        self._write("ERROR", message, extra or None)

    def warning(self, message: str, **extra: Any) -> None:
        self._write("WARNING", message, extra or None)

    def debug(self, message: str, **extra: Any) -> None:
        self._write("DEBUG", message, extra or None)
