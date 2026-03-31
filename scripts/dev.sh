#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "EasyPro 2"
echo "1. Inicie PostgreSQL: docker compose up -d"
echo "2. Backend: cd ${ROOT}/backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000"
echo "3. Frontend: cd ${ROOT}/frontend && npm install && npm run dev # puerto 5179"
