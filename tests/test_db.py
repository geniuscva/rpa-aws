from __future__ import annotations

from robot_ops.db import Database


def _insert_robot(db: Database, name: str = "bot") -> int:
    with db.lock:
        cur = db.conn.execute(
            "INSERT INTO robots (name, workdir, command, created_at) VALUES (?, '.', 'x', 't')",
            (name,),
        )
        db.conn.commit()
        return int(cur.lastrowid)


def test_data_persists_after_reopen(tmp_path):
    path = tmp_path / "x.db"
    db = Database(path)
    _insert_robot(db, "persisted")
    db.close()

    db2 = Database(path)
    row = db2.conn.execute("SELECT name FROM robots").fetchone()
    assert row["name"] == "persisted"
    db2.close()


def test_unfinished_runs_marked_stopped_on_startup(tmp_path):
    path = tmp_path / "x.db"
    db = Database(path)
    rid = _insert_robot(db)
    with db.lock:
        db.conn.execute(
            "INSERT INTO runs (robot_id, started_at, status) VALUES (?, 't', 'running')", (rid,)
        )
        db.conn.commit()
    db.close()

    db2 = Database(path)
    row = db2.conn.execute("SELECT status, ended_at FROM runs").fetchone()
    assert db2.recovered_runs == 1
    assert row["status"] == "stopped"
    assert row["ended_at"] is not None
    db2.close()
