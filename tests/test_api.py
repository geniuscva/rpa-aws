from __future__ import annotations

import sys
import time

from robot_ops.config import Settings


def _py(code: str) -> str:
    return f'"{sys.executable}" -c "{code}"'


def _create(client, tmp_path, name="bot", command=None, schedule=None):
    body = {
        "name": name,
        "workdir": str(tmp_path),
        "command": command or _py("print('api ok')"),
        "schedule": schedule,
    }
    return client.post("/api/robots", json=body)


def _wait_status(client, robot_id, wanted, timeout=15):
    end = time.time() + timeout
    while time.time() < end:
        status = client.get(f"/api/robots/{robot_id}").json()["status"]
        if status == wanted:
            return status
        time.sleep(0.1)
    return status


def test_full_flow_declare_run_history_log_alert(client, tmp_path):
    created = _create(client, tmp_path, command=_py("import sys; print('boom'); sys.exit(2)"))
    assert created.status_code == 201
    rid = created.json()["id"]
    assert client.get("/api/robots").json()[0]["status"] == "stopped"

    started = client.post(f"/api/robots/{rid}/start")
    assert started.status_code == 200
    assert _wait_status(client, rid, "error") == "error"

    runs = client.get(f"/api/robots/{rid}/runs?page=1&page_size=10").json()
    assert runs["total"] == 1 and runs["items"][0]["exit_code"] == 2
    log = client.get(f"/api/runs/{runs['items'][0]['id']}/log").json()["log"]
    assert "boom" in log

    alerts = client.get("/api/alerts").json()
    assert len(alerts) == 1 and alerts[0]["robot_name"] == "bot"
    assert client.post(f"/api/alerts/{alerts[0]['id']}/resolve").status_code == 200
    assert client.get("/api/alerts").json() == []


def test_start_stop_and_duplicate_start(client, tmp_path):
    rid = _create(client, tmp_path, command=_py("import time; time.sleep(60)")).json()["id"]
    assert client.post(f"/api/robots/{rid}/start").status_code == 200
    dup = client.post(f"/api/robots/{rid}/start")
    assert dup.status_code == 409 and "already running" in dup.json()["detail"]
    assert client.delete(f"/api/robots/{rid}").status_code == 409
    stopped = client.post(f"/api/robots/{rid}/stop")
    assert stopped.status_code == 200 and stopped.json()["status"] == "stopped"
    assert client.post(f"/api/robots/{rid}/stop").status_code == 409


def test_update_delete_and_not_found(client, tmp_path):
    rid = _create(client, tmp_path).json()["id"]
    body = {"name": "renamed", "workdir": str(tmp_path), "command": "x", "schedule": "07:30"}
    updated = client.put(f"/api/robots/{rid}", json=body).json()
    assert updated["name"] == "renamed" and updated["schedule"] == "07:30"
    assert client.delete(f"/api/robots/{rid}").status_code == 204
    assert client.get(f"/api/robots/{rid}").status_code == 404
    assert client.post("/api/robots/999/start").status_code == 404
    assert client.get("/api/runs/999/log").status_code == 404
    assert client.post("/api/alerts/999/resolve").status_code == 404


def test_invalid_input_returns_422_and_duplicate_name_409(client, tmp_path):
    blank = {"name": "", "workdir": "x", "command": "y"}
    assert client.post("/api/robots", json=blank).status_code == 422
    bad_schedule = {"name": "a", "workdir": "x", "command": "y", "schedule": "25:99"}
    assert client.post("/api/robots", json=bad_schedule).status_code == 422
    assert client.post("/api/robots", json={"name": "a"}).status_code == 422
    assert _create(client, tmp_path, name="dup").status_code == 201
    assert _create(client, tmp_path, name="dup").status_code == 409


def test_bad_workdir_returns_400_and_counts_in_health(client, tmp_path):
    body = {"name": "bad", "workdir": str(tmp_path / "nope"), "command": "x"}
    rid = client.post("/api/robots", json=body).json()["id"]
    resp = client.post(f"/api/robots/{rid}/start")
    assert resp.status_code == 400 and "does not exist" in resp.json()["detail"]
    health = client.get("/health").json()
    assert health["status"] == "ok" and health["start_failures"] == 1
    assert health["robots"] == 1


def test_default_bind_is_localhost_only():
    settings = Settings.from_env({})
    assert settings.host == "127.0.0.1" and settings.port == 8000
