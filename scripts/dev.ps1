$root = Split-Path -Parent $PSScriptRoot
Write-Host "EasyPro 2"
Write-Host "1. Inicie PostgreSQL: docker compose up -d"
Write-Host "2. Backend: cd $root\backend; python -m venv .venv; .\.venv\Scripts\activate; pip install -r requirements.txt; uvicorn app.main:app --reload --host 127.0.0.1 --port 8001"
Write-Host "3. Frontend: cd $root\frontend; npm install; npm run dev  # puerto 5179"
