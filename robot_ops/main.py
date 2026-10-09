"""FastAPI application: REST API plus the single-page UI."""

from __future__ import annotations

import logging
import re
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator

from .config import Settings
from .db import Database
from .repository import DuplicateRobotError, Repository, RobotNotFoundError
from .runner import AlreadyRunningError, Runner, StartError
from .scheduler import SchedulerThread

STATIC_DIR = Path(__file__).parent / "static"
SCHEDULE_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
logger = logging.getLogger("robot_ops")


class RobotIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    workdir: str = Field(min_length=1, max_length=500)
    command: str = Field(min_length=1, max_length=1000)
    schedule: str | None = None  # daily time "HH:MM" (optional)

    @field_validator("name", "workdir", "command")
    @classmethod
    def _strip_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v

    @field_validator("schedule")
    @classmethod
    def _check_schedule(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        v = v.strip()
        if not SCHEDULE_RE.match(v):
            raise ValueError("schedule must be HH:MM (24h)")
        return v


def setup_logging(log_dir: Path) -> None:
    """Write the application's own log to <log_dir>/app.log (NFR4)."""
    log_dir.mkdir(parents=True, exist_ok=True)
    target = str((log_dir / "app.log").resolve())
    root = logging.getLogger("robot_ops")
    root.setLevel(logging.INFO)
    for h in root.handlers:
        if getattr(h, "baseFilename", None) == target:
            return
    handler = RotatingFileHandler(target, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    root.addHandler(handler)


def create_app(
    db_path: str | Path | None = None,
    log_dir: str | Path | None = None,
    start_scheduler: bool = True,
) -> FastAPI:
    settings = Settings.from_env()
    db_path = Path(db_path) if db_path else settings.db_path
    log_dir = Path(log_dir) if log_dir else settings.log_dir
    setup_logging(log_dir)

    db = Database(db_path)
    repo = Repository(db)
    runner = Runner(repo, log_dir / "runs")
    scheduler = SchedulerThread(repo) if start_scheduler else None

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if scheduler is not None:
            scheduler.start()
        logger.info("Robot Ops started (db=%s)", db_path)
        yield
        if scheduler is not None:
            scheduler.stop()
        runner.shutdown()
        logger.info("Robot Ops stopped")

    app = FastAPI(title="Robot Ops", lifespan=lifespan)
    app.state.repo = repo
    app.state.runner = runner

    @app.exception_handler(RobotNotFoundError)
    async def _not_found(_: Request, exc: RobotNotFoundError):
        return JSONResponse({"detail": str(exc)}, status_code=404)

    @app.exception_handler(DuplicateRobotError)
    async def _duplicate(_: Request, exc: DuplicateRobotError):
        return JSONResponse({"detail": str(exc)}, status_code=409)

    @app.exception_handler(AlreadyRunningError)
    async def _running(_: Request, exc: AlreadyRunningError):
        return JSONResponse({"detail": str(exc)}, status_code=409)

    @app.exception_handler(StartError)
    async def _start_error(_: Request, exc: StartError):
        return JSONResponse({"detail": str(exc)}, status_code=400)

    # ---- UI / health --------------------------------------------------------------------

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(STATIC_DIR / "index.html", media_type="text/html")

    @app.get("/health")
    def health():
        robots = repo.list_robots()
        return {
            "status": "ok",
            "robots": len(robots),
            "running": sum(1 for r in robots if r["status"] == "running"),
            "open_alerts": len(repo.list_alerts()),
            "start_failures": runner.start_failures,
        }

    # ---- robots -------------------------------------------------------------------------

    @app.get("/api/robots")
    def list_robots():
        return repo.list_robots()

    @app.post("/api/robots", status_code=201)
    def create_robot(body: RobotIn):
        return repo.create_robot(body.name, body.workdir, body.command, body.schedule)

    @app.get("/api/robots/{robot_id}")
    def get_robot(robot_id: int):
        return repo.get_robot(robot_id)

    @app.put("/api/robots/{robot_id}")
    def update_robot(robot_id: int, body: RobotIn):
        return repo.update_robot(robot_id, body.name, body.workdir, body.command, body.schedule)

    @app.delete("/api/robots/{robot_id}", status_code=204)
    def delete_robot(robot_id: int):
        if repo.get_open_run(robot_id) is not None:
            raise AlreadyRunningError("Stop the robot before deleting it")
        repo.delete_robot(robot_id)

    @app.post("/api/robots/{robot_id}/start")
    def start_robot(robot_id: int):
        return runner.start(robot_id)

    @app.post("/api/robots/{robot_id}/stop")
    def stop_robot(robot_id: int):
        run = runner.stop(robot_id)
        if run is None:
            raise HTTPException(status_code=409, detail="Robot is not running")
        return run

    # ---- runs / logs --------------------------------------------------------------------

    @app.get("/api/robots/{robot_id}/runs")
    def list_runs(
        robot_id: int,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
    ):
        return repo.list_runs(robot_id, page, page_size)

    @app.get("/api/runs/{run_id}/log")
    def run_log(run_id: int):
        text = runner.read_log(run_id)
        if text is None:
            raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
        return {"run_id": run_id, "log": text}

    # ---- alerts -------------------------------------------------------------------------

    @app.get("/api/alerts")
    def list_alerts(include_resolved: bool = False):
        return repo.list_alerts(include_resolved=include_resolved)

    @app.post("/api/alerts/{alert_id}/resolve")
    def resolve_alert(alert_id: int):
        try:
            return repo.resolve_alert(alert_id)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return app
