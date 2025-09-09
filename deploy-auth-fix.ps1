#!/usr/bin/env pwsh
# Casino-Club F2P 인증 수정 배포 스크립트
# ==================================================

$ErrorActionPreference = "Stop"

function Write-ColoredOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Show-Header {
    param([string]$Title)
    
    Write-Host "`n" -NoNewline
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host " $Title " -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
}

function Deploy-FixedFiles {
    Show-Header "수정된 파일 배포"
    
    # 복사할 파일 매핑
    $fixedFiles = @{
        "fixed_auth_service.py" = "cc-webapp/backend/app/auth/auth_service.py"
        "fixed_dependencies.py" = "cc-webapp/backend/app/dependencies.py"
    }
    
    foreach ($file in $fixedFiles.GetEnumerator()) {
        $source = Join-Path $PSScriptRoot $file.Key
        $destination = Join-Path $PSScriptRoot $file.Value
        
        if (Test-Path $source) {
            try {
                Write-ColoredOutput "파일 복사 중: $($file.Key) -> $($file.Value)" "Yellow"
                Copy-Item -Path $source -Destination $destination -Force
                Write-ColoredOutput "✅ 성공" "Green"
            }
            catch {
                Write-ColoredOutput "❌ 실패: $_" "Red"
            }
        }
        else {
            Write-ColoredOutput "⚠️ 소스 파일 없음: $source" "Yellow"
        }
    }
    
    # 컨테이너 재시작
    Write-ColoredOutput "`n백엔드 컨테이너 재시작 중..." "Yellow"
    docker restart cc_backend_dev
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColoredOutput "✅ 백엔드 컨테이너 재시작 성공" "Green"
    }
    else {
        Write-ColoredOutput "❌ 백엔드 컨테이너 재시작 실패" "Red"
    }
    
    # 변경 확인을 위한 대기
    Write-ColoredOutput "변경 사항 적용을 위해 10초 대기 중..." "Yellow"
    Start-Sleep -Seconds 10
}

function Run-DiagnosticTest {
    Show-Header "진단 테스트 실행"
    
    $testFile = "jwt_token_debug.py"
    $fullPath = Join-Path $PSScriptRoot $testFile
    
    if (Test-Path $fullPath) {
        Write-ColoredOutput "진단 테스트 실행 중: $testFile" "Yellow"
        
        # Python이 설치되어 있는지 확인
        $pythonExists = Get-Command python -ErrorAction SilentlyContinue
        
        if ($pythonExists) {
            # 로컬에서 실행
            try {
                python $fullPath
                Write-ColoredOutput "`n✅ 테스트 완료" "Green"
            }
            catch {
                Write-ColoredOutput "❌ 테스트 실행 실패: $_" "Red"
            }
        }
        else {
            # 컨테이너에서 실행
            try {
                Write-ColoredOutput "로컬 Python이 없습니다. 컨테이너에서 실행합니다." "Yellow"
                
                # 테스트 파일 복사
                docker cp $fullPath cc_backend_dev:/app/
                
                # 실행
                docker exec cc_backend_dev python /app/$(Split-Path $fullPath -Leaf)
                Write-ColoredOutput "`n✅ 테스트 완료" "Green"
            }
            catch {
                Write-ColoredOutput "❌ 컨테이너에서 테스트 실행 실패: $_" "Red"
            }
        }
    }
    else {
        Write-ColoredOutput "⚠️ 테스트 파일 없음: $fullPath" "Yellow"
    }
}

function Check-Logs {
    Show-Header "로그 확인"
    
    Write-ColoredOutput "백엔드 로그 확인 중..." "Yellow"
    docker logs cc_backend_dev --tail 100 | Select-String -Pattern "\[AUTH\]|\[auth\]|JWT|token|error|Exception" | ForEach-Object {
        Write-ColoredOutput $_ "Magenta"
    }
    
    Write-ColoredOutput "`n계속하려면 아무 키나 누르세요..." "Cyan"
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# 메인 함수
function Main {
    Show-Header "Casino-Club F2P 인증 수정 배포 스크립트"
    
    # 메뉴
    while ($true) {
        Write-Host "`n메뉴:" -ForegroundColor Cyan
        Write-Host "1. 수정된 파일 배포" -ForegroundColor White
        Write-Host "2. 진단 테스트 실행" -ForegroundColor White
        Write-Host "3. 로그 확인" -ForegroundColor White
        Write-Host "4. 종료" -ForegroundColor White
        
        $choice = Read-Host "`n선택"
        
        switch ($choice) {
            "1" { Deploy-FixedFiles }
            "2" { Run-DiagnosticTest }
            "3" { Check-Logs }
            "4" { 
                Write-ColoredOutput "`n스크립트를 종료합니다." "Yellow"
                return 
            }
            default { Write-ColoredOutput "`n잘못된 선택입니다. 다시 시도하세요." "Red" }
        }
    }
}

# 스크립트 실행
Main
