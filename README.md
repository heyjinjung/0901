# 🎰 Casino-Club F2P

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org/)

**Casino-Club F2P**는 차세대 F2P (Free-to-Play) 카지노 플랫폼입니다. 
사용자 참여도와 수익화를 극대화하기 위한 도파민 루프, 행동 중독 메커니즘, 데이터 기반 개인화를 통해 설계되었습니다.

## 🌟 주요 특징

### 🎮 게임 시스템
- **슬롯머신**: 가변 비율 보상 시스템
- **룰렛**: 실시간 멀티플레이어 경험
- **가챠 시스템**: 확률 기반 럭키박스
- **가위바위보**: 빠른 베팅 게임

### 💎 경제 시스템
- **이중 화폐**: 일반 코인 & 프리미엄 젬
- **배틀패스**: 무료/유료 트랙 시스템
- **VIP 시스템**: 계층별 혜택
- **성인 콘텐츠**: 단계별 언락 시스템

### 🧠 개인화 시스템
- **RFM 분석**: 최신성, 빈도, 금액 기반 사용자 세분화
- **사이코메트릭 퀴즈**: 위험 성향 측정
- **실시간 추천**: AI 기반 개인화 콘텐츠
- **감정 피드백**: 도파민 루프 최적화

### 📱 기술 스택
- **프론트엔드**: Next.js 15.4.5, React.js, TypeScript, Tailwind CSS v4, Framer Motion
- **백엔드**: FastAPI, Python 3.11, SQLAlchemy, Pydantic
- **데이터베이스**: PostgreSQL 14, Redis 7
- **메시징**: Apache Kafka + Zookeeper
- **배경 작업**: Celery + Beat
- **컨테이너**: Docker Compose
- **테스트**: Pytest, Jest, React Testing Library

## 🚀 빠른 시작

### 필수 요구사항
- Docker & Docker Compose
- Git
- Windows PowerShell (Windows 환경)

### 1. 프로젝트 클론
```bash
git clone https://github.com/mamam1281/auto7777.git
cd auto7777
```

### 2. 환경 설정 및 실행
```powershell
# 개발환경 체크
.\docker-manage.ps1 check

# 초기 설정 (디렉토리 생성, 이미지 빌드)
.\docker-manage.ps1 setup

# 서비스 시작 (개발 도구 포함)
.\docker-manage.ps1 start --tools
```

> 참고: 루트에 `.env`가 없고 `.env.development`만 있을 경우, `cc-manage.ps1`가 자동으로 `.env`를 생성합니다.

### 3. 서비스 접근
- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
 - **OpenAPI 스펙 (Canonical)**: `cc-webapp/backend/current_openapi.json`
- **pgAdmin**: http://localhost:5050
- **Redis Commander**: http://localhost:8081
- **Kafka UI**: http://localhost:8082

## 🏗️ 프로젝트 구조

```
auto7777/
├── docker-manage.ps1                 # Docker 관리 스크립트
├── docker-compose.yml               # 메인 Docker 구성
├── docker-compose.override.dev.yml  # 개발환경 오버라이드
├── .env.development                 # 개발환경 변수
├── cc-webapp/
│   ├── backend/                     # FastAPI 백엔드
│   │   ├── app/
│   │   │   ├── api/                 # API 라우터
│   │   │   ├── core/                # 핵심 설정
│   │   │   ├── models/              # SQLAlchemy 모델
│   │   │   ├── schemas/             # Pydantic 스키마
│   │   │   ├── services/            # 비즈니스 로직
│   │   │   └── utils/               # 유틸리티
│   │   ├── tests/                   # 백엔드 테스트
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── frontend/                    # Next.js 프론트엔드
│       ├── app/                     # App Router
│       ├── components/              # React 컴포넌트
│       │   ├── games/               # 게임 컴포넌트
│       │   ├── profile/             # 프로필 시스템
│       │   └── ui/                  # UI 컴포넌트
│       ├── public/
│       │   └── images/
│       │       ├── avatars/         # 아바타 이미지
│       │       ├── games/           # 게임 아이콘
│       │       └── streaming/       # 스트리밍 썸네일
│       ├── styles/                  # 글로벌 스타일
│       ├── utils/                   # 유틸리티 함수
│       ├── package.json
│       └── Dockerfile
├── logs/                           # 서비스 로그
└── data/                           # 데이터 볼륨
```

## 🛠️ 개발 가이드

### 일일 개발 루틴
```powershell
# 1. 서비스 상태 확인
.\docker-manage.ps1 status

# 2. 개발 서버 시작
.\docker-manage.ps1 start --tools

# 3. 백엔드 개발 (컨테이너 진입)
.\docker-manage.ps1 shell backend

# 4. 프론트엔드 개발 (컨테이너 진입)
.\docker-manage.ps1 shell frontend

# 5. 로그 모니터링
.\docker-manage.ps1 logs backend
.\docker-manage.ps1 logs frontend

# 6. 테스트 실행
.\docker-manage.ps1 test coverage
```

### 데이터베이스 관리
```powershell
# 마이그레이션 실행
.\docker-manage.ps1 migrate

# 테스트 데이터 시드
.\docker-manage.ps1 seed

# 데이터베이스 백업
.\docker-manage.ps1 backup

# 데이터베이스 리셋
.\docker-manage.ps1 reset-db
```

### 테스트
```powershell
# 전체 테스트 스위트
.\docker-manage.ps1 test

# 백엔드 테스트 (커버리지 포함)
.\docker-manage.ps1 test coverage

# 프론트엔드 테스트
.\docker-manage.ps1 test frontend
```

### OpenAPI 스펙 내보내기
컨테이너 내부에서 FastAPI의 app.openapi()를 호출해 최신 스펙을 생성합니다.

```powershell
docker exec cc_backend python -m app.export_openapi
# 출력: cc-webapp/backend/current_openapi.json
```

## 🎨 디자인 시스템

### 테마: Futuristic Neon Cyberpunk
- **색상 팔레트**: 네온 퍼플, 골드, 핑크 액센트
- **다크 모드**: 기본 테마
- **애니메이션**: Framer Motion 기반 유려한 전환
- **반응형**: Desktop 3열, Mobile 1열

### 핵심 컴포넌트
- **게임 카드**: 호버 효과와 네온 글로우
- **아바타 시스템**: 8가지 캐릭터 타입
- **스트리밍 화면**: VJ 상호작용 시스템
- **게임 팝업**: 독립적인 고정 크기 창

## 🧪 핵심 시스템

### 1. 도파민 루프 메커니즘
- **가변 비율 보상**: 예측 불가능한 보상 타이밍
- **니어 미스 효과**: "거의 당첨" 시각적 피드백
- **연속 플레이 유도**: 스트릭 보너스 시스템

### 2. 데이터 기반 개인화
```python
# RFM 세분화 예시
def calculate_rfm_segment(user_actions):
    recency = days_since_last_action(user_actions)
    frequency = action_count_last_30_days(user_actions)
    monetary = total_spent_last_30_days(user_actions)
    
    if monetary > 10000 and frequency > 20:
        return "WHALE"
    elif frequency > 10:
        return "HIGH_ENGAGED"
    # ... 추가 세분화 로직
```

## CI / 컨테이너화된 Playwright E2E 실행

리포지토리는 Playwright 기반 E2E를 GitHub Actions와 컨테이너로 실행할 수 있는 간단한 워크플로와 실행 이미지를 포함합니다.

- 워크플로: `.github/workflows/playwright-e2e.yml` (push/PR on main)
- 컨테이너: `ci/playwright/Dockerfile` 와 `ci/playwright/run_e2e.sh`

로컬에서 시도하려면(권장: Docker Desktop이 설치된 경우):

```powershell
# 스택 시작
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d --build

# 컨테이너 빌드 및 실행 (리포지토리 루트에서 실행)
docker build -t cc-playwright-runner -f ci/playwright/Dockerfile .
docker run --rm --network host -v ${PWD}:/workspace -w /workspace cc-playwright-runner bash ci/playwright/run_e2e.sh

# 종료
docker compose -f docker-compose.yml -f docker-compose.override.yml down -v --remove-orphans
```

CI는 워크플로에서 동일한 빌드/실행 과정을 수행합니다. 백엔드가 8000에서 /docs를 노출해야 합니다.


### 3. 실시간 추천 엔진
```python
@app.post("/api/recommend/personalized")
async def get_personalized_recommendations(user_id: int):
    user_segment = await get_user_segment(user_id)
    recommendations = await generate_recommendations(
        segment=user_segment,
        context="slot_machine_loss",
        risk_profile=user.risk_profile
    )
    return recommendations
```

## 📊 모니터링 & 분석

### 핵심 메트릭
- **일간/월간 토큰 획득량**
- **Whale 사용자 비율**
- **이탈률 (Churn Rate)**
- **피크 플레이 시간**
- **RFM 그룹별 사용자 분포**

### 대시보드 (개발 중)
- Grafana 또는 Metabase 통합 예정
- 실시간 사용자 행동 추적
- A/B 테스트 결과 시각화

## 🤝 기여 가이드

### 개발 환경 설정
1. 이 저장소를 포크
2. 기능 브랜치 생성: `git checkout -b feature/amazing-feature`
3. 변경사항 커밋: `git commit -m 'Add amazing feature'`
4. 브랜치에 푸시: `git push origin feature/amazing-feature`
5. Pull Request 생성

### 코딩 표준
- **백엔드**: Clean Architecture, SOLID 원칙, TDD
- **프론트엔드**: React 모범 사례, TypeScript 엄격 모드
- **스타일**: ESLint + Prettier 설정 준수
- **테스트**: 최소 80% 커버리지 유지

### 커밋 메시지 규칙
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 변경
style: 코드 포매팅
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 빌드 작업, 패키지 관리
```

## 📜 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🆘 지원

### 문제 해결
- [이슈 트래커](https://github.com/mamam1281/auto7777/issues)
- [토론 게시판](https://github.com/mamam1281/auto7777/discussions)

### 유용한 명령어
```powershell
# 환경 체크
.\docker-manage.ps1 check

# 전체 시스템 상태
.\docker-manage.ps1 status

# 성능 모니터링
.\docker-manage.ps1 monitor

# 도움말
.\docker-manage.ps1 help
```

---

**Casino-Club F2P**로 차세대 F2P 게임 플랫폼을 경험해보세요! 🎰✨

[![Star this repo](https://img.shields.io/github/stars/mamam1281/auto7777?style=social)](https://github.com/mamam1281/auto7777)
