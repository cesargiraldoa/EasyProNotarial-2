param(
    [int]$BackendPort = 8001
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$backendPath = Join-Path $root 'backend'
$frontendPath = Join-Path $root 'frontend'
$frontendLauncher = Join-Path $root 'scripts\dev\start-frontend-local.ps1'
$backendHealthUrl = "http://127.0.0.1:$BackendPort/health"

function Stop-NodeProcesses {
    $nodeProcesses = Get-Process node -ErrorAction SilentlyContinue
    if ($null -ne $nodeProcesses) {
        $nodeProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    }
}

function Get-PidsByPort {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port
    )

    $processIds = @()

    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction Stop
        if ($null -ne $connections) {
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
        [int[]]$Ports
    )

    foreach ($port in $Ports) {
        $processIdsToStop = Get-PidsByPort -Port $port
        foreach ($processIdToStop in $processIdsToStop) {
            try {
                Stop-Process -Id $processIdToStop -Force -ErrorAction Stop
                Write-Host "Port $port freed by stopping PID $processIdToStop"
            }
            catch {
                Write-Host ("Could not stop PID {0} on port {1}: {2}" -f $processIdToStop, $port, $_.Exception.Message)
            }
        }
    }
}

function Remove-PathIfExists {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
        Write-Host "Removed $Path"
    }
}

function Assert-RequiredPaths {
    $required = @(
        (Join-Path $backendPath '.venv')
    )

    foreach ($path in $required) {
        if (-not (Test-Path -LiteralPath $path)) {
            throw "Required path missing: $path"
        }
    }
}

function Wait-For-BackendHealth {
    param(
        [int]$TimeoutSeconds = 60
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $backendHealthUrl -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                return
            }
        }
        catch {
        }

        Start-Sleep -Seconds 2
    }

    throw "Backend health check failed after $TimeoutSeconds seconds: $backendHealthUrl"
}

$currentBranch = (git branch --show-current).Trim()
if ($currentBranch -eq 'main') {
    Write-Error 'This script cannot run on main. Switch to your feature branch.'
    exit 1
}

Write-Host "Branch: $currentBranch"
Write-Host "Backend port: $BackendPort"

if (-not (Test-Path -LiteralPath $backendPath)) {
    throw "Backend path not found: $backendPath"
}

if (-not (Test-Path -LiteralPath $frontendPath)) {
    throw "Frontend path not found: $frontendPath"
}

Write-Host "Stopping node processes..."
Stop-NodeProcesses

Write-Host "Freeing ports 5179 and $BackendPort..."
Stop-ProcessesOnPort -Ports @(5179, $BackendPort)

Write-Host "Cleaning frontend cache..."
Remove-PathIfExists -Path (Join-Path $frontendPath '.next')

Assert-RequiredPaths

$backendWindowCommand = "Set-Location -LiteralPath `"$backendPath`"; .\.venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --host 127.0.0.1 --port $BackendPort"

Write-Host "Starting backend in a new PowerShell window..."
Start-Process -FilePath powershell.exe -ArgumentList @(
    '-NoExit',
    '-ExecutionPolicy',
    'Bypass',
    '-Command',
    $backendWindowCommand
)

Write-Host 'Waiting for backend health...'
Wait-For-BackendHealth -TimeoutSeconds 60

Write-Host "Starting frontend in a new PowerShell window..."
Start-Process -FilePath powershell.exe -ArgumentList @(
    '-NoExit',
    '-ExecutionPolicy',
    'Bypass',
    '-File',
    $frontendLauncher
) -WorkingDirectory $root

Write-Host ''
Write-Host "Backend: $backendHealthUrl"
Write-Host 'Frontend: http://127.0.0.1:5179/dashboard'
Write-Host 'Crear Minuta: http://127.0.0.1:5179/dashboard/minutas/nueva'
