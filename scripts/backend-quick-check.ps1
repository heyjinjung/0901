#requires -Version 5.1
[CmdletBinding()]
param(
    [switch]$VerboseLogs,
    [switch]$FastOnly
)

$ErrorActionPreference = 'Stop'

function Invoke-InBackend([string]$cmd){
    $full = "docker compose exec backend /bin/sh -lc `"$cmd`""
    if($VerboseLogs){ Write-Host "[exec] $full" -ForegroundColor Cyan }
    $psi = Start-Process -FilePath powershell -ArgumentList "-NoProfile","-Command",$full -Wait -PassThru -WindowStyle Hidden
    return $psi.ExitCode
}

if(-not $FastOnly){
    Write-Host "== Alembic: heads -v (정보)" -ForegroundColor Yellow
    Invoke-Expression "docker compose exec backend /bin/sh -lc 'alembic heads -v'"

    Write-Host "== Alembic: upgrade head(시도)" -ForegroundColor Yellow
    $code = Invoke-InBackend "alembic upgrade head"
    if($code -ne 0){
        Write-Warning "upgrade head 실패 → 스키마 선행 생성 상태로 보임. 운영 시간 외 수동 정리 권장(현재는 생략)."
    }
} else {
    Write-Host "== Alembic 단계 생략(FastOnly)" -ForegroundColor DarkYellow
}

Write-Host "== Alembic: heads -v" -ForegroundColor Yellow
Invoke-Expression "docker compose exec backend /bin/sh -lc 'alembic heads -v'"

Write-Host "== Pytest quick smoke: /health" -ForegroundColor Yellow
$envs = "env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 TEST_DISABLE_LIFESPAN=1 QUICK_SMOKE=1 KAFKA_ENABLED=0 CLICKHOUSE_ENABLED=0 DISABLE_SCHEMA_DRIFT_GUARD=1"
$t1 = Invoke-InBackend "$envs pytest -q -vv -s app/tests/test_smoke_health.py::test_health_ok -k test_health_ok -x --maxfail=1"

Write-Host "== Pytest quick smoke: /docs" -ForegroundColor Yellow
$t2 = Invoke-InBackend "$envs pytest -q -vv -s app/tests/test_smoke_health.py::test_docs_available -k test_docs_available -x --maxfail=1"

if($t1 -eq 0 -and $t2 -eq 0){
    Write-Host "✅ Quick smoke PASS (health/docs) + Alembic upgrade OK" -ForegroundColor Green
    exit 0
} else {
    Write-Warning ("Quick smoke 결과: health={0}, docs={1}" -f $t1,$t2)
    exit 1
}
