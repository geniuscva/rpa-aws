#!/usr/bin/env bash
# Starts the Robot Ops web app on http://127.0.0.1:8000 (local access only, no login).
# Optional environment variables: ROBOT_OPS_DATA_DIR, ROBOT_OPS_DB, ROBOT_OPS_LOG_DIR,
# ROBOT_OPS_HOST, ROBOT_OPS_PORT.

cd "$(dirname "$0")" || exit 1

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

python3 -m robot_ops

if [ $? -ne 0 ]; then
    echo "Application exited with an error. See data/logs/app.log"
    read -rp "Press Enter to continue..."
fi
