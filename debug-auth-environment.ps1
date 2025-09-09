#!/usr/bin/env pwsh
# Casino-Club F2P Authentication Debug Environment
# ==================================================
# This script sets up a debugging environment for JWT authentication in the Docker containers

# 설정
$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
$LogFile = "$ScriptRoot\auth_debug.log"

# 로그 함수
function Write-Log {
    param([string]$Message, [string]$Color = "White")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    
    # 콘솔에 출력
    Write-Host $logMessage -ForegroundColor $Color
    
    # 로그 파일에 저장
    Add-Content -Path $LogFile -Value $logMessage
}

function Show-Header {
    param([string]$Title)
    
    Write-Host "`n" -NoNewline
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host " $Title " -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
    
    # 로그 파일에 저장
    $separator = "=" * 80
    Add-Content -Path $LogFile -Value "`n$separator`n $Title `n$separator"
}

function Test-DockerRunning {
    try {
        $result = docker info 2>&1
        if ($LASTEXITCODE -ne 0) {
            return $false
        }
        return $true
    }
    catch {
        return $false
    }
}

function Setup-Environment {
    Show-Header "환경 설정"
    
    # Docker가 실행 중인지 확인
    Write-Log "Docker 상태 확인 중..." "Yellow"
    if (-not (Test-DockerRunning)) {
        Write-Log "Docker가 실행되고 있지 않습니다. Docker Desktop을 시작하세요." "Red"
        exit 1
    }
    Write-Log "Docker가 실행 중입니다." "Green"
    
    # 디렉토리 확인
    Write-Log "디렉토리 구조 확인 중..." "Yellow"
    $requiredDirs = @("cc-webapp", "cc-webapp\backend", "cc-webapp\frontend")
    foreach ($dir in $requiredDirs) {
        $fullPath = Join-Path $ScriptRoot $dir
        if (-not (Test-Path $fullPath -PathType Container)) {
            Write-Log "필수 디렉토리가 없습니다: $fullPath" "Red"
            exit 1
        }
    }
    Write-Log "디렉토리 구조가 올바릅니다." "Green"
    
    # 로그 디렉토리 생성
    $logDirs = @("logs", "logs\backend", "logs\frontend", "logs\postgres", "logs\celery")
    foreach ($dir in $logDirs) {
        $fullPath = Join-Path $ScriptRoot $dir
        if (-not (Test-Path $fullPath -PathType Container)) {
            New-Item -Path $fullPath -ItemType Directory -Force | Out-Null
            Write-Log "로그 디렉토리 생성됨: $fullPath" "Yellow"
        }
    }
}

function Start-Containers {
    Show-Header "Docker 컨테이너 시작"
    
    # 컨테이너 상태 확인
    Write-Log "기존 컨테이너 확인 중..." "Yellow"
    $containers = docker ps -a --format "{{.Names}}" | Select-String -Pattern "cc_" | ForEach-Object { $_.ToString() }
    
    # 컨테이너 정리
    if ($containers.Count -gt 0) {
        Write-Log "기존 Casino-Club 컨테이너를 중지 및 제거합니다..." "Yellow"
        docker-compose down 2>&1 | Out-Null
    }
    
    # 컨테이너 시작
    Write-Log "컨테이너를 시작합니다... (개발 환경 오버라이드 사용)" "Yellow"
    $startResult = docker-compose -f docker-compose.yml -f docker-compose.override.dev.yml up -d
    
    if ($LASTEXITCODE -ne 0) {
        Write-Log "컨테이너 시작 실패" "Red"
        Write-Log $startResult "Red"
        exit 1
    }
    
    Write-Log "컨테이너가 시작되었습니다." "Green"
    
    # 백엔드가 준비될 때까지 대기
    Write-Log "백엔드가 준비될 때까지 대기합니다..." "Yellow"
    $maxRetries = 30
    $retries = 0
    $backendReady = $false
    
    while (-not $backendReady -and $retries -lt $maxRetries) {
        Start-Sleep -Seconds 5
        $retries++
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                $backendReady = $true
                Write-Log "백엔드가 준비되었습니다. ($retries번 시도 후)" "Green"
            }
        }
        catch {
            Write-Log "백엔드 준비 대기 중... ($retries/$maxRetries)" "Yellow"
        }
    }
    
    if (-not $backendReady) {
        Write-Log "백엔드가 준비되지 않았습니다. 직접 상태를 확인하세요." "Red"
    }
    
    # 컨테이너 목록 출력
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Out-String | Write-Log
}

function Update-AuthFiles {
    Show-Header "인증 파일 업데이트"
    
    $authFiles = @{
        "dependencies.py.new" = "cc-webapp/backend/app/dependencies.py"
        "auth_service.py.new" = "cc-webapp/backend/app/auth/auth_service.py"
        "user.py.new" = "cc-webapp/backend/app/schemas/user.py"
    }
    
    foreach ($file in $authFiles.GetEnumerator()) {
        $source = Join-Path $ScriptRoot $file.Key
        $destination = Join-Path $ScriptRoot $file.Value
        
        if (Test-Path $source) {
            try {
                Copy-Item -Path $source -Destination $destination -Force
                Write-Log "파일 업데이트됨: $($file.Value)" "Green"
            }
            catch {
                Write-Log "파일 업데이트 실패: $($file.Value)" "Red"
                Write-Log $_.Exception.Message "Red"
            }
        }
        else {
            Write-Log "소스 파일 없음: $source" "Yellow"
        }
    }
    
    # 컨테이너 재시작
    Write-Log "백엔드 컨테이너를 재시작합니다..." "Yellow"
    docker restart cc_backend_dev
    
    # 백엔드가 준비될 때까지 대기
    Write-Log "백엔드가 다시 준비될 때까지 대기합니다..." "Yellow"
    Start-Sleep -Seconds 10
}

function Run-Tests {
    Show-Header "인증 테스트 실행"
    
    $testFiles = @(
        "complete_auth_test.py",
        "jwt_token_test.py",
        "auth_flow_test.py"
    )
    
    foreach ($testFile in $testFiles) {
        $fullPath = Join-Path $ScriptRoot $testFile
        
        if (Test-Path $fullPath) {
            Write-Log "테스트 실행: $testFile" "Yellow"
            
            # Python이 설치되어 있는지 확인
            $pythonExists = Get-Command python -ErrorAction SilentlyContinue
            
            if ($pythonExists) {
                # 현재 PowerShell 세션에서 직접 실행
                try {
                    $output = python $fullPath
                    Write-Log "===== $testFile 실행 결과 =====" "Cyan"
                    $output | Write-Log
                }
                catch {
                    Write-Log "테스트 실행 실패: $testFile" "Red"
                    Write-Log $_.Exception.Message "Red"
                }
            }
            else {
                # Docker 컨테이너 내에서 실행
                try {
                    Write-Log "호스트에 Python이 없습니다. 컨테이너에서 실행합니다." "Yellow"
                    
                    # 백엔드 컨테이너로 테스트 파일 복사
                    docker cp $fullPath cc_backend_dev:/app/
                    
                    # 컨테이너 내에서 실행
                    $output = docker exec cc_backend_dev python /app/$(Split-Path $fullPath -Leaf)
                    Write-Log "===== $testFile 실행 결과 =====" "Cyan"
                    $output | Write-Log
                }
                catch {
                    Write-Log "컨테이너에서 테스트 실행 실패: $testFile" "Red"
                    Write-Log $_.Exception.Message "Red"
                }
            }
        }
        else {
            Write-Log "테스트 파일 없음: $fullPath" "Yellow"
        }
    }
}

function Debug-Logs {
    Show-Header "로그 확인"
    
    # 백엔드 로그 확인
    Write-Log "백엔드 컨테이너 로그 확인 중..." "Yellow"
    docker logs cc_backend_dev --tail 100 2>&1 | Select-String -Pattern "error|exception|AUTH|auth|token|jwt|Bearer|401|403|500|debug|인증|토큰" | ForEach-Object {
        Write-Log $_ "Magenta"
    }
}

# 메인 실행 로직
function Main {
    Show-Header "Casino-Club F2P 인증 디버깅 환경 설정"
    
    # 로그 초기화
    if (Test-Path $LogFile) {
        Clear-Content $LogFile
    }
    
    # 환경 설정
    Setup-Environment
    
    # 컨테이너 시작
    Start-Containers
    
    # 인증 파일 업데이트
    Update-AuthFiles
    
    # 테스트 실행
    Run-Tests
    
    # 로그 분석
    Debug-Logs
    
    Show-Header "디버깅 환경 설정 완료"
    Write-Log "모든 단계가 완료되었습니다." "Green"
    Write-Log "로그 파일: $LogFile" "Cyan"
}

# 스크립트 실행
Main
