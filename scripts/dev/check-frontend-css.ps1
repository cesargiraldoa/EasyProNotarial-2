$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$frontendUrl = 'http://127.0.0.1:5179/dashboard/minutas/nueva'
$frontendBaseUrl = 'http://127.0.0.1:5179'
$timeoutSeconds = 20

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
        throw "El frontend no responde en $PageUrl. $($_.Exception.Message)"
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

$deadline = (Get-Date).AddSeconds($timeoutSeconds)
$lastError = $null

while ((Get-Date) -lt $deadline) {
    try {
        $cssUrls = Assert-FrontendCssReady -PageUrl $frontendUrl -BaseUrl $frontendBaseUrl
        Write-Host "Frontend activo en 5179 y CSS verificado:" -ForegroundColor Green
        foreach ($cssUrl in $cssUrls) {
            Write-Host "  $cssUrl" -ForegroundColor Green
        }
        exit 0
    }
    catch {
        $lastError = $_.Exception.Message
        Start-Sleep -Seconds 1
    }
}

Write-Host $lastError -ForegroundColor Red
exit 1
