$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$frontendPath = Join-Path $repoRoot 'frontend'
$layoutPath = Join-Path $frontendPath 'app/layout.tsx'
$globalsCssPath = Join-Path $frontendPath 'app/globals.css'
$nextPath = Join-Path $frontendPath '.next'
$frontendUrl = 'http://127.0.0.1:5179/dashboard/minutas/nueva'
$frontendBaseUrl = 'http://127.0.0.1:5179'
$devTimeoutSeconds = 90

function Get-ListeningProcessIdsOnPort {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port
    )

    $processIds = @()

    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop
        if ($connections) {
            $processIds += $connections.OwningProcess
        }
    }
    catch {
        $netstatLines = netstat -ano | Select-String ":$Port\s"
        foreach ($line in $netstatLines) {
            if ($line.Line -match '\s+(\d+)\s*$') {
                $processIds += [int]$Matches[1]
            }
        }
    }

    return $processIds | Sort-Object -Unique
}

function Stop-ProcessesOnPort {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port
    )

    foreach ($processId in (Get-ListeningProcessIdsOnPort -Port $Port)) {
        try {
            $process = Get-Process -Id $processId -ErrorAction Stop
            Stop-Process -Id $processId -Force -ErrorAction Stop
            Write-Host "Stopped $($process.ProcessName) (PID $processId) on port $($Port)"
        }
        catch {
            Write-Host "Unable to stop PID $processId on port $($Port): $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
}

function Assert-FrontendCssReady {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PageUrl,
        [Parameter(Mandatory = $true)]
        [string]$BaseUrl
    )

    try {
        $response = Invoke-WebRequest -Uri $PageUrl -UseBasicParsing -TimeoutSec 10 -Headers @{ 'Cache-Control' = 'no-cache' }
    }
    catch {
        throw "No fue posible obtener el HTML de $PageUrl. $($_.Exception.Message)"
    }

    if ($response.StatusCode -ne 200) {
        throw "El HTML de $PageUrl respondio $($response.StatusCode) en vez de 200."
    }

    $cssMatches = [regex]::Matches([string]$response.Content, '/_next/static/css/[^"''\s>]+\.css')
    if ($cssMatches.Count -eq 0) {
        throw "El HTML de $PageUrl no referencia ningun asset CSS de Next (/_next/static/css/)."
    }

    $cssUrls = $cssMatches | ForEach-Object { "$BaseUrl$($_.Value)" } | Select-Object -Unique
    foreach ($cssUrl in $cssUrls) {
        try {
            $cssResponse = Invoke-WebRequest -Uri $cssUrl -UseBasicParsing -TimeoutSec 10 -Headers @{ 'Cache-Control' = 'no-cache' }
        }
        catch {
            throw "El asset CSS no respondio correctamente: $cssUrl. $($_.Exception.Message)"
        }

        if ($cssResponse.StatusCode -ne 200) {
            throw "El asset CSS respondio $($cssResponse.StatusCode) en vez de 200: $cssUrl"
        }
    }

    return $cssUrls
}

function Wait-FrontendCssReady {
    param(
        [Parameter(Mandatory = $true)]
        [System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $true)]
        [string]$PageUrl,
        [Parameter(Mandatory = $true)]
        [string]$BaseUrl,
        [int]$TimeoutSeconds = 90
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $lastError = $null

    while ((Get-Date) -lt $deadline) {
        if ($Process.HasExited) {
            throw "El proceso del frontend termino antes de estar listo. ExitCode: $($Process.ExitCode)"
        }

        try {
            $cssUrls = Assert-FrontendCssReady -PageUrl $PageUrl -BaseUrl $BaseUrl
            return $cssUrls
        }
        catch {
            $lastError = $_.Exception.Message
            Start-Sleep -Seconds 1
        }
    }

    throw "El frontend no quedo listo con CSS en $TimeoutSeconds segundos. Ultimo error: $lastError"
}

if (-not (Test-Path -LiteralPath $frontendPath)) {
    throw "Frontend path not found: $frontendPath"
}

if (-not (Test-Path -LiteralPath $globalsCssPath)) {
    throw "Missing global stylesheet: $globalsCssPath"
}

if (-not (Test-Path -LiteralPath $layoutPath)) {
    throw "Missing app layout: $layoutPath"
}

$layoutContent = Get-Content -LiteralPath $layoutPath -Raw
if (($layoutContent.Contains('import "./globals.css";') -eq $false) -and ($layoutContent.Contains("import './globals.css';") -eq $false)) {
    throw 'frontend/app/layout.tsx must contain: import "./globals.css";'
}

$globalsContent = Get-Content -LiteralPath $globalsCssPath -Raw
foreach ($directive in @('@tailwind base;', '@tailwind components;', '@tailwind utilities;')) {
    if ($globalsContent.Contains($directive) -eq $false) {
        throw "frontend/app/globals.css must contain: $directive"
    }
}

Stop-ProcessesOnPort -Port 5179
if (Test-Path -LiteralPath $nextPath) {
    Remove-Item -LiteralPath $nextPath -Recurse -Force
    Write-Host "Removed $nextPath"
}

Write-Host "Starting EasyPro frontend from $frontendPath"
Write-Host "URL: $frontendUrl"

$frontendProcess = Start-Process -FilePath 'npm.cmd' -ArgumentList @('run', 'dev:next') -WorkingDirectory $frontendPath -WindowStyle Hidden -PassThru

try {
    $cssUrls = Wait-FrontendCssReady -Process $frontendProcess -PageUrl $frontendUrl -BaseUrl $frontendBaseUrl -TimeoutSeconds $devTimeoutSeconds
    Write-Host "CSS asset verification passed:" -ForegroundColor Green
    foreach ($cssUrl in $cssUrls) {
        Write-Host "  $cssUrl" -ForegroundColor Green
    }
    Write-Host "Frontend ready at $frontendUrl" -ForegroundColor Green
}
catch {
    Stop-ProcessesOnPort -Port 5179
    if (-not $frontendProcess.HasExited) {
        Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host $_.Exception.Message -ForegroundColor Red
    throw
}
