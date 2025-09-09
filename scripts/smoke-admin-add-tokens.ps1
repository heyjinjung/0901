<#
용도: Admin 토큰 추가 API 스모크 테스트
전제:
- 백엔드: http://localhost:8000 기동
- 개발용 elevate 허용 엔드포인트: POST /api/admin/users/elevate
절차:
1) admin1 회원가입→로그인→elevate로 관리자 승격
2) user1 회원가입→로그인
3) 관리자 토큰으로 POST /api/admin/users/{user_id}/tokens/add 호출(JSON 본문)
4) user1 토큰으로 GET /api/users/balance로 new_balance 확인
#>

param(
	[string]$BaseUrl = "http://localhost:8000",
	# 기본값은 실행 시 각기 다른 고유 값으로 대체됨(아래에서 덮어씀)
	[string]$AdminSiteId = "",
	[string]$UserSiteId = "",
	[string]$Password = "passw0rd!",
	[int]$Amount = 777
)

$ErrorActionPreference = 'Stop'

function Wait-Health {
	param(
		[string]$Url,
		[int]$TimeoutSec = 30
	)
	$deadline = (Get-Date).AddSeconds($TimeoutSec)
	while ((Get-Date) -lt $deadline) {
		try {
			$r = Invoke-RestMethod -Method Get -Uri "$Url/health" -TimeoutSec 5
			if ($r.status -and $r.status -eq 'healthy') { return $true }
		} catch {
			Start-Sleep -Seconds 1
		}
	}
	throw "백엔드가 준비되지 않았습니다: $Url/health 응답 없음"
}

function Invoke-JsonPost {
	param([string]$Url, [hashtable]$Body, [hashtable]$Headers)
	$json = $Body | ConvertTo-Json -Depth 6
	return Invoke-RestMethod -Method Post -Uri $Url -ContentType 'application/json' -Body $json -Headers $Headers
}

function SignupLogin {
	param(
		[string]$SiteId,
		[string]$Phone
	)
	# signup (중복이면 무시)
	try {
		Invoke-JsonPost -Url "$BaseUrl/api/auth/signup" -Body @{ site_id=$SiteId; nickname="nick_$SiteId"; password=$Password; invite_code='5858'; phone_number=$Phone } -Headers @{}
	} catch {
		# 회원가입 실패 원인(중복 등)은 로그인 시도로 이어가므로 무시
	}
	try {
		$login = Invoke-JsonPost -Url "$BaseUrl/api/auth/login" -Body @{ site_id=$SiteId; password=$Password } -Headers @{}
	} catch {
		throw "로그인 실패(site_id=$SiteId). 이전에 동일 ID가 다른 비밀번호로 생성되었을 수 있습니다. 새 ID로 재시도하세요. 원인: $($_.Exception.Message)"
	}
	return $login.access_token
}

# 고유 site_id/전화번호 생성(충돌 방지)
$epoch = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
if (-not $AdminSiteId -or $AdminSiteId.Trim().Length -eq 0) { $AdminSiteId = "admin_smoke_$epoch" }
if (-not $UserSiteId -or $UserSiteId.Trim().Length -eq 0) { $UserSiteId = "user_smoke_$epoch" }
$adminPhone = ("010" + (Get-Random -Minimum 100000000 -Maximum 999999999))
$userPhone  = ("010" + (Get-Random -Minimum 100000000 -Maximum 999999999))

Write-Host "[0/5] 백엔드 헬스 체크... ($BaseUrl)" -ForegroundColor Cyan
Wait-Health -Url $BaseUrl -TimeoutSec 30

Write-Host "[1/5] 관리자 계정 준비... ($AdminSiteId)" -ForegroundColor Cyan
$adminAccess = SignupLogin -SiteId $AdminSiteId -Phone $adminPhone

Write-Host "[2/5] 관리자 승격(dev elevate)..." -ForegroundColor Cyan
Invoke-JsonPost -Url "$BaseUrl/api/admin/users/elevate" -Body @{ site_id=$AdminSiteId } -Headers @{}

# 재로그인(권한 클레임 업데이트 보장)
$adminAccess = SignupLogin -SiteId $AdminSiteId -Phone $adminPhone
$adminHeaders = @{ Authorization = "Bearer $adminAccess" }

Write-Host "[3/5] 일반 사용자 생성... ($UserSiteId)" -ForegroundColor Cyan
$userAccess = SignupLogin -SiteId $UserSiteId -Phone $userPhone
$userHeaders = @{ Authorization = "Bearer $userAccess" }

# userId 조회 (자기 프로필)
# Debug: show token basics and decoded payload (no verification)
try {
	$dbgTok = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/auth/debug/token" -Headers $userHeaders
	Write-Host "[DEBUG] user token length=$($dbgTok.length) prefix=$($dbgTok.prefix)" -ForegroundColor DarkGray
	$dbgDec = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/auth/debug/decode" -Headers $userHeaders
	Write-Host "[DEBUG] user payload: $((($dbgDec.payload) | ConvertTo-Json -Depth 6))" -ForegroundColor DarkGray
	$dbgVer = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/auth/debug/verify" -Headers $userHeaders
	Write-Host "[DEBUG] verify: $((($dbgVer) | ConvertTo-Json -Depth 6))" -ForegroundColor DarkGray
	$dbgSig = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/auth/debug/sig" -Headers $userHeaders
	Write-Host "[DEBUG] sig: $((($dbgSig) | ConvertTo-Json -Depth 6))" -ForegroundColor DarkGray
	$dbgGuess = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/auth/debug/sig-guess" -Headers $userHeaders
	Write-Host "[DEBUG] sig-guess: $((($dbgGuess) | ConvertTo-Json -Depth 6))" -ForegroundColor DarkGray
	$serverTok = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/auth/debug/make"
	Write-Host "[DEBUG] server token len=$($serverTok.token.Length)" -ForegroundColor DarkGray
	$serverHdr = @{ Authorization = "Bearer $($serverTok.token)" }
	$serverSig = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/auth/debug/sig" -Headers $serverHdr
	Write-Host "[DEBUG] server sig: $((($serverSig) | ConvertTo-Json -Depth 6))" -ForegroundColor DarkGray
} catch {
	Write-Host "[DEBUG] token debug endpoints failed: $($_.Exception.Message)" -ForegroundColor DarkGray
}
$me = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/users/profile" -Headers $userHeaders
$userId = $me.id
Write-Host "대상 사용자 ID: $userId" -ForegroundColor Yellow

Write-Host "[4/5] 관리자 토큰 추가 호출..." -ForegroundColor Cyan
$resp = Invoke-JsonPost -Url "$BaseUrl/api/admin/users/$userId/tokens/add" -Body @{ amount=$Amount; reason='smoke' } -Headers $adminHeaders
$resp | ConvertTo-Json -Depth 6 | Write-Output

if (-not $resp.success) { throw "관리자 토큰 추가 실패" }

Write-Host "[5/5] 사용자 잔액 확인..." -ForegroundColor Cyan
$bal = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/users/balance" -Headers $userHeaders
$bal | ConvertTo-Json -Depth 6 | Write-Output

if ($bal.cyber_token_balance -lt $Amount) {
	throw "잔액 검증 실패: 기대 >= $Amount, 실제 $($bal.cyber_token_balance)"
}

Write-Host "✅ 스모크 성공: user_id=$userId, 증가량=$Amount, 현재잔액=$($bal.cyber_token_balance)" -ForegroundColor Green
