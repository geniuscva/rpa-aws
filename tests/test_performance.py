"""NFR1: the robot list loads in under 2 seconds with 50 robots and 10,000 history records."""

from __future__ import annotations

import time

ROBOTS = 50
RUNS_PER_ROBOT = 200  # 50 * 200 = 10,000 run records
LIMIT_SECONDS = 2.0


def test_robot_list_and_history_are_fast_with_large_data(client):
    repo = client.app.state.repo
    robot_ids = [repo.create_robot(f"bot-{i}", ".", "echo hi", None)["id"] for i in range(ROBOTS)]
    rows = [
        (rid, "2026-01-01T00:00:00", "2026-01-01T00:01:00", "success", 0)
        for rid in robot_ids
        for _ in range(RUNS_PER_ROBOT)
    ]
    with repo.db.lock:  # bulk insert in one transaction; per-row commits would dominate the test
        repo.db.conn.executemany(
            "INSERT INTO runs (robot_id, started_at, ended_at, status, exit_code) "
            "VALUES (?, ?, ?, ?, ?)",
            rows,
        )
        repo.db.conn.commit()

    start = time.perf_counter()
    response = client.get("/api/robots")
    list_elapsed = time.perf_counter() - start
    assert response.status_code == 200
    assert len(response.json()) == ROBOTS
    assert list_elapsed < LIMIT_SECONDS

    start = time.perf_counter()
    history = client.get("/api/robots/1/runs", params={"page": 1, "page_size": 20})
    history_elapsed = time.perf_counter() - start
    assert history.status_code == 200
    assert history_elapsed < LIMIT_SECONDS
