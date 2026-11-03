#!/usr/bin/env bash
# Runner script for IIITA Cyber Security Lab (IT-30001)

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv .venv || uv venv
    echo "[*] Installing dependencies..."
    ./.venv/bin/pip install -r requirements.txt
fi

if [ "$1" == "test" ]; then
    echo "[*] Running automated test suite..."
    ./.venv/bin/python test_exploit.py
else
    echo "[*] Starting Flask web server on http://127.0.0.1:5000 ..."
    echo "[*] Press Ctrl+C to stop."
    ./.venv/bin/python app.py
fi
