"""SQLite access: connection, schema creation and startup recovery."""

from __future__ import annotations

import logging
import sqlite3
import threading
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("robot_ops.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS robots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    workdir TEXT NOT NULL,
    command TEXT NOT NULL,
    schedule TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    robot_id INTEGER NOT NULL REFERENCES robots(id) ON DELETE CASCADE,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    status TEXT NOT NULL CHECK (status IN ('running', 'success', 'error', 'stopped')),
    exit_code INTEGER,
    log_path TEXT
);
CREATE INDEX IF NOT EXISTS idx_runs_robot ON runs(robot_id, id DESC);
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    robot_id INTEGER NOT NULL REFERENCES robots(id) ON DELETE CASCADE,
    run_id INTEGER REFERENCES runs(id) ON DELETE SET NULL,
    kind TEXT NOT NULL CHECK (kind IN ('run_error', 'missed_schedule')),
    message TEXT NOT NULL,
    schedule_date TEXT,
    created_at TEXT NOT NULL,
    resolved_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_alerts_open ON alerts(resolved_at, id DESC);
"""


class Database:
    """Thin wrapper around one shared SQLite connection guarded by a lock."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(self.path, check_same_thread=False)
        except (OSError, sqlite3.Error):
            logger.exception("Cannot open database at %s", self.path)
            raise
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.lock = threading.RLock()
        with self.lock:
            self.conn.executescript(SCHEMA)
            self.conn.commit()
        self.recovered_runs = self._recover_stale_runs()

    def _recover_stale_runs(self) -> int:
        """Mark runs left open by a previous process as stopped (NFR3)."""
        now = datetime.now().isoformat(timespec="seconds")
        with self.lock:
            cur = self.conn.execute(
                "UPDATE runs SET status = 'stopped', ended_at = ? WHERE status = 'running'",
                (now,),
            )
            self.conn.commit()
        if cur.rowcount:
            logger.warning("Marked %d unfinished run(s) as stopped on startup", cur.rowcount)
        return cur.rowcount

    def close(self) -> None:
        with self.lock:
            self.conn.close()
