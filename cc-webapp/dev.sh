#!/bin/bash

# 개발 서버 관리 스크립트

case "$1" in
    "start")
        echo "🚀 개발 서버 시작..."
        docker-compose -f docker-compose.dev.yml up -d
        echo "✅ 서버 시작 완료!"
        echo "📊 상태 확인: ./dev.sh status"
        ;;
    "stop")
        echo "🛑 개발 서버 중지..."
        docker-compose -f docker-compose.dev.yml down
        echo "✅ 서버 중지 완료!"
        ;;
    "restart")
        echo "🔄 개발 서버 재시작..."
        docker-compose -f docker-compose.dev.yml down
        docker-compose -f docker-compose.dev.yml up -d --build
        echo "✅ 재시작 완료!"
        ;;
    "logs")
        echo "📝 실시간 로그 확인 (Ctrl+C로 종료)"
        docker-compose -f docker-compose.dev.yml logs -f
        ;;
    "backend-logs")
        echo "📝 백엔드 로그 확인 (Ctrl+C로 종료)"
        docker-compose -f docker-compose.dev.yml logs -f backend
        ;;
    "frontend-logs")
        echo "📝 프론트엔드 로그 확인 (Ctrl+C로 종료)"
        docker-compose -f docker-compose.dev.yml logs -f frontend
        ;;
    "status")
        echo "📊 서비스 상태:"
        docker-compose -f docker-compose.dev.yml ps
        ;;
    "rebuild")
        echo "🔨 전체 재빌드..."
        docker-compose -f docker-compose.dev.yml down
        docker-compose -f docker-compose.dev.yml up -d --build --force-recreate
        echo "✅ 재빌드 완료!"
        ;;
    *)
        echo "🎮 Casino-Club F2P 개발 서버 관리"
        echo "================================"
        echo "사용법: ./dev.sh [명령]"
        echo ""
        echo "명령어:"
        echo "  start         - 개발 서버 시작"
        echo "  stop          - 개발 서버 중지"
        echo "  restart       - 개발 서버 재시작 (코드 변경시 불필요)"
        echo "  logs          - 전체 실시간 로그"
        echo "  backend-logs  - 백엔드 로그만"
        echo "  frontend-logs - 프론트엔드 로그만"
        echo "  status        - 서비스 상태 확인"
        echo "  rebuild       - 강제 재빌드 (패키지 변경시)"
        echo ""
        echo "🔥 Hot Reload 활성화: 코드 수정시 자동 반영!"
        ;;
esac
