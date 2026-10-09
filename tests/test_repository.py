from __future__ import annotations

import pytest

from robot_ops.db import Database
from robot_ops.repository import DuplicateRobotError, Repository, RobotNotFoundError


@pytest.fixture()
def repo(tmp_path):
    db = Database(tmp_path / "r.db")
    yield Repository(db)
    db.close()


def test_robot_crud(repo):
    r = repo.create_robot("A", "C:/w", "run.bat", "08:00")
    assert r["status"] == "stopped" and r["schedule"] == "08:00"
    updated = repo.update_robot(r["id"], "A2", "C:/w2", "go.bat", None)
    assert updated["name"] == "A2" and updated["schedule"] is None
    assert [x["name"] for x in repo.list_robots()] == ["A2"]
    repo.delete_robot(r["id"])
    assert repo.list_robots() == []


def test_duplicate_and_missing_robot(repo):
    repo.create_robot("A", "w", "c", None)
    with pytest.raises(DuplicateRobotError):
        repo.create_robot("A", "w", "c", None)
    with pytest.raises(RobotNotFoundError):
        repo.get_robot(999)


def test_derived_status(repo):
    r = repo.create_robot("A", "w", "c", None)
    run1 = repo.create_run(r["id"])
    assert repo.get_robot(r["id"])["status"] == "running"
    repo.finish_run(run1, "error", 1)
    assert repo.get_robot(r["id"])["status"] == "error"
    run2 = repo.create_run(r["id"])
    repo.finish_run(run2, "success", 0)
    assert repo.get_robot(r["id"])["status"] == "stopped"


def test_history_pagination_newest_first(repo):
    r = repo.create_robot("A", "w", "c", None)
    ids = []
    for _ in range(5):
        run = repo.create_run(r["id"])
        repo.finish_run(run, "success", 0)
        ids.append(run)
    page1 = repo.list_runs(r["id"], page=1, page_size=2)
    page3 = repo.list_runs(r["id"], page=3, page_size=2)
    assert page1["total"] == 5
    assert [x["id"] for x in page1["items"]] == [ids[4], ids[3]]
    assert [x["id"] for x in page3["items"]] == [ids[0]]


def test_alert_resolve(repo):
    r = repo.create_robot("A", "w", "c", None)
    aid = repo.create_alert(r["id"], "run_error", "boom")
    assert len(repo.list_alerts()) == 1
    resolved = repo.resolve_alert(aid)
    assert resolved["resolved_at"] is not None
    assert repo.list_alerts() == []
    assert len(repo.list_alerts(include_resolved=True)) == 1
    with pytest.raises(LookupError):
        repo.resolve_alert(12345)
