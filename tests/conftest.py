from __future__ import annotations

import pytest


@pytest.fixture()
def client(tmp_path):
    """Test client backed by a temporary DB and log directory (scheduler thread disabled)."""
    from fastapi.testclient import TestClient

    from robot_ops.main import create_app

    app = create_app(db_path=tmp_path / "test.db", log_dir=tmp_path / "logs", start_scheduler=False)
    with TestClient(app) as c:
        yield c
