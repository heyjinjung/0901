Param(
  [string]$EnvPath = ".env.production"
)

if (!(Test-Path $EnvPath)) {
  Write-Error "파일 없음: $EnvPath"; exit 2
}

$lines = Get-Content -Path $EnvPath -ErrorAction Stop
$envMap = @{}
foreach ($l in $lines) {
  if ([string]::IsNullOrWhiteSpace($l)) { continue }
  if ($l.Trim().StartsWith('#')) { continue }
  $ix = $l.IndexOf('=')
  if ($ix -lt 1) { continue }
  $k = $l.Substring(0,$ix).Trim()
  $v = $l.Substring($ix+1).Trim()
  $envMap[$k] = $v
}

$issues = @()
function Add-Issue([string]$msg) { $script:issues += $msg }

# Helper: weak/placeholder checks
function Test-Placeholder([string]$v) {
  if ([string]::IsNullOrWhiteSpace($v)) { return $true }
  $pats = @('secure_password_here','super_secure_production_key_here','change_this_for_prod','your-domain.com')
  foreach ($p in $pats) { if ($v -like "*${p}*") { return $true } }
  return $false
}

function Test-WeakSecret([string]$v) {
  if ([string]::IsNullOrWhiteSpace($v)) { return $true }
  if ($v.Length -lt 32) { return $true }
  if ($v -match '^[A-Za-z0-9+/=\-_.]{0,}$' -and $v.Length -lt 48) { return $true } # overly short simple set
  return $false
}

# Required keys
$required = @('JWT_SECRET_KEY','POSTGRES_PASSWORD','REDIS_PASSWORD')
foreach ($k in $required) {
  if (-not $envMap.ContainsKey($k)) { Add-Issue "누락: $k"; continue }
  $v = $envMap[$k]
  if (Test-Placeholder $v) { Add-Issue "플레이스홀더 값 감지: $k" }
  elseif (Test-WeakSecret $v) { Add-Issue "약한 시크릿: $k (32자 이상 권장)" }
}

# JWT_SECRET(optional) present but should not be placeholder/weak
if ($envMap.ContainsKey('JWT_SECRET')) {
  $v = $envMap['JWT_SECRET']
  if (Test-Placeholder $v) { Add-Issue "플레이스홀더 값 감지: JWT_SECRET" }
  elseif (Test-WeakSecret $v) { Add-Issue "약한 시크릿: JWT_SECRET (32자 이상 권장)" }
}

# DATABASE_URL should not contain secure_password_here
if ($envMap.ContainsKey('DATABASE_URL')) {
  $v = $envMap['DATABASE_URL']
  if (Test-Placeholder $v) { Add-Issue "플레이스홀더 값 감지: DATABASE_URL(비밀번호/호스트/DB명 교체 필요)" }
}

# Kafka: if enabled, bootstrap must not be placeholder-like
if ($envMap.ContainsKey('KAFKA_ENABLED') -and $envMap['KAFKA_ENABLED'] -in @('1','true','TRUE')) {
  if (-not $envMap.ContainsKey('KAFKA_BOOTSTRAP_SERVERS')) {
    Add-Issue "누락: KAFKA_BOOTSTRAP_SERVERS (KAFKA_ENABLED=1)"
  }
}

# Cross checks
if ($envMap.ContainsKey('JWT_SECRET_KEY') -and $envMap.ContainsKey('JWT_SECRET')) {
  if ($envMap['JWT_SECRET_KEY'] -eq $envMap['JWT_SECRET']) {
    Add-Issue "경고: JWT_SECRET_KEY와 JWT_SECRET이 동일 — 분리 권장"
  }
}

if ($issues.Count -eq 0) {
  Write-Host "[PASS] .env.production 시크릿 점검: 이상 없음" -ForegroundColor Green
  exit 0
}
else {
  Write-Host ("[FAIL] .env.production 시크릿 점검: {0}건" -f $issues.Count) -ForegroundColor Yellow
  foreach ($i in $issues) { Write-Host (" - {0}" -f $i) }
  exit 1
}
