"""IdempotencyStore: chống trùng message theo eventID (BR1.2, REL-U1-3).

Lưu các eventID đã xử lý trong file JSON đơn giản. Trước khi xử lý, kiểm tra
eventID; sau khi xử lý xong, đánh dấu đã xử lý.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone


class IdempotencyStore:
    """Lưu eventID đã xử lý để bỏ qua message trùng."""

    def __init__(self, store_path: str) -> None:
        self.store_path = store_path
        directory = os.path.dirname(store_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        self._seen: dict[str, str] = self._load()

    def _load(self) -> dict[str, str]:
        if not os.path.isfile(self.store_path):
            return {}
        try:
            with open(self.store_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}

    def is_processed(self, event_id: str) -> bool:
        return event_id in self._seen

    def mark_processed(self, event_id: str) -> None:
        self._seen[event_id] = datetime.now(timezone.utc).isoformat()
        with open(self.store_path, "w", encoding="utf-8") as fh:
            json.dump(self._seen, fh, ensure_ascii=False, indent=2)
