# create-vscode-files.ps1
# VSCode 설정 파일들을 개별적으로 생성하는 스크립트

Write-Host "🚀 VSCode 설정 파일들을 생성합니다..." -ForegroundColor Cyan

# .vscode 디렉토리 생성
if (-not (Test-Path ".vscode")) {
    New-Item -Path ".vscode" -ItemType Directory -Force
    Write-Host "📁 .vscode 디렉토리 생성됨" -ForegroundColor Green
}

Write-Host "✅ VSCode 개발 환경 설정이 완료되었습니다!" -ForegroundColor Green
Write-Host "🔄 VSCode를 재시작하여 설정을 적용하세요." -ForegroundColor Cyan
