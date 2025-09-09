#!/usr/bin/env pwsh

<#
  목적: Windows PowerShell에서 따옴표/리디렉션 오류 없이
        컨테이너 내부에서 백엔드 검증 루틴을 일괄 실행한다.

  수행 항목
  - pytest 스모크/가드: health, alembic guard, schema drift guard
  - Alembic heads 확인 및 upgrade head
  - OpenAPI 재수출 + drift diff 테스트

  사용법
    ./scripts/backend-verify.ps1

  요구사항
    - Docker Desktop 실행 중
    - docker compose v2 또는 v1 설치됨
    - 프로젝트 루트에서 실행
#>

param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)

# Docker Compose CLI 감지 (PS 5.1 호환: 리다이렉션과 종료 코드 사용)
function Get-ComposeCli {
  # 우선 docker compose (v2) 확인
  & docker compose version > $null 2>&1
  if ($LASTEXITCODE -eq 0) { return @{ cmd = 'docker'; sub = 'compose' } }

  # 다음 docker-compose (v1) 확인
  & docker-compose --version > $null 2>&1
  if ($LASTEXITCODE -eq 0) { return @{ cmd = 'docker-compose'; sub = $null } }

  throw 'Docker Compose가 감지되지 않았습니다. Docker Desktop을 업데이트하세요.'
}

# 컨테이너 backend에서 명령 실행 (Invoke 승인 동사 사용)
function Invoke-InBackend {
  param(
    [Parameter(Mandatory = $true)][string] $Cmd,
    [string] $Title
  )

  if ($Title) { Write-Host "▶ $Title" -ForegroundColor Cyan }

  $dc = Get-ComposeCli
  if ($dc.sub) {
    & $dc.cmd $dc.sub exec backend /bin/sh -lc "$Cmd"
  } else {
    & $dc.cmd exec backend /bin/sh -lc "$Cmd"
  }

  $code = $LASTEXITCODE
  if ($code -ne 0) {
    $label = if ($Title) { $Title } else { $Cmd }
    Write-Host ("✖ 실패 (Exit {0}) : {1}" -f $code, $label) -ForegroundColor Red
  } else {
    $label = if ($Title) { $Title } else { $Cmd }
    Write-Host ("✔ 성공 : {0}" -f $label) -ForegroundColor Green
  }
  return $code
}

Write-Host 'Casino-Club F2P 백엔드 검증 시작' -ForegroundColor Green

$failures = @()

# 1) pytest 스모크/가드
$code = Invoke-InBackend -Title 'Pytest 스모크/가드 (health, alembic, schema drift)' -Cmd "pytest -q app/tests/test_smoke_health.py app/tests/test_ci_alembic_guard.py app/tests/test_schema_drift_guard.py"
if ($code -ne 0) { $failures += 'pytest_smoke_and_guards' }

# 2) Alembic heads 및 업그레이드
$code = Invoke-InBackend -Title 'Alembic heads 확인' -Cmd 'alembic heads -v'
if ($code -ne 0) { $failures += 'alembic_heads' }

$code = Invoke-InBackend -Title 'Alembic upgrade head' -Cmd 'alembic upgrade head'
if ($code -ne 0) { $failures += 'alembic_upgrade' }

# 3) OpenAPI 재수출 + drift diff
$code = Invoke-InBackend -Title 'OpenAPI 재수출' -Cmd 'python -m app.export_openapi'
if ($code -ne 0) { $failures += 'export_openapi' }

$code = Invoke-InBackend -Title 'OpenAPI 드리프트 가드' -Cmd 'pytest -q app/tests/test_openapi_diff_ci.py'
if ($code -ne 0) { $failures += 'openapi_drift_guard' }

Write-Host '--- 요약 ---' -ForegroundColor Yellow
if ($failures.Count -eq 0) {
  Write-Host 'PASS: 모든 항목 통과' -ForegroundColor Green
  exit 0
} else {
  Write-Host ("FAIL: {0}" -f ($failures -join ', ')) -ForegroundColor Red
  exit 1
}
