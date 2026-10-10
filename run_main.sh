#!/bin/bash
# Chuyển đến thư mục chứa script
cd "$(dirname "$0")"

# Kích hoạt môi trường ảo nếu có
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Chạy file main.py
python main.py
