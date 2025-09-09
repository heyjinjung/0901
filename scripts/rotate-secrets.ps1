param(
    [string]$EnvPath = ".env.production",
    [string]$OutPath = ".env.production.updated",
    [ValidateSet("sync","rotate")] [string]$PostgresMode = "sync",
    [string]$ComposePath = "docker-compose.yml",
    [switch]$DryRun
)

# Utility: Random generators
function New-RandomBase64([int]$bytes = 64) {
    $b = New-Object byte[] $bytes
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($b)
    [Convert]::ToBase64String($b)
}
function New-RandomHex([int]$bytes = 32) {
    $b = New-Object byte[] $bytes
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($b)
    ($b | ForEach-Object { $_.ToString('x2') }) -join ''
}
function Mask([string]$s, [int]$show = 6) {
    if ([string]::IsNullOrWhiteSpace($s)) { return "" }
    if ($s.Length -le $show) { return ('*' * $s.Length) }
    return $s.Substring(0,$show) + ('*' * [Math]::Max(0, $s.Length - $show))
}

Write-Host "[rotate-secrets] 시작: EnvPath=$EnvPath, OutPath=$OutPath, PostgresMode=$PostgresMode" -ForegroundColor Cyan

# Load existing env lines if present
$envLines = @()
if (Test-Path -LiteralPath $EnvPath) {
    $envLines = Get-Content -LiteralPath $EnvPath -ErrorAction Stop
} else {
    Write-Warning "[rotate-secrets] $EnvPath 파일을 찾지 못했습니다. 새 파일 기준으로 생성합니다."
}

# Convert env to dictionary (preserve unknown keys)
$envMap = @{}
foreach ($line in $envLines) {
    if ($line.Trim().StartsWith('#') -or -not $line.Contains('=')) { continue }
    $idx = $line.IndexOf('=')
    $k = $line.Substring(0,$idx).Trim()
    $v = $line.Substring($idx+1)
    $envMap[$k] = $v
}

# Compose parsing for current Postgres password (sync mode)
$currentComposePgPass = $null
if (Test-Path -LiteralPath $ComposePath) {
    try {
        $composeText = Get-Content -LiteralPath $ComposePath -Raw
        $m = [regex]::Match($composeText, "POSTGRES_PASSWORD\s*:\s*([^\r\n#]+)")
        if ($m.Success) { $currentComposePgPass = $m.Groups[1].Value.Trim() }
    } catch { Write-Warning "[rotate-secrets] docker-compose.yml 파싱 실패: $_" }
}

# Plan new values
$newJwtKey = New-RandomBase64 64
$newJwtSecret = New-RandomBase64 64
$newRedisPass = New-RandomHex 32

# Postgres
$newPgPass = $null
$pgNote = ""
if ($PostgresMode -eq 'sync') {
    if ($currentComposePgPass) {
        $newPgPass = $currentComposePgPass
        $pgNote = "compose 값과 동기화"
    } elseif ($envMap.ContainsKey('POSTGRES_PASSWORD')) {
        $newPgPass = $envMap['POSTGRES_PASSWORD']
        $pgNote = ".env 기존값 유지(임시)"
    } else {
        $pgNote = "동기화할 비밀번호를 찾지 못했습니다. 필요 시 -PostgresMode rotate 사용 권장"
    }
} else {
    $newPgPass = New-RandomHex 24
    $pgNote = "로테이션(ALTER ROLE 필요)"
}

# Apply to map (without writing original file)
$envMap['JWT_SECRET_KEY'] = $newJwtKey
$envMap['JWT_SECRET'] = $newJwtSecret
$envMap['REDIS_PASSWORD'] = $newRedisPass
if ($newPgPass) { $envMap['POSTGRES_PASSWORD'] = $newPgPass }

# Ensure helpful defaults exist
if (-not $envMap.ContainsKey('CORS_ORIGINS')) {
    $envMap['CORS_ORIGINS'] = 'http://localhost:3000,http://127.0.0.1:3000'
}

# Rebuild lines preserving comments and unknown keys at top
$knownKeys = @('JWT_SECRET_KEY','JWT_SECRET','REDIS_PASSWORD','POSTGRES_PASSWORD','CORS_ORIGINS')
$outLines = @()
$outLines += "# 생성일: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$outLines += "# 본 파일은 rotate-secrets.ps1로 생성된 업데이트 제안본입니다. 필요한 값만 반영 후 원본 .env.production 으로 교체하세요."
foreach ($k in $knownKeys) {
    if ($envMap.ContainsKey($k)) { $outLines += "$k=$($envMap[$k])" }
}
# Append other keys that existed before
foreach ($kv in $envMap.GetEnumerator() | Where-Object { $knownKeys -notcontains $_.Key }) {
    $outLines += "$($kv.Key)=$($kv.Value)"
}

if ($DryRun) {
    Write-Host "[rotate-secrets] DryRun: 파일을 쓰지 않습니다." -ForegroundColor Yellow
} else {
    $dir = Split-Path -Parent $OutPath
    if ($dir -and -not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
    Set-Content -LiteralPath $OutPath -Value ($outLines -join "`n") -Encoding UTF8
    Write-Host "[rotate-secrets] 생성됨: $OutPath" -ForegroundColor Green
}

# Plan summary (masked)
function SummLine($name, $old, $new) {
    $oldM = if ($null -ne $old) { Mask $old } else { '(없음)' }
    $newM = if ($null -ne $new) { Mask $new } else { '(변경없음)' }
    return ("- {0}: {1} -> {2}" -f $name, $oldM, $newM)
}

$oldJwtKey = $null; if (Test-Path $EnvPath) { $oldJwtKey = (Get-Content $EnvPath | Select-String -Pattern '^JWT_SECRET_KEY=(.*)' | ForEach-Object { $_.Matches[0].Groups[1].Value }) | Select-Object -First 1 }
$oldJwt = $null; if (Test-Path $EnvPath) { $oldJwt = (Get-Content $EnvPath | Select-String -Pattern '^JWT_SECRET=(.*)' | ForEach-Object { $_.Matches[0].Groups[1].Value }) | Select-Object -First 1 }
$oldRedis = $null; if (Test-Path $EnvPath) { $oldRedis = (Get-Content $EnvPath | Select-String -Pattern '^REDIS_PASSWORD=(.*)' | ForEach-Object { $_.Matches[0].Groups[1].Value }) | Select-Object -First 1 }
$oldPg = $null; if (Test-Path $EnvPath) { $oldPg = (Get-Content $EnvPath | Select-String -Pattern '^POSTGRES_PASSWORD=(.*)' | ForEach-Object { $_.Matches[0].Groups[1].Value }) | Select-Object -First 1 }

Write-Host "[rotate-secrets] 변경 요약" -ForegroundColor Cyan
Write-Host (SummLine 'JWT_SECRET_KEY' $oldJwtKey $newJwtKey)
Write-Host (SummLine 'JWT_SECRET' $oldJwt $newJwtSecret)
Write-Host (SummLine 'REDIS_PASSWORD' $oldRedis $newRedisPass)
Write-Host (SummLine "POSTGRES_PASSWORD ($pgNote)" $oldPg $newPgPass)

Write-Host "`n[다음 단계]" -ForegroundColor Cyan
Write-Host "1) $OutPath 내용을 검토 후 .env.production 으로 교체" 
Write-Host "2) 재시작 순서: Redis → Backend" 
Write-Host "3) Postgres가 rotate 모드인 경우 DB에서 ALTER ROLE 로 비밀번호 변경 후 compose/.env 동기화" 
Write-Host "4) 검증: /health 200, /docs 200, 로그인, 요약 스모크 0 fail"

Write-Host "`n[선택 명령어] PowerShell" -ForegroundColor DarkCyan
Write-Host "./docker-manage.ps1 restart redis"
Write-Host "./docker-manage.ps1 restart backend"
Write-Host "./scripts/prod-verify.ps1 -RunSmoke"
