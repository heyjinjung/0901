Param(
  [string]$ResultsDir = "test-results",
  [string]$DocPath = "0909.md",
  [switch]$UpdateEvidence
)

function Get-LatestE2ESummary {
  Param([string]$Dir)
  if (!(Test-Path $Dir)) { return $null }
  $files = Get-ChildItem -Path $Dir -Filter *.json | Sort-Object LastWriteTime -Descending
  if (!$files) { return $null }
  foreach ($f in $files) {
    try {
      $json = Get-Content $f.FullName -Raw | ConvertFrom-Json
  if ($null -ne $json.passed -and $null -ne $json.failed -and $null -ne $json.skipped) { return $json }
    } catch { }
  }
  return $null
}

$summary = Get-LatestE2ESummary -Dir $ResultsDir
if (-not $summary) { Write-Host "No summary JSON with passed/failed/skipped found."; exit 0 }
$total = [int]$summary.total
if ($total -eq 0) { $total = [int]$summary.passed + [int]$summary.failed + [int]$summary.skipped }

$passRate = if ($total -gt 0) { [Math]::Round(($summary.passed / $total)*100,1) } else { 0 }

$doc = Get-Content $DocPath -Raw

function Get-LastCommitHashForFile($path) {
  if (!(Test-Path $path)) { return $null }
  $git = "git log -1 --pretty=format:%H -- `"$path`""
  $hash = cmd /c $git 2>$null
  if ($LASTEXITCODE -ne 0) { return $null }
  return $hash
}

function ExtractClaimLines($text) {
  # 19.2 테이블 근거 문서/라인 범위에 지정된 문서명을 기반으로 첫 매칭 라인 번호 산출
  $targets = @{}
  $pattern = '(?m)^\| (overall_max_win.*?|Unified Purchase.*?|DB 제약 정리 필요.*?|이벤트 리워드 플로우 미검증.*?|승/패 파생 JSON 세부 통계 재도입.*?|E2E 실패 3건.*?|Streak/XP 공식 단일화.*?|Idempotency Unique Key 단일화.*?|Follow/Relation/Event 링크 제약 축소.*?|game_stats.user_id NOT NULL 필요).*?$'
  $claimMatches = [System.Text.RegularExpressions.Regex]::Matches($text, $pattern)
  foreach ($m in $claimMatches) {
    $line = ($text.Substring(0,$m.Index) -split "`n").Length
    $targets[$m.Groups[1].Value] = $line
  }
  return $targets
}

if ($UpdateEvidence) {
  Write-Host "[Evidence] 19.2 커밋/라인 자동 주입 실행";
  # TODO: 한글 라인 매칭 인코딩 이슈로 임시 비활성. 후속 개선 예정.
  $claims = @{}
  $fileMap = [ordered]@{}
  $fileMap['overall_max_win'] = '2025-09-09_게임통계_풀스택동기화_완성.md'
  $fileMap['Unified Purchase'] = 'api docs/20250808.md'
  $fileMap['DB 제약 정리 필요'] = '0909데이터베이스.md'
  $fileMap['이벤트 리워드 플로우 미검증'] = '2025-09-06_온보딩_운영_누적학습_요약.md'
  $fileMap['승/패 파생 JSON 세부 통계 재도입'] = '2025-09-09_게임통계_풀스택동기화_완성.md'
  $fileMap['E2E 실패 3건'] = 'E2E_failed_tests_20250909.md'
  $fileMap['Streak/XP 공식 단일화'] = '2025-09-06_온보딩_운영_누적학습_요약.md'
  $fileMap['Idempotency Unique Key 단일화'] = '0909데이터베이스.md'
  $fileMap['Follow/Relation/Event 링크 제약 축소'] = '0909데이터베이스.md'
  $fileMap['game_stats.user_id NOT NULL 필요'] = '0909데이터베이스.md'
  # 기존 테이블 라인 추출
  $tablePattern = '(?s)(### 19.2 변경 근거 매핑 테이블.*?\n)(\| 주장/결정.*?\n)(\| overall_max_win.*?)(\n\n|$)'
  $m = [System.Text.RegularExpressions.Regex]::Match($doc, $tablePattern)
  if ($m.Success) {
    $tableBlock = $m.Groups[3].Value
    $newLines = @()
    foreach ($line in $tableBlock -split "`n") {
      if ($line -notmatch '^\|') { $newLines += $line; continue }
  if ($line -match '^\| (overall_max_win|Unified Purchase|DB 제약 정리 필요|이벤트 리워드 플로우 미검증|승/패 파생 JSON 세부 통계 재도입|E2E 실패 3건|Streak/XP 공식 단일화|Idempotency Unique Key 단일화|Follow/Relation/Event 링크 제약 축소|game_stats.user_id NOT NULL 필요)') {
  $key = $null
        $key = [System.Text.RegularExpressions.Regex]::Match($line,'^\| ([^|]+?) ').Groups[1].Value
        # 키 간략 매핑
        $lookupKey = $key
        if ($lookupKey -like 'overall_max_win*') { $lookupKey = 'overall_max_win' }
        elseif ($lookupKey -like 'Unified Purchase*') { $lookupKey = 'Unified Purchase' }
        elseif ($lookupKey -like 'DB 제약 정리 필요*') { $lookupKey = 'DB 제약 정리 필요' }
        elseif ($lookupKey -like '이벤트 리워드 플로우 미검증*') { $lookupKey = '이벤트 리워드 플로우 미검증' }
        elseif ($lookupKey -like '승/패 파생 JSON 세부 통계 재도입*') { $lookupKey = '승/패 파생 JSON 세부 통계 재도입' }
        elseif ($lookupKey -like 'E2E 실패 3건*') { $lookupKey = 'E2E 실패 3건' }
        elseif ($lookupKey -like 'Streak/XP 공식 단일화*') { $lookupKey = 'Streak/XP 공식 단일화' }
        elseif ($lookupKey -like 'Idempotency Unique Key 단일화*') { $lookupKey = 'Idempotency Unique Key 단일화' }
        elseif ($lookupKey -like 'Follow/Relation/Event 링크 제약 축소*') { $lookupKey = 'Follow/Relation/Event 링크 제약 축소' }
        elseif ($lookupKey -like 'game_stats.user_id NOT NULL 필요*') { $lookupKey = 'game_stats.user_id NOT NULL 필요' }
        $file = $fileMap[$lookupKey]
        $hash = if ($file) { Get-LastCommitHashForFile $file } else { '' }
  $lineRef = ''
        # 커밋 hash7 형식 교체
        $line = [System.Text.RegularExpressions.Regex]::Replace($line,'\| ([^|]+?) \| ([^|]+?) \| ([0-9a-f]{7})?','{ keep }') # 단순 회피
        # 간단히 끝에 주석 형식 추가
        $line = $line + " <!-- $hash $lineRef -->"
      }
      $newLines += $line
    }
    $newBlock = ($newLines -join "`n")
    $doc = $doc.Substring(0,$m.Groups[3].Index) + $newBlock + $doc.Substring($m.Groups[3].Index + $m.Groups[3].Length)
  }
}

# Update Section 21.1 table rows using regex replace
$pattern = '(## 21\. 테스트 게이트[\s\S]*?### 21\.1 현재 E2E 상태 .*?\n)(\| 분류 \|.*?\n)(\| Passed \|).*?(\n\| Total \| .*?\|)'
$newTable = "| 분류 | 수 | 비율 |`n|------|----|------|`n| Passed | $($summary.passed) | $passRate% |`n| Failed | $($summary.failed) | $([Math]::Round(($summary.failed/$total)*100,1))% |`n| Skipped | $($summary.skipped) | $([Math]::Round(($summary.skipped/$total)*100,1))% |`n| Total | $total | 100% |"

$updated = [System.Text.RegularExpressions.Regex]::Replace($doc, $pattern, { param($m) $m.Groups[1].Value + $m.Groups[2].Value + $newTable }, 'Singleline')

if ($updated -ne $doc) { $doc = $updated }
Set-Content -Path $DocPath -Value $doc -Encoding UTF8
Write-Host "0909.md 자동 갱신 완료 (PassRate=$passRate%). Evidence=$($UpdateEvidence.IsPresent)"
