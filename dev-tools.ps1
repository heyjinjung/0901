# 카지노 클럽 F2P 프로젝트 개발 환경 스크립트
param(
    [string]$command = "help",
    [switch]$frontend = $false,
    [switch]$backend = $false,
    [switch]$cache = $false,
    [switch]$tools = $false
)

$rootDir = $PSScriptRoot
$frontendDir = Join-Path $rootDir "cc-webapp\frontend"
$backendDir = Join-Path $rootDir "cc-webapp\backend"

function Show-Header {
    Write-Host "🎮 카지노 클럽 F2P 프로젝트 개발 환경 관리 🎮" -ForegroundColor Cyan
    Write-Host "===============================================" -ForegroundColor Cyan
}

function Show-Help {
    Show-Header
    Write-Host "사용법: .\dev-tools.ps1 [command] [options]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "명령어:" -ForegroundColor Yellow
    Write-Host "  help      : 이 도움말을 표시합니다."
    Write-Host "  start     : 개발 서버를 시작합니다."
    Write-Host "  build     : 프로젝트를 빌드합니다."
    Write-Host "  clean     : 캐시 및 임시 파일을 정리합니다."
    Write-Host "  docker    : Docker 컨테이너를 관리합니다."
    Write-Host ""
    Write-Host "옵션:" -ForegroundColor Yellow
    Write-Host "  -frontend : 프론트엔드 작업만 수행합니다."
    Write-Host "  -backend  : 백엔드 작업만 수행합니다."
    Write-Host "  -cache    : 캐시 삭제를 포함합니다."
    Write-Host "  -tools    : 개발 도구를 포함합니다."
}

function Start-Development {
    Show-Header
    Write-Host "🚀 개발 환경 시작 중..." -ForegroundColor Green
    
    if ($frontend -or (-not $frontend -and -not $backend)) {
        Write-Host "📱 프론트엔드 시작 중..." -ForegroundColor Blue
        if ($cache) {
            Write-Host "🧹 프론트엔드 캐시 정리 중..." -ForegroundColor Yellow
            Remove-Item -Path (Join-Path $frontendDir ".next") -Recurse -Force -ErrorAction SilentlyContinue
        }
        Set-Location $frontendDir
        Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "npm run dev"
    }
    
    if ($backend -or (-not $frontend -and -not $backend)) {
        Write-Host "🖥️ 백엔드 시작 중..." -ForegroundColor Blue
        if ($tools) {
            Write-Host "🛠️ Docker 개발 도구 시작 중..." -ForegroundColor Yellow
            & .\docker-manage.ps1 start --tools
        } else {
            & .\docker-manage.ps1 start
        }
    }
}

function Build-Project {
    Show-Header
    Write-Host "🔨 프로젝트 빌드 중..." -ForegroundColor Green
    
    if ($frontend -or (-not $frontend -and -not $backend)) {
        Write-Host "📱 프론트엔드 빌드 중..." -ForegroundColor Blue
        Set-Location $frontendDir
        npm run build
    }
    
    if ($backend -or (-not $frontend -and -not $backend)) {
        Write-Host "🖥️ 백엔드 빌드 중..." -ForegroundColor Blue
        & .\docker-manage.ps1 build
    }
}

function Clean-Project {
    Show-Header
    Write-Host "🧹 프로젝트 정리 중..." -ForegroundColor Green
    
    if ($frontend -or (-not $frontend -and -not $backend)) {
        Write-Host "📱 프론트엔드 캐시 정리 중..." -ForegroundColor Blue
        Remove-Item -Path (Join-Path $frontendDir ".next") -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item -Path (Join-Path $frontendDir "node_modules") -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "✅ 프론트엔드 캐시 정리 완료" -ForegroundColor Green
    }
    
    if ($backend -or (-not $frontend -and -not $backend)) {
        Write-Host "🖥️ 백엔드 캐시 정리 중..." -ForegroundColor Blue
        & .\docker-manage.ps1 clean
        Write-Host "✅ 백엔드 캐시 정리 완료" -ForegroundColor Green
    }
}

function Manage-Docker {
    Show-Header
    Write-Host "🐳 Docker 컨테이너 관리 중..." -ForegroundColor Green
    $dockerArgs = $args
    & .\docker-manage.ps1 $dockerArgs
}

# 메인 로직
switch ($command) {
    "help" { Show-Help }
    "start" { Start-Development }
    "build" { Build-Project }
    "clean" { Clean-Project }
    "docker" { Manage-Docker $args }
    default { 
        Write-Host "❌ 알 수 없는 명령어: $command" -ForegroundColor Red
        Show-Help
    }
}
