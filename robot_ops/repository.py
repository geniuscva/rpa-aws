"""Data access for robots, runs and alerts."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any

from .db import Database

RUN_STATUSES = ("running", "success", "error", "stopped")


class RobotNotFoundError(LookupError):
    pass


class DuplicateRobotError(ValueError):
    pass


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def robot_status(last_run_status: str | None) -> str:
    """Derive the robot status from its latest run: running | error | stopped."""
    if last_run_status == "running":
        return "running"
    if last_run_status == "error":
        return "error"
    return "stopped"


class Repository:
    def __init__(self, db: Database):
        self.db = db

    # ---- robots -------------------------------------------------------------------------

    _ROBOT_SELECT = """
        SELECT r.*,
               (SELECT status FROM runs WHERE robot_id = r.id ORDER BY id DESC LIMIT 1)
                   AS last_status,
               (SELECT started_at FROM runs WHERE robot_id = r.id ORDER BY id DESC LIMIT 1)
                   AS last_started_at
        FROM robots r
    """

    @staticmethod
    def _robot_dict(row: sqlite3.Row) -> dict[str, Any]:
        d = dict(row)
        d["status"] = robot_status(d.pop("last_status"))
        return d

    def create_robot(self, name: str, workdir: str, command: str, schedule: str | None) -> dict:
        with self.db.lock:
            try:
                cur = self.db.conn.execute(
                    "INSERT INTO robots (name, workdir, command, schedule, created_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (name, workdir, command, schedule, _now()),
                )
                self.db.conn.commit()
            except sqlite3.IntegrityError as exc:
                self.db.conn.rollback()
                raise DuplicateRobotError(f"Robot name already exists: {name}") from exc
            return self.get_robot(int(cur.lastrowid))

    def get_robot(self, robot_id: int) -> dict:
        with self.db.lock:
            row = self.db.conn.execute(
                self._ROBOT_SELECT + " WHERE r.id = ?", (robot_id,)
            ).fetchone()
        if row is None:
            raise RobotNotFoundError(f"Robot {robot_id} not found")
        return self._robot_dict(row)

    def list_robots(self) -> list[dict]:
        with self.db.lock:
            rows = self.db.conn.execute(self._ROBOT_SELECT + " ORDER BY r.name").fetchall()
        return [self._robot_dict(r) for r in rows]

    def update_robot(
        self, robot_id: int, name: str, workdir: str, command: str, schedule: str | None
    ) -> dict:
        self.get_robot(robot_id)
        with self.db.lock:
            try:
                self.db.conn.execute(
                    "UPDATE robots SET name = ?, workdir = ?, command = ?, schedule = ? "
                    "WHERE id = ?",
                    (name, workdir, command, schedule, robot_id),
                )
                self.db.conn.commit()
            except sqlite3.IntegrityError as exc:
                self.db.conn.rollback()
                raise DuplicateRobotError(f"Robot name already exists: {name}") from exc
        return self.get_robot(robot_id)

    def delete_robot(self, robot_id: int) -> None:
        self.get_robot(robot_id)
        with self.db.lock:
            self.db.conn.execute("DELETE FROM robots WHERE id = ?", (robot_id,))
            self.db.conn.commit()

    # ---- runs ---------------------------------------------------------------------------

    def create_run(self, robot_id: int, log_path: str | None = None) -> int:
        with self.db.lock:
            cur = self.db.conn.execute(
                "INSERT INTO runs (robot_id, started_at, status, log_path) "
                "VALUES (?, ?, 'running', ?)",
                (robot_id, _now(), log_path),
            )
            self.db.conn.commit()
            return int(cur.lastrowid)

    def set_run_log_path(self, run_id: int, log_path: str) -> None:
        with self.db.lock:
            self.db.conn.execute("UPDATE runs SET log_path = ? WHERE id = ?", (log_path, run_id))
            self.db.conn.commit()

    def finish_run(self, run_id: int, status: str, exit_code: int | None) -> None:
        if status not in RUN_STATUSES or status == "running":
            raise ValueError(f"Invalid final run status: {status}")
        with self.db.lock:
            self.db.conn.execute(
                "UPDATE runs SET status = ?, exit_code = ?, ended_at = ? WHERE id = ?",
                (status, exit_code, _now(), run_id),
            )
            self.db.conn.commit()

    def get_run(self, run_id: int) -> dict | None:
        with self.db.lock:
            row = self.db.conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        return dict(row) if row else None

    def get_open_run(self, robot_id: int) -> dict | None:
        with self.db.lock:
            row = self.db.conn.execute(
                "SELECT * FROM runs WHERE robot_id = ? AND status = 'running' "
                "ORDER BY id DESC LIMIT 1",
                (robot_id,),
            ).fetchone()
        return dict(row) if row else None

    def list_runs(self, robot_id: int, page: int = 1, page_size: int = 20) -> dict:
        self.get_robot(robot_id)
        page = max(page, 1)
        page_size = max(page_size, 1)
        with self.db.lock:
            total = self.db.conn.execute(
                "SELECT COUNT(*) FROM runs WHERE robot_id = ?", (robot_id,)
            ).fetchone()[0]
            rows = self.db.conn.execute(
                "SELECT * FROM runs WHERE robot_id = ? ORDER BY id DESC LIMIT ? OFFSET ?",
                (robot_id, page_size, (page - 1) * page_size),
            ).fetchall()
        return {
            "items": [dict(r) for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def has_run_started_since(self, robot_id: int, since_iso: str) -> bool:
        with self.db.lock:
            row = self.db.conn.execute(
                "SELECT 1 FROM runs WHERE robot_id = ? AND started_at >= ? LIMIT 1",
                (robot_id, since_iso),
            ).fetchone()
        return row is not None

    # ---- alerts -------------------------------------------------------------------------

    def create_alert(
        self,
        robot_id: int,
        kind: str,
        message: str,
        run_id: int | None = None,
        schedule_date: str | None = None,
    ) -> int:
        with self.db.lock:
            cur = self.db.conn.execute(
                "INSERT INTO alerts (robot_id, run_id, kind, message, schedule_date, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (robot_id, run_id, kind, message, schedule_date, _now()),
            )
            self.db.conn.commit()
            return int(cur.lastrowid)

    def has_alert(self, robot_id: int, kind: str, schedule_date: str) -> bool:
        with self.db.lock:
            row = self.db.conn.execute(
                "SELECT 1 FROM alerts WHERE robot_id = ? AND kind = ? AND schedule_date = ? "
                "LIMIT 1",
                (robot_id, kind, schedule_date),
            ).fetchone()
        return row is not None

    def list_alerts(self, include_resolved: bool = False, limit: int = 200) -> list[dict]:
        sql = (
            "SELECT a.*, r.name AS robot_name FROM alerts a " "JOIN robots r ON r.id = a.robot_id "
        )
        if not include_resolved:
            sql += "WHERE a.resolved_at IS NULL "
        sql += "ORDER BY a.id DESC LIMIT ?"
        with self.db.lock:
            rows = self.db.conn.execute(sql, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def resolve_alert(self, alert_id: int) -> dict:
        with self.db.lock:
            cur = self.db.conn.execute(
                "UPDATE alerts SET resolved_at = COALESCE(resolved_at, ?) WHERE id = ?",
                (_now(), alert_id),
            )
            self.db.conn.commit()
            if cur.rowcount == 0:
                raise LookupError(f"Alert {alert_id} not found")
            row = self.db.conn.execute(
                "SELECT a.*, r.name AS robot_name FROM alerts a "
                "JOIN robots r ON r.id = a.robot_id WHERE a.id = ?",
                (alert_id,),
            ).fetchone()
        return dict(row)
