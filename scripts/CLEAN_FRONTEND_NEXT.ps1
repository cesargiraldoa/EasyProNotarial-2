$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$frontendPath = Join-Path $root 'frontend'

function Stop-NodeProcesses {
    $nodeProcesses = Get-Process node -ErrorAction SilentlyContinue
    if ($null -ne $nodeProcesses) {
        $nodeProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
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

if (-not (Test-Path -LiteralPath $frontendPath)) {
    throw "Frontend path not found: $frontendPath"
}

Stop-NodeProcesses
Remove-PathIfExists -Path (Join-Path $frontendPath '.next')
Remove-PathIfExists -Path (Join-Path $frontendPath 'node_modules/.cache')

Write-Host 'Frontend cache cleaned.'
Write-Host 'Next step: cd frontend; npm run build && npm run start'
