$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$frontendPath = Join-Path $repoRoot 'frontend'
$layoutPath = Join-Path $frontendPath 'app/layout.tsx'
$globalsCssPath = Join-Path $frontendPath 'app/globals.css'
$envLocalPath = Join-Path $frontendPath '.env.local'
$nextPath = Join-Path $frontendPath '.next'
$stdoutLogPath = Join-Path $frontendPath 'frontend-local.stdout.log'
$stderrLogPath = Join-Path $frontendPath 'frontend-local.stderr.log'
$frontendBaseUrl = 'http://127.0.0.1:5179'
$backendHealthUrl = 'http://127.0.0.1:8001/health'
$devTimeoutSeconds = 120
$validationRoutes = @(
    '/login'
    '/dashboard'
    '/dashboard/minutas/nueva'
    '/dashboard/casos/5/editor/6/3'
)

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
            Write-Host "Stopped $($process.ProcessName) (PID $processId) on port $Port" -ForegroundColor Yellow
        }
        catch {
            Write-Host "Unable to stop PID $processId on port ${Port}: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
}

function Stop-NodeProcesses {
    $nodeProcesses = Get-Process -Name 'node' -ErrorAction SilentlyContinue
    if ($null -eq $nodeProcesses) {
        return
    }

    foreach ($process in $nodeProcesses) {
        try {
            Stop-Process -Id $process.Id -Force -ErrorAction Stop
            Write-Host "Stopped node process (PID $($process.Id))" -ForegroundColor Yellow
        }
        catch {
            Write-Host "Unable to stop node process PID $($process.Id): $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
}

function Ensure-FrontendEnvLocal {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [string]$BackendUrl
    )

    $desiredLine = "NEXT_PUBLIC_API_URL=$BackendUrl"
    if (-not (Test-Path -LiteralPath $Path)) {
        @(
            'NEXT_PUBLIC_FRONTEND_URL=http://127.0.0.1:5179'
            $desiredLine
            'NEXT_PUBLIC_ONLYOFFICE_DOCS_URL=https://onlyoffice.easypronotarial.com'
            'ONLYOFFICE_JWT_SECRET=EasyProOnlyOfficeSecret2026'
        ) | Set-Content -LiteralPath $Path -Encoding utf8
        Write-Host "Created $Path with local backend URL $BackendUrl" -ForegroundColor Yellow
        return
    }

    $lines = Get-Content -LiteralPath $Path
    $updated = $false
    $foundApiLine = $false

    for ($index = 0; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -match '^\s*NEXT_PUBLIC_API_URL\s*=') {
            $foundApiLine = $true
            if ($lines[$index].Trim() -ne $desiredLine) {
                $lines[$index] = $desiredLine
                $updated = $true
            }
        }
    }

    if (-not $foundApiLine) {
        $lines += $desiredLine
        $updated = $true
    }

    if ($updated) {
        Set-Content -LiteralPath $Path -Value $lines -Encoding utf8
        Write-Host "Corrected $Path to $desiredLine" -ForegroundColor Yellow
    }
}

function Ensure-NpmCiIfMissingNodeModules {
    param(
        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory
    )

    $nodeModulesPath = Join-Path $WorkingDirectory 'node_modules'
    if (Test-Path -LiteralPath $nodeModulesPath) {
        return
    }

    Write-Host "node_modules missing, running npm ci" -ForegroundColor Yellow
    Push-Location $WorkingDirectory
    try {
        & npm.cmd ci
    }
    finally {
        Pop-Location
    }
}

function Assert-BackendHealth {
    param(
        [Parameter(Mandatory = $true)]
        [string]$HealthUrl
    )

    try {
        $response = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 5 -Headers @{ 'Cache-Control' = 'no-cache' }
    }
    catch {
        throw "Backend local no responde en $HealthUrl"
    }

    if ($response.StatusCode -ne 200) {
        throw "Backend local no responde en $HealthUrl"
    }
}

function Assert-FrontendPageReady {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PageUrl,
        [Parameter(Mandatory = $true)]
        [string]$BaseUrl
    )

    try {
        $response = Invoke-WebRequest -Uri $PageUrl -UseBasicParsing -TimeoutSec 15 -Headers @{ 'Cache-Control' = 'no-cache' }
    }
    catch {
        throw "No fue posible obtener el HTML de $PageUrl. $($_.Exception.Message)"
    }

    if ($response.StatusCode -ne 200) {
        throw "El HTML de $PageUrl respondio $($response.StatusCode) en vez de 200."
    }

    $html = [string]$response.Content
    foreach ($badMarker in @(
        '__webpack_modules__[moduleId] is not a function'
        'Cannot find module vendor-chunks'
        'Internal Server Error'
    )) {
        if ($html.Contains($badMarker)) {
            throw "El HTML de $PageUrl contiene un error no permitido: $badMarker"
        }
    }

    $cssMatches = [regex]::Matches($html, '/_next/static/css/[^"''\s>]+\.css')
    if ($cssMatches.Count -eq 0) {
        throw "HTML sin CSS en ${PageUrl}: no referencia ningun asset CSS de Next (/_next/static/css/)."
    }

    $cssUrls = $cssMatches | ForEach-Object { "$BaseUrl$($_.Value)" } | Select-Object -Unique
    foreach ($cssUrl in $cssUrls) {
        try {
            $cssResponse = Invoke-WebRequest -Uri $cssUrl -UseBasicParsing -TimeoutSec 15 -Headers @{ 'Cache-Control' = 'no-cache' }
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

function Write-ProcessLogTail {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [int]$Tail = 120
    )

    Write-Host "$Label ($Path)" -ForegroundColor Yellow
    if (-not (Test-Path -LiteralPath $Path)) {
        Write-Host '  log file not found' -ForegroundColor DarkYellow
        return
    }

    $lines = Get-Content -LiteralPath $Path -Tail $Tail -ErrorAction SilentlyContinue
    if ($null -eq $lines -or $lines.Count -eq 0) {
        Write-Host '  log file empty' -ForegroundColor DarkYellow
        return
    }

    foreach ($line in $lines) {
        Write-Host "  $line"
    }
}

function Write-FailureContext {
    param(
        [Parameter(Mandatory = $true)]
        [System.Diagnostics.Process]$Process
    )

    Write-Host "Frontend process exit code: $($Process.ExitCode)" -ForegroundColor Red
    Write-ProcessLogTail -Label 'stdout tail' -Path $stdoutLogPath -Tail 120
    Write-ProcessLogTail -Label 'stderr tail' -Path $stderrLogPath -Tail 120
}

function Wait-FrontendReady {
    param(
        [Parameter(Mandatory = $true)]
        [System.Diagnostics.Process]$Process,
        [int]$TimeoutSeconds = 120
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $lastError = $null

    while ((Get-Date) -lt $deadline) {
        if ($Process.HasExited) {
            Write-FailureContext -Process $Process
            throw "El proceso del frontend termino antes de estar listo."
        }

        try {
            $cssByRoute = @{}
            foreach ($route in $validationRoutes) {
                $pageUrl = "$frontendBaseUrl$route"
                $cssByRoute[$route] = Assert-FrontendPageReady -PageUrl $pageUrl -BaseUrl $frontendBaseUrl
            }

            return $cssByRoute
        }
        catch {
            $lastError = $_.Exception.Message
            Start-Sleep -Seconds 1
        }
    }

    if ($Process.HasExited) {
        Write-FailureContext -Process $Process
    }

    throw "El frontend no quedo listo con rutas y CSS en $TimeoutSeconds segundos. Ultimo error: $lastError"
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

Ensure-FrontendEnvLocal -Path $envLocalPath -BackendUrl 'http://127.0.0.1:8001'
Ensure-NpmCiIfMissingNodeModules -WorkingDirectory $frontendPath

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

Stop-NodeProcesses
Stop-ProcessesOnPort -Port 5179

Write-Host "Cleaning .next before local startup" -ForegroundColor Yellow
if (Test-Path -LiteralPath $nextPath) {
    Remove-Item -LiteralPath $nextPath -Recurse -Force
}

foreach ($logPath in @($stdoutLogPath, $stderrLogPath)) {
    if (Test-Path -LiteralPath $logPath) {
        Remove-Item -LiteralPath $logPath -Force
    }
}

Assert-BackendHealth -HealthUrl $backendHealthUrl
Write-Host "backend health OK $backendHealthUrl" -ForegroundColor Green

Write-Host "Starting EasyPro frontend from $frontendPath"
Write-Host "URL base: $frontendBaseUrl"
Write-Host "frontend dev server starting" -ForegroundColor Green

$frontendProcess = Start-Process -FilePath 'npm.cmd' -ArgumentList @('run', 'dev:local') -WorkingDirectory $frontendPath -WindowStyle Hidden -RedirectStandardOutput $stdoutLogPath -RedirectStandardError $stderrLogPath -PassThru

try {
    $cssByRoute = Wait-FrontendReady -Process $frontendProcess -TimeoutSeconds $devTimeoutSeconds
    Write-Host 'Frontend dev server ready.' -ForegroundColor Green
    foreach ($route in $validationRoutes) {
        Write-Host "Validated route: $frontendBaseUrl$route" -ForegroundColor Green
        foreach ($cssUrl in $cssByRoute[$route]) {
            Write-Host "  CSS: $cssUrl" -ForegroundColor Green
        }
    }
    Write-Host "Backend health: OK $backendHealthUrl" -ForegroundColor Green
}
catch {
    Stop-ProcessesOnPort -Port 5179
    if (-not $frontendProcess.HasExited) {
        Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Write-FailureContext -Process $frontendProcess
    Write-Host $_.Exception.Message -ForegroundColor Red
    throw
}

