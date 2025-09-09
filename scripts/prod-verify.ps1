param(
  [string]$EnvFile = ".env.production",
  [string]$BackendUrl = "http://localhost:8000",
  [string]$FrontendUrl = "http://localhost:3000",
  [switch]$RunSmoke,
  [switch]$SkipSecretCheck
)

Set-StrictMode -Version 2
$ErrorActionPreference = 'Stop'

function Write-Info($msg) { Write-Host "[prod-verify] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "[prod-verify] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[prod-verify] $msg" -ForegroundColor Red }

function Test-HttpOk([string]$Url, [int]$TimeoutSeconds = 30) {
  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  do {
    try {
      $res = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
      if ($res.StatusCode -eq 200) { return $true }
    } catch { Start-Sleep -Seconds 1 }
  } while ((Get-Date) -lt $deadline)
  return $false
}

Write-Info "시작: 시크릿 검증 및 재검증 루프"

if (-not (Test-Path -LiteralPath $EnvFile)) {
  Write-Err "Env 파일을 찾을 수 없습니다: $EnvFile"
  exit 2
}

$content = Get-Content -LiteralPath $EnvFile -Raw

$requiredKeys = @(
  'JWT_SECRET_KEY','POSTGRES_PASSWORD','DATABASE_URL','REDIS_PASSWORD','FRONTEND_URL','BACKEND_URL'
)
$missing = @()
foreach ($k in $requiredKeys) {
  if ($content -notmatch ("^(?im)\s*" + [regex]::Escape($k) + "\s*=")) {
    $missing += $k
  }
}
if ($missing.Count -gt 0) {
  Write-Err ("필수 키 누락: " + ($missing -join ', '))
  if (-not $SkipSecretCheck) { exit 3 }
}

$placeholders = @(
  'secure_password_here',
  'super_secure_production_key_here',
  'change_this_for_prod',
  'your-domain.com'
)
$found = @()
foreach ($p in $placeholders) {
  if ($content -match [regex]::Escape($p)) { $found += $p }
}
if ($found.Count -gt 0) {
  Write-Err ("placeholder 값 감지: " + ($found -join ', '))
  if (-not $SkipSecretCheck) { exit 4 }
}

Write-Info ".env.production 검증 통과(또는 SkipSecretCheck 사용). 백엔드 재시작"
& docker compose restart backend | Out-Null

Write-Info "헬스 체크: $BackendUrl/health"
if (-not (Test-HttpOk "$BackendUrl/health" 30)) {
  Write-Err "/health 200 미수신"
  exit 5
}
Write-Info "헬스 체크: $BackendUrl/docs"
if (-not (Test-HttpOk "$BackendUrl/docs" 30)) {
  Write-Err "/docs 200 미수신"
  exit 6
}

if ($RunSmoke) {
  Write-Info "Playwright 요약 스모크 실행(컨테이너)"
  $cmd = 'docker compose -f docker-compose.yml -f docker-compose.playwright.yml run --rm --entrypoint bash playwright -lc "npm install --no-audit --no-fund; npx playwright test cc-webapp/frontend/tests/playwright-smoke.spec.ts --config=playwright.config.ts"'
  Write-Host $cmd
  $proc = Start-Process -FilePath "powershell" -ArgumentList "-NoLogo","-NoProfile","-ExecutionPolicy","Bypass","-Command",$cmd -PassThru -Wait -WindowStyle Hidden
  if ($proc.ExitCode -ne 0) {
    Write-Err "Playwright 스모크 실패(ExitCode=$($proc.ExitCode))"
    exit 7
  }
  Write-Info "Playwright 스모크 0 failed"
}

Write-Host "HEALTH:PASS DOCS:PASS SMOKE:$((if($RunSmoke){'PASS'}else{'SKIP'}))" -ForegroundColor Green
exit 0
