#!/bin/bash

echo "🎮 Casino-Club F2P SSH 서버 완전 자동 설치 & 실행"
echo "=================================================="

# 기본 환경 체크
echo "🔍 환경 확인 중..."

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다."
    echo "💡 다음 명령어를 먼저 실행하세요:"
    echo "   curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh"
    exit 1
fi

# Docker Compose 설치 확인
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose가 설치되지 않았습니다."
    echo "💡 다음 명령어를 먼저 실행하세요:"
    echo '   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose'
    echo "   sudo chmod +x /usr/local/bin/docker-compose"
    exit 1
fi

echo "✅ Docker 환경 확인 완료"

# 실행 권한 부여
chmod +x dev.sh 2>/dev/null
chmod +x deploy_ssh.sh 2>/dev/null

# 기존 컨테이너 정리
echo "🧹 기존 컨테이너 정리 중..."
docker-compose -f docker-compose.dev.yml down 2>/dev/null

# 환경 변수 로드
if [ -f .env.dev ]; then
    export $(cat .env.dev | grep -v '#' | awk '/=/ {print $1}')
    echo "✅ 환경변수 로드 완료"
else
    echo "⚠️  .env.dev 파일이 없습니다. 기본값을 사용합니다."
fi

# 이미지 빌드 및 컨테이너 시작
echo "🔨 Docker 이미지 빌드 및 컨테이너 시작 중..."
docker-compose -f docker-compose.dev.yml up -d --build

# 컨테이너 상태 확인
echo "⏳ 서비스 시작 대기 중... (30초)"
sleep 30

echo "📊 컨테이너 상태 확인:"
docker-compose -f docker-compose.dev.yml ps

# 서비스 헬스체크
echo ""
echo "🏥 서비스 헬스체크:"

# 백엔드 확인
if curl -f http://localhost:${BACKEND_PORT:-8000}/docs > /dev/null 2>&1; then
    echo "✅ 백엔드 API: 정상 동작"
else
    echo "❌ 백엔드 API: 연결 실패"
fi

# 프론트엔드 확인
if curl -f http://localhost:${FRONTEND_PORT:-3000} > /dev/null 2>&1; then
    echo "✅ 프론트엔드: 정상 동작"
else
    echo "❌ 프론트엔드: 연결 실패"
fi

# 최종 정보 출력
echo ""
echo "🎉 배포 완료!"
echo "🌐 접근 주소:"
echo "  - 프론트엔드:     http://$(hostname -I | awk '{print $1}'):${FRONTEND_PORT:-3000}"
echo "  - 백엔드 API:     http://$(hostname -I | awk '{print $1}'):${BACKEND_PORT:-8000}"
echo "  - API 문서:       http://$(hostname -I | awk '{print $1}'):${BACKEND_PORT:-8000}/docs"
echo "  - 관리자 페이지:  http://$(hostname -I | awk '{print $1}'):${FRONTEND_PORT:-3000}/admin/users"
echo "  - DB 관리도구:    http://$(hostname -I | awk '{print $1}'):${ADMINER_PORT:-8080}"
echo ""
echo "🔧 개발 명령어:"
echo "  - 실시간 로그:    ./dev.sh logs"
echo "  - 서비스 상태:    ./dev.sh status"
echo "  - 서버 중지:      ./dev.sh stop"
echo ""
echo "🚨 방화벽 포트 열기 (필요시):"
echo "  sudo ufw allow ${FRONTEND_PORT:-3000}/tcp"
echo "  sudo ufw allow ${BACKEND_PORT:-8000}/tcp"
echo "  sudo ufw allow ${ADMINER_PORT:-8080}/tcp"
