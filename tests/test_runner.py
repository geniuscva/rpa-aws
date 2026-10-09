from __future__ import annotations

import sys
import time

import pytest

from robot_ops.db import Database
from robot_ops.repository import Repository
from robot_ops.runner import AlreadyRunningError, Runner, StartError


def py(code: str) -> str:
    """Shell command running a tiny Python program (use single quotes inside `code`)."""
    return f'"{sys.executable}" -c "{code}"'


@pytest.fixture()
def env(tmp_path):
    db = Database(tmp_path / "r.db")
    repo = Repository(db)
    runner = Runner(repo, tmp_path / "logs")
    yield repo, runner, tmp_path
    runner.shutdown()
    db.close()


def _robot(repo, tmp_path, command, workdir=None):
    return repo.create_robot("bot", str(workdir or tmp_path), command, None)


def test_successful_run_records_history_and_log(env):
    repo, runner, tmp_path = env
    robot = _robot(repo, tmp_path, py("print('hello robot')"))
    run = runner.start(robot["id"])
    runner.wait_for_run(run["id"])
    done = repo.get_run(run["id"])
    assert done["status"] == "success" and done["exit_code"] == 0
    assert done["ended_at"] is not None
    assert "hello robot" in runner.read_log(run["id"])
    assert repo.list_alerts() == []


def test_failed_run_creates_alert(env):
    repo, runner, tmp_path = env
    robot = _robot(repo, tmp_path, py("import sys; print('bad'); sys.exit(3)"))
    run = runner.start(robot["id"])
    runner.wait_for_run(run["id"])
    done = repo.get_run(run["id"])
    assert done["status"] == "error" and done["exit_code"] == 3
    assert repo.get_robot(robot["id"])["status"] == "error"
    alerts = repo.list_alerts()
    assert len(alerts) == 1 and alerts[0]["kind"] == "run_error"


def test_duplicate_start_is_blocked_and_stop_kills_process(env):
    repo, runner, tmp_path = env
    robot = _robot(repo, tmp_path, py("import time; print('up', flush=True); time.sleep(60)"))
    run = runner.start(robot["id"])
    assert repo.get_robot(robot["id"])["status"] == "running"
    with pytest.raises(AlreadyRunningError):
        runner.start(robot["id"])
    time.sleep(0.5)
    started = time.time()
    stopped = runner.stop(robot["id"])
    assert time.time() - started < 15
    assert stopped["status"] == "stopped" and stopped["id"] == run["id"]
    assert repo.get_robot(robot["id"])["status"] == "stopped"
    assert repo.list_alerts() == []  # a manual stop is not an error
    assert runner.stop(robot["id"]) is None  # nothing running any more


def test_start_failure_is_reported_not_raised_as_crash(env):
    repo, runner, tmp_path = env
    robot = _robot(repo, tmp_path, "x", workdir=tmp_path / "missing_dir")
    with pytest.raises(StartError):
        runner.start(robot["id"])
    assert runner.start_failures == 1
    assert repo.get_robot(robot["id"])["status"] == "error"
    assert len(repo.list_alerts()) == 1
    # the application keeps working: another robot still runs
    ok = repo.create_robot("ok", str(tmp_path), py("print(1)"), None)
    run = runner.start(ok["id"])
    runner.wait_for_run(run["id"])
    assert repo.get_run(run["id"])["status"] == "success"


def test_unknown_command_exits_with_error(env):
    repo, runner, tmp_path = env
    robot = _robot(repo, tmp_path, "this_command_does_not_exist_12345")
    run = runner.start(robot["id"])
    runner.wait_for_run(run["id"])
    done = repo.get_run(run["id"])
    assert done["status"] == "error" and done["exit_code"] != 0
