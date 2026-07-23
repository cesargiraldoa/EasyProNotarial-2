param(
    [int]$BackendPort = 8001
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$backendPath = Join-Path $repoRoot 'backend'
$pythonExe = Join-Path $backendPath '.venv'
$pythonExe = Join-Path $pythonExe 'Scripts/python.exe'
$healthUrl = "http://127.0.0.1:$BackendPort/health"

if (-not (Test-Path -LiteralPath $backendPath)) {
    throw "Backend path not found: $backendPath"
}

if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw "Missing backend interpreter: $pythonExe"
}

Write-Host "Starting EasyPro backend from $backendPath"
Write-Host "Port: $BackendPort"
Write-Host "Health URL: $healthUrl"

Set-Location -LiteralPath $backendPath
& $pythonExe -m uvicorn app.main:app --host 127.0.0.1 --port $BackendPort
