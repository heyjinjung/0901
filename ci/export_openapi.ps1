param(
  [string]$BackendService = "backend"
)

Write-Host "[OpenAPI] exporting from running container..."
docker compose exec -T $BackendService sh -lc "python -m app.export_openapi && ls -l app/current_openapi.json"
if ($LASTEXITCODE -ne 0) { Write-Error "[OpenAPI] export failed"; exit 1 }

$stamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
$root = Split-Path -Parent $PSScriptRoot
$src = Join-Path $root "cc-webapp\backend\app\current_openapi.json"
$dst = Join-Path $root "openapi_$stamp.json"

if (Test-Path $src) {
  Copy-Item $src $dst -Force
  Write-Host "[OpenAPI] snapshot saved -> $dst"
} else {
  Write-Error "[OpenAPI] source not found: $src"
  exit 1
}

# Optional: diff against last snapshot if exists
$prev = Get-ChildItem -Path $root -Filter "openapi_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 1 -First 1
if ($prev) {
  Write-Host "[OpenAPI] diff against: $($prev.FullName)"
  # Use comp for simple text diff output (Windows built-in)
  & cmd /c "comp `"$($prev.FullName)`" `"$dst`" /L" | Out-File -Encoding UTF8 (Join-Path $root "openapi_diff_$stamp.txt")
  Write-Host "[OpenAPI] diff saved -> openapi_diff_$stamp.txt"
}
