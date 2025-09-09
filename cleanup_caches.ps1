<#
  Casino-Club F2P 개발 캐시 정리 스크립트
  사용법:
    미리보기:  ./cleanup_caches.ps1 -WhatIf
    전체삭제:  ./cleanup_caches.ps1
    선택패턴:  ./cleanup_caches.ps1 -Patterns "__pycache__",".pytest_cache"
  로그: cleanup_caches.log 에 기록
#>
param(
  [string[]]$Patterns = @(
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".coverage",
    "htmlcov",
    "coverage.xml",
    ".benchmarks",
    ".pytest_cache",
    ".next",
    "dist",
    "build",
    "node_modules/.cache",
    "tsconfig.tsbuildinfo"
  ),
  [switch]$WhatIf
)

$ErrorActionPreference = 'SilentlyContinue'
$logFile = Join-Path -Path (Get-Location) -ChildPath "cleanup_caches.log"
"==== $(Get-Date -Format 'u') 시작 ====" | Out-File -FilePath $logFile -Encoding UTF8 -Append

function Resolve-Targets($pattern) {
  Get-ChildItem -Recurse -Force -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -eq $pattern -or $_.FullName -like "*${pattern}" }
}

$allTargets = @()
foreach ($p in $Patterns) {
  $found = Resolve-Targets $p | Sort-Object -Unique
  foreach ($f in $found) { $allTargets += $f }
}
$allTargets = $allTargets | Sort-Object FullName -Unique

Write-Host "대상 개수:" $allTargets.Count
"패턴: $($Patterns -join ', ')" | Out-File $logFile -Append
"대상 수: $($allTargets.Count)" | Out-File $logFile -Append

foreach ($t in $allTargets) {
  $type = if ($t.PSIsContainer) { 'DIR ' } else { 'FILE' }
  if ($WhatIf) {
    Write-Host "[미리보기] $type -> $($t.FullName)" -ForegroundColor Yellow
  } else {
    try {
      if ($t.PSIsContainer) { Remove-Item -Recurse -Force $t.FullName } else { Remove-Item -Force $t.FullName }
      Write-Host "[삭제] $type -> $($t.FullName)" -ForegroundColor Green
      "REMOVED $type $($t.FullName)" | Out-File $logFile -Append
    } catch {
      Write-Host "[실패] $type -> $($t.FullName) $_" -ForegroundColor Red
      "FAILED $type $($t.FullName) $_" | Out-File $logFile -Append
    }
  }
}

if ($WhatIf) { Write-Host "미리보기 모드: 실제 삭제 없음" -ForegroundColor Cyan }
"==== $(Get-Date -Format 'u') 종료 ====" | Out-File -FilePath $logFile -Append
