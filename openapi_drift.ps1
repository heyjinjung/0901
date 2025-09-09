Param(
  [string]$ExportCmd = 'python -m app.export_openapi',
  [string]$BackendPath = 'cc-webapp/backend',
  [string]$OutputFile = 'current_openapi.json',
  [string]$ChangeLog = 'docs/change-log.json'
)

function Initialize-FileIfMissing($path, $defaultJson) {
  if (!(Test-Path $path)) { $defaultJson | Set-Content -Path $path -Encoding UTF8 }
}

# 1. 기존 파일 존재 여부 확인
$fullOut = Join-Path $BackendPath $OutputFile
if (!(Test-Path $fullOut)) { Write-Host "기존 OpenAPI 파일 없음: $fullOut" }

# 2. 임시 새 파일 경로
$temp = Join-Path $BackendPath ("_temp_" + [guid]::NewGuid().ToString() + '.json')

Push-Location $BackendPath
try {
  Write-Host "OpenAPI export 실행..."
  cmd /c $ExportCmd > $null 2>&1
  if (!(Test-Path $fullOut)) { Write-Host "Export 산출물 미발견: $fullOut"; exit 1 }
  Copy-Item $fullOut $temp
} finally {
  Pop-Location
}

# 3. diff 비교
if (Test-Path $fullOut -and (Test-Path $temp)) {
  $oldHash = (Get-FileHash $fullOut -Algorithm SHA256).Hash
  $newHash = (Get-FileHash $temp -Algorithm SHA256).Hash
  if ($oldHash -ne $newHash) {
    Write-Host "변경 감지: OpenAPI drift 발생"
    $oldLines = Get-Content $fullOut
    $newLines = Get-Content $temp
    $diff = Compare-Object $oldLines $newLines -SyncWindow 3 | Select-Object -First 200
    $entry = [ordered]@{
      timestamp = (Get-Date).ToString('s')
      old_hash = $oldHash
      new_hash = $newHash
      adds = ($diff | Where-Object {$_.SideIndicator -eq '=>'} | Select-Object -ExpandProperty InputObject)
      removes = ($diff | Where-Object {$_.SideIndicator -eq '<='} | Select-Object -ExpandProperty InputObject)
    }
  Initialize-FileIfMissing $ChangeLog '[]'
    $logJson = Get-Content $ChangeLog -Raw | ConvertFrom-Json
    $logJson += (New-Object psobject -Property $entry)
    ($logJson | ConvertTo-Json -Depth 5) | Set-Content -Path $ChangeLog -Encoding UTF8
    # 새 파일로 교체
    Copy-Item $temp $fullOut -Force
    Write-Host "change-log.json 업데이트 완료"
  } else {
    Write-Host "변경 없음 (hash 동일)"
  }
}
Remove-Item $temp -ErrorAction SilentlyContinue
