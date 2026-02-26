param(
    [switch]$SkipVersionBump
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$androidAppDir = Join-Path $projectRoot "android-app"
$innerScript = Join-Path $androidAppDir "build-release-aab.ps1"

if (-not (Test-Path $innerScript)) {
    Write-Error "Missing script: $innerScript"
}

Push-Location $androidAppDir
try {
    if ($SkipVersionBump) {
        & ".\build-release-aab.ps1" -SkipVersionBump
    } else {
        & ".\build-release-aab.ps1"
    }
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
