"""Application settings, read from environment variables (no secrets involved)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    db_path: Path
    log_dir: Path
    host: str = "127.0.0.1"
    port: int = 8000

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Settings:
        env = os.environ if env is None else env
        data_dir = Path(env.get("ROBOT_OPS_DATA_DIR", "data"))
        try:
            port = int(env.get("ROBOT_OPS_PORT", "8000"))
        except ValueError as exc:
            raise ValueError("ROBOT_OPS_PORT must be an integer") from exc
        if not 1 <= port <= 65535:
            raise ValueError("ROBOT_OPS_PORT must be between 1 and 65535")
        return cls(
            db_path=Path(env.get("ROBOT_OPS_DB", str(data_dir / "robot_ops.db"))),
            log_dir=Path(env.get("ROBOT_OPS_LOG_DIR", str(data_dir / "logs"))),
            host=env.get("ROBOT_OPS_HOST", "127.0.0.1"),
            port=port,
        )
