"""Start, stop and supervise robot processes."""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import sys
import threading
from pathlib import Path

from .repository import Repository

logger = logging.getLogger("robot_ops.runner")

IS_WINDOWS = sys.platform == "win32"
MAX_LOG_BYTES = 1_000_000


class AlreadyRunningError(RuntimeError):
    pass


class StartError(RuntimeError):
    """The robot process could not be started (bad path, missing file, ...)."""


class Runner:
    def __init__(self, repo: Repository, log_dir: str | Path):
        self.repo = repo
        self.log_dir = Path(log_dir)
        self.start_failures = 0
        self._lock = threading.Lock()
        self._procs: dict[int, subprocess.Popen] = {}
        self._watchers: dict[int, threading.Thread] = {}
        self._stop_requested: set[int] = set()

    # ---- start --------------------------------------------------------------------------

    def start(self, robot_id: int) -> dict:
        """Start the declared command of a robot. Raises RobotNotFoundError, AlreadyRunningError,
        StartError."""
        robot = self.repo.get_robot(robot_id)  # the command always comes from the stored robot
        with self._lock:
            if self.repo.get_open_run(robot_id) is not None:
                raise AlreadyRunningError(f"Robot '{robot['name']}' is already running")
            run_id = self.repo.create_run(robot_id)
            log_path = self.log_dir / f"run_{run_id}.log"
            self.repo.set_run_log_path(run_id, str(log_path))
            try:
                proc, log_file = self._spawn(robot, log_path)
            except StartError as exc:
                self._record_start_failure(robot, run_id, log_path, str(exc))
                raise
            self._procs[run_id] = proc
            watcher = threading.Thread(
                target=self._watch,
                args=(run_id, robot, proc, log_file),
                daemon=True,
                name=f"robot-watch-{run_id}",
            )
            self._watchers[run_id] = watcher
            watcher.start()
        logger.info("Started robot %s run %s pid %s", robot["name"], run_id, proc.pid)
        run = self.repo.get_run(run_id)
        assert run is not None
        return run

    def _spawn(self, robot: dict, log_path: Path):
        workdir = Path(robot["workdir"])
        if not workdir.is_dir():
            raise StartError(f"Working directory does not exist: {workdir}")
        kwargs: dict = {}
        if IS_WINDOWS:
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kwargs["start_new_session"] = True
        log_file = None
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            log_file = open(log_path, "wb")  # noqa: SIM115 - closed by the watcher thread
            proc = subprocess.Popen(
                robot["command"],
                cwd=str(workdir),
                # shell=True: the command is the operator-declared string (e.g. run.bat),
                # never taken from a request body.
                shell=True,
                stdin=subprocess.DEVNULL,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                **kwargs,
            )
        except (OSError, ValueError) as exc:
            if log_file is not None:
                log_file.close()
            raise StartError(f"Cannot start command: {exc}") from exc
        return proc, log_file

    def _record_start_failure(self, robot: dict, run_id: int, log_path: Path, message: str):
        self.start_failures += 1
        logger.error("Failed to start robot %s: %s", robot["name"], message)
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            log_path.write_text(f"[robot-ops] {message}\n", encoding="utf-8")
        except OSError:
            logger.exception("Cannot write start-failure log %s", log_path)
        self.repo.finish_run(run_id, "error", None)
        self.repo.create_alert(
            robot["id"],
            "run_error",
            f"Robot '{robot['name']}' failed to start: {message}",
            run_id=run_id,
        )

    # ---- supervision --------------------------------------------------------------------

    def _watch(self, run_id: int, robot: dict, proc: subprocess.Popen, log_file) -> None:
        try:
            code = proc.wait()
        finally:
            try:
                log_file.close()
            except OSError:
                logger.exception("Cannot close log file of run %s", run_id)
        try:
            with self._lock:
                stopped = run_id in self._stop_requested
                self._stop_requested.discard(run_id)
                self._procs.pop(run_id, None)
            if stopped:
                status = "stopped"
            elif code == 0:
                status = "success"
            else:
                status = "error"
            self.repo.finish_run(run_id, status, code)
            if status == "error":
                self.repo.create_alert(
                    robot["id"],
                    "run_error",
                    f"Robot '{robot['name']}' finished with exit code {code}",
                    run_id=run_id,
                )
            logger.info("Run %s of %s finished: %s (exit %s)", run_id, robot["name"], status, code)
        except Exception:  # keep the watcher from dying silently
            logger.exception("Failed to record end of run %s", run_id)

    # ---- stop ---------------------------------------------------------------------------

    def stop(self, robot_id: int, timeout: float = 15.0) -> dict | None:
        """Stop the running process tree of a robot. Returns the finished run, or None if the
        robot was not running."""
        self.repo.get_robot(robot_id)
        run = self.repo.get_open_run(robot_id)
        if run is None:
            return None
        run_id = run["id"]
        with self._lock:
            proc = self._procs.get(run_id)
            watcher = self._watchers.get(run_id)
            if proc is not None:
                self._stop_requested.add(run_id)
        if proc is None:  # no live process known (should not happen): just close the record
            self.repo.finish_run(run_id, "stopped", None)
        else:
            self._kill_tree(proc)
            if watcher is not None:
                watcher.join(timeout)
        return self.repo.get_run(run_id)

    @staticmethod
    def _kill_tree(proc: subprocess.Popen) -> None:
        if proc.poll() is not None:
            return
        try:
            if IS_WINDOWS:
                result = subprocess.run(
                    ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    capture_output=True,
                    check=False,
                    timeout=15,
                )
                if result.returncode != 0:
                    logger.warning("taskkill returned %s: %s", result.returncode, result.stderr)
                    proc.kill()
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        except (OSError, subprocess.SubprocessError):
            logger.exception("Failed to kill process tree of pid %s", proc.pid)
            proc.kill()

    def shutdown(self) -> None:
        """Stop every running robot (called when the application exits)."""
        with self._lock:
            run_ids = list(self._procs)
        for run_id in run_ids:
            run = self.repo.get_run(run_id)
            if run is not None:
                try:
                    self.stop(run["robot_id"])
                except Exception:
                    logger.exception("Failed to stop run %s on shutdown", run_id)

    def wait_for_run(self, run_id: int, timeout: float = 30.0) -> None:
        """Block until the watcher of a run finished (used by tests and shutdown)."""
        watcher = self._watchers.get(run_id)
        if watcher is not None:
            watcher.join(timeout)

    # ---- logs ---------------------------------------------------------------------------

    def read_log(self, run_id: int) -> str | None:
        """Return the (tail of the) log text of a run, or None if the run does not exist."""
        run = self.repo.get_run(run_id)
        if run is None:
            return None
            
        robot = self.repo.get_robot(run["robot_id"])
        path = run.get("log_path")
        
        text_parts = []
        
        if path:
            try:
                size = os.path.getsize(path)
                with open(path, "rb") as fh:
                    if size > MAX_LOG_BYTES:
                        fh.seek(size - MAX_LOG_BYTES)
                    data = fh.read()
                text_parts.append(f"--- KẾT QUẢ CHẠY (STDOUT) ---\n{data.decode('utf-8', errors='replace')}")
            except FileNotFoundError:
                text_parts.append("--- KẾT QUẢ CHẠY (STDOUT) ---\n(Không tìm thấy file log)")
            except OSError:
                logger.exception("Cannot read log %s", path)
                text_parts.append("[robot-ops] Cannot read log file")

        if robot.get("workdir"):
            custom_log_path = Path(robot["workdir"]) / "logs" / "robot.json.log"
            try:
                size = os.path.getsize(custom_log_path)
                with open(custom_log_path, "rb") as fh:
                    if size > MAX_LOG_BYTES:
                        fh.seek(size - MAX_LOG_BYTES)
                    data = fh.read()
                text_parts.append(f"\n--- LOG CỦA ROBOT (robot.json.log) ---\n{data.decode('utf-8', errors='replace')}")
            except FileNotFoundError:
                text_parts.append(f"\n--- LOG CỦA ROBOT (robot.json.log) ---\n(Chưa có file log này tại {custom_log_path})")
            except OSError:
                logger.exception("Cannot read log %s", custom_log_path)
                text_parts.append(f"\n[robot-ops] Lỗi không thể đọc file: {custom_log_path}")

        if not text_parts:
            return ""
            
        return "\n".join(text_parts)
