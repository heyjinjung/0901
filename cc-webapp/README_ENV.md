# Casino-Club F2P Docker Compose 환경별 실행 가이드

## 네이밍 규칙
- dev: cc_postgres_dev, cc_redis_dev, cc_backend_dev, cc_kafka_dev, cc_zookeeper_dev
- prod: cc_postgres_prod, cc_redis_prod, cc_backend_prod, cc_kafka_prod, cc_zookeeper_prod

## 환경별 실행법

### 개발 환경(dev)
```sh
docker-compose --env-file .env.dev -f docker-compose.dev.yml up -d
```

### 운영 환경(prod)
```sh
docker-compose --env-file .env.prod -f docker-compose.yml up -d
```

## 환경 변수 관리
- .env.dev: 개발 환경 변수
- .env.prod: 운영 환경 변수

## 주요 참고사항
- 컨테이너/서비스 네이밍은 환경별로 명확히 구분
- 포트/볼륨/네트워크도 dev/prod 분리 권장
- 환경별 compose 파일에서 필요한 서비스만 정의

## 인증/세션 관련 환경변수 (추가)
- JWT_EXPIRE_MINUTES: 액세스 토큰 만료 분 (기본 30)
- MAX_CONCURRENT_SESSIONS: 동시 허용 세션 수 (기본 1). 1일 때 신규 로그인/리프레시 시 이전 세션 비활성화

## 관련 API 엔드포인트 (백엔드)
- POST /api/auth/logout: 현재 토큰 로그아웃(블랙리스트 등록)
- POST /api/auth/logout-all: 모든 세션 로그아웃(현재 토큰 블랙리스트 + 전체 세션 비활성화)
