from __future__ import annotations

from datetime import datetime

import pytest

from robot_ops.db import Database
from robot_ops.repository import Repository
from robot_ops.scheduler import check_missed_schedules


@pytest.fixture()
def repo(tmp_path):
    db = Database(tmp_path / "s.db")
    yield Repository(db)
    db.close()


def _make_robot(repo, schedule="08:00"):
    robot = repo.create_robot("bot", "w", "c", schedule)
    # pretend the robot was declared yesterday so that today's schedule applies
    with repo.db.lock:
        repo.db.conn.execute(
            "UPDATE robots SET created_at = '2000-01-01T00:00:00' WHERE id = ?", (robot["id"],)
        )
        repo.db.conn.commit()
    return robot


def test_missed_schedule_creates_one_alert(repo):
    robot = _make_robot(repo)
    now = datetime(2030, 1, 1, 8, 6, 0)
    created = check_missed_schedules(repo, now=now)
    assert len(created) == 1
    alert = repo.list_alerts()[0]
    assert alert["kind"] == "missed_schedule" and alert["robot_id"] == robot["id"]
    assert check_missed_schedules(repo, now=datetime(2030, 1, 1, 9, 0, 0)) == []  # no duplicate


def test_no_alert_within_grace_or_without_schedule(repo):
    _make_robot(repo)
    repo.create_robot("manual", "w", "c", None)
    assert check_missed_schedules(repo, now=datetime(2030, 1, 1, 8, 4, 59)) == []
    assert repo.list_alerts() == []


def test_no_alert_when_robot_started_on_time(repo):
    robot = _make_robot(repo)
    with repo.db.lock:
        repo.db.conn.execute(
            "INSERT INTO runs (robot_id, started_at, status) VALUES (?, '2030-01-01T08:01:00', "
            "'success')",
            (robot["id"],),
        )
        repo.db.conn.commit()
    assert check_missed_schedules(repo, now=datetime(2030, 1, 1, 9, 0, 0)) == []
