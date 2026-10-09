@echo off
REM Starts the Robot Ops web app on http://127.0.0.1:8000 (local access only, no login).
REM Optional environment variables: ROBOT_OPS_DATA_DIR, ROBOT_OPS_DB, ROBOT_OPS_LOG_DIR,
REM ROBOT_OPS_HOST, ROBOT_OPS_PORT.
cd /d "%~dp0"
python -m robot_ops
if errorlevel 1 (
    echo Application exited with an error. See data\logs\app.log
    pause
)
