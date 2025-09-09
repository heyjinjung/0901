# PowerShell helper to export current OpenAPI schema (canonical + timestamped snapshot)
# Usage: ./scripts/export_openapi.ps1 [-Python "python"]
param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path (Split-Path $root) "cc-webapp\backend\app"
Write-Host "[*] Exporting OpenAPI from backend path: $backend"
Push-Location $backend
try {
    & $Python -m app.export_openapi
} finally {
    Pop-Location
}
