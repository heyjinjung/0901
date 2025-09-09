param(
  [Parameter(Mandatory=$true)]
  [string]$SourceEnvPath,
  [string]$TargetEnvPath = ".env.production"
)

Set-StrictMode -Version 2
$ErrorActionPreference = 'Stop'

function Write-Info($m){ Write-Host "[apply-prod-env] $m" -ForegroundColor Cyan }
function Write-Err($m){ Write-Host "[apply-prod-env] $m" -ForegroundColor Red }

if (-not (Test-Path -LiteralPath $SourceEnvPath)) {
  Write-Err "원본 파일을 찾을 수 없습니다: $SourceEnvPath"
  exit 2
}

if (Test-Path -LiteralPath $TargetEnvPath) {
  $ts = Get-Date -Format "yyyyMMdd_HHmmss"
  $backup = "$TargetEnvPath.bak_$ts"
  Copy-Item -LiteralPath $TargetEnvPath -Destination $backup -Force
  Write-Info "기존 파일 백업 완료: $backup"
}

Copy-Item -LiteralPath $SourceEnvPath -Destination $TargetEnvPath -Force
Write-Info "교체 완료: $TargetEnvPath <= $SourceEnvPath"
exit 0
