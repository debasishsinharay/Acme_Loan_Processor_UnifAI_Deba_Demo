#!/usr/bin/env bash
# Starts the backend (port 5500) and the frontend (port 5001) for local development.
# Run from the repo root: ./scripts/run_dev.sh   (Ctrl+C stops both)
set -euo pipefail
cd "$(dirname "$0")/.."

[ -f .env ] || { echo "Create .env first: cp .env.example .env"; exit 1; }

python3 -m venv .venv
.venv/bin/pip install -q -r backend/requirements.txt
(cd frontend && npm install --silent)

(cd backend && ../.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 5500 --reload) &
BACKEND=$!
trap 'kill $BACKEND' EXIT
cd frontend && npx next dev -p 5001
