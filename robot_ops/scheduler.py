"""Detect robots that missed their expected daily schedule time."""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timedelta

from .repository import Repository

logger = logging.getLogger("robot_ops.scheduler")

GRACE = timedelta(minutes=5)


def check_missed_schedules(
    repo: Repository, now: datetime | None = None, grace: timedelta = GRACE
) -> list[int]:
    """Create a 'missed_schedule' alert for every robot whose scheduled time today passed by more
    than `grace` without a run starting. Returns the ids of the created alerts."""
    now = now or datetime.now()
    created: list[int] = []
    today = now.date().isoformat()
    for robot in repo.list_robots():
        schedule = robot.get("schedule")
        if not schedule:
            continue
        try:
            hour, minute = (int(x) for x in schedule.split(":"))
            due = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        except ValueError:
            logger.warning("Robot %s has invalid schedule %r", robot["name"], schedule)
            continue
        if now < due + grace:
            continue
        # a robot declared after the due time cannot have missed it
        if robot["created_at"] > due.isoformat(timespec="seconds"):
            continue
        if repo.has_run_started_since(robot["id"], due.isoformat(timespec="seconds")):
            continue
        if repo.has_alert(robot["id"], "missed_schedule", today):
            continue
        created.append(
            repo.create_alert(
                robot["id"],
                "missed_schedule",
                f"Robot '{robot['name']}' did not run on schedule ({schedule})",
                schedule_date=today,
            )
        )
        logger.warning("Missed schedule alert for robot %s (%s)", robot["name"], schedule)
    return created


class SchedulerThread(threading.Thread):
    """Background loop calling check_missed_schedules periodically."""

    def __init__(self, repo: Repository, interval: float = 30.0):
        super().__init__(daemon=True, name="robot-scheduler")
        self.repo = repo
        self.interval = interval
        self._stop_event = threading.Event()

    def run(self) -> None:
        while not self._stop_event.is_set():
            try:
                check_missed_schedules(self.repo)
            except Exception:
                logger.exception("Schedule check failed")
            self._stop_event.wait(self.interval)

    def stop(self) -> None:
        self._stop_event.set()
