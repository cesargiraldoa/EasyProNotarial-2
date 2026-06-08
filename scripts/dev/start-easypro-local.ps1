$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$backendScript = Join-Path $PSScriptRoot 'start-backend-local.ps1'
$frontendScript = Join-Path $PSScriptRoot 'start-frontend-local.ps1'

if (-not (Test-Path -LiteralPath $backendScript)) {
    throw "Missing backend launcher: $backendScript"
}

if (-not (Test-Path -LiteralPath $frontendScript)) {
    throw "Missing frontend launcher: $frontendScript"
}

Write-Host "Opening EasyPro backend and frontend in separate PowerShell windows..."
Write-Host "Backend: http://127.0.0.1:8001/health"
Write-Host "Frontend: http://127.0.0.1:5179/dashboard/minutas/nueva"

Start-Process -FilePath powershell.exe -ArgumentList @(
    '-NoExit',
    '-ExecutionPolicy',
    'Bypass',
    '-File',
    $backendScript
) -WorkingDirectory $repoRoot

Start-Process -FilePath powershell.exe -ArgumentList @(
    '-NoExit',
    '-ExecutionPolicy',
    'Bypass',
    '-File',
    $frontendScript
) -WorkingDirectory $repoRoot
