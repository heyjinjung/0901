# PowerShell script to start the backend with the standard main file
$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path -Parent $scriptPath
Set-Location $scriptDir

Write-Host "Starting backend server (main.py)..."
Set-Location -Path ".\backend"
# 안정적인 개발 환경용 JWT 설정 주입 (로컬 전용)
if (-not $env:JWT_SECRET_KEY -or $env:JWT_SECRET_KEY.Trim().Length -lt 8) {
	$env:JWT_SECRET_KEY = 'secret_key_for_development_only'
}
# 필요 시 서명 검증 우회(세션/흐름 디버깅 목적). 프로덕션 금지.
$env:JWT_DEV_ALLOW_UNVERIFIED = '1'
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
