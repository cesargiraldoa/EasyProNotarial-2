<#
  dev-restart.ps1 — Reinicia EasyProNotarial en local, sin copiar/pegar comandos.

  Qué hace (en orden):
    1. Mata cualquier proceso que ocupe los puertos del backend (8001) y frontend (5179).
    2. Limpia la cache .next del frontend (evita JS viejo servido por HMR).
    3. Arranca el BACKEND en 8001 con --reload (recarga sola al cambiar codigo).
    4. Espera a que el backend responda /health.
    5. Arranca el FRONTEND en 5179 apuntando a http://127.0.0.1:8001.

  No exige ninguna rama. Usa rutas relativas a este archivo, asi que funciona
  aunque el repo este en una subcarpeta (p.ej. C:\EasyProNotarial-2\easypro2).

  Uso:  desde cualquier lado, click derecho > "Ejecutar con PowerShell", o:
        powershell -ExecutionPolicy Bypass -File scripts\dev-restart.ps1
#>

param(
    [int]$BackendPort = 8001,
    [int]$FrontendPort = 5179
)

$ErrorActionPreference = 'Stop'

# Raiz del repo = carpeta padre de /scripts (funciona en subcarpetas).
$root = Split-Path -Parent $PSScriptRoot
$backendPath = Join-Path $root 'backend'
$frontendPath = Join-Path $root 'frontend'
$backendHealthUrl = "http://127.0.0.1:$BackendPort/health"
$apiUrl = "http://127.0.0.1:$BackendPort"

function Get-PidsByPort {
    param([Parameter(Mandatory = $true)][int]$Port)
    $processIds = @()
    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction Stop
        if ($null -ne $connections) { $processIds += $connections.OwningProcess }
    }
    catch {
        foreach ($line in (netstat -ano | Select-String ":$Port\s")) {
            if ($line.Line -match '\s+(\d+)\s*$') { $processIds += [int]$Matches[1] }
        }
    }
    return $processIds | Sort-Object -Unique
}

function Stop-ProcessesOnPort {
    param([Parameter(Mandatory = $true)][int[]]$Ports)
    foreach ($port in $Ports) {
        foreach ($processId in (Get-PidsByPort -Port $port)) {
            if ($processId -eq 0) { continue }
            try {
                Stop-Process -Id $processId -Force -ErrorAction Stop
                Write-Host "  Puerto $port liberado (PID $processId detenido)."
            }
            catch {
                Write-Host ("  No se pudo detener PID {0} en puerto {1}: {2}" -f $processId, $port, $_.Exception.Message)
            }
        }
    }
}

function Wait-For-BackendHealth {
    param([int]$TimeoutSeconds = 60)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $backendHealthUrl -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) { return $true }
        }
        catch { }
        Start-Sleep -Seconds 2
    }
    return $false
}

# --- Validaciones minimas ---
if (-not (Test-Path -LiteralPath $backendPath)) { throw "No encuentro backend en: $backendPath" }
if (-not (Test-Path -LiteralPath $frontendPath)) { throw "No encuentro frontend en: $frontendPath" }
$venvActivate = Join-Path $backendPath '.venv\Scripts\Activate.ps1'
if (-not (Test-Path -LiteralPath $venvActivate)) { throw "No encuentro el venv del backend en: $venvActivate" }

Write-Host "== EasyPro dev-restart ==" -ForegroundColor Cyan
Write-Host "Repo: $root"

Write-Host "1) Liberando puertos $BackendPort (backend) y $FrontendPort (frontend)..."
Stop-ProcessesOnPort -Ports @($BackendPort, $FrontendPort)

Write-Host "2) Limpiando cache .next del frontend..."
$nextCache = Join-Path $frontendPath '.next'
if (Test-Path -LiteralPath $nextCache) {
    Remove-Item -LiteralPath $nextCache -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  Cache .next eliminada."
}

Write-Host "3) Arrancando BACKEND en $BackendPort (--reload) en una ventana nueva..."
$backendCmd = "Set-Location -LiteralPath `"$backendPath`"; .\.venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --host 127.0.0.1 --port $BackendPort --reload"
Start-Process -FilePath powershell.exe -ArgumentList @('-NoExit', '-ExecutionPolicy', 'Bypass', '-Command', $backendCmd)

Write-Host "4) Esperando /health del backend..."
if (Wait-For-BackendHealth -TimeoutSeconds 60) {
    Write-Host "  Backend OK en $backendHealthUrl" -ForegroundColor Green
}
else {
    Write-Host "  El backend no respondio /health a tiempo. Revisa su ventana por errores." -ForegroundColor Yellow
}

Write-Host "5) Arrancando FRONTEND en $FrontendPort (apuntando a $apiUrl)..."
$frontendCmd = "Set-Location -LiteralPath `"$frontendPath`"; `$env:NEXT_PUBLIC_API_URL='$apiUrl'; npm run dev:raw"
Start-Process -FilePath powershell.exe -ArgumentList @('-NoExit', '-ExecutionPolicy', 'Bypass', '-Command', $frontendCmd)

Write-Host ""
Write-Host "Listo." -ForegroundColor Cyan
Write-Host "  Backend:  $apiUrl  (health: $backendHealthUrl)"
Write-Host "  Frontend: http://127.0.0.1:$FrontendPort/dashboard"
Write-Host ""
Write-Host "Se abrieron dos ventanas (backend y frontend). Cierralas para detener los servicios."
