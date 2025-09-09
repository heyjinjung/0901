# 카지노 클럽 F2P 간단 시작 가이드

이 안내서는 카지노 클럽 F2P 프로젝트를 최소한의 설정으로 빠르게 시작하는 방법을 설명합니다.

## 1. 시작하기

프로젝트를 시작하기 위해 간단한 명령어를 사용할 수 있습니다:

```powershell
# 환경 시작
.\cc-manage.ps1 start

# 상태 확인
.\cc-manage.ps1 status
```

## 2. 사용 가능한 서비스

이 설정에는 다음과 같은 서비스가 포함되어 있습니다:

- **웹 프론트엔드 (Next.js)**: http://localhost:3000
- **API 백엔드 (FastAPI)**: http://localhost:8000
- **데이터베이스 (PostgreSQL)**: localhost:5432
  - 사용자: cc_user
  - 비밀번호: cc_password
  - 데이터베이스: cc_webapp

## 3. 유용한 명령어

```powershell
# 환경 시작
.\cc-manage.ps1 start

# 환경 중지
.\cc-manage.ps1 stop

# 로그 확인
.\cc-manage.ps1 logs        # 모든 로그
.\cc-manage.ps1 logs api    # API 로그만
.\cc-manage.ps1 logs web    # 웹 로그만
.\cc-manage.ps1 logs db     # DB 로그만

# 컨테이너 상태 확인
.\cc-manage.ps1 status

# 컨테이너 쉘 접속
.\cc-manage.ps1 shell api   # API 컨테이너 쉘
.\cc-manage.ps1 shell web   # 웹 컨테이너 쉘
.\cc-manage.ps1 shell db    # DB SQL 쉘

# 도움말 표시
.\cc-manage.ps1 help
```

## 4. 문제 해결

### 서비스가 시작되지 않는 경우

로그를 확인하여 문제를 진단할 수 있습니다:

```powershell
.\cc-manage.ps1 logs api
```

### 포트가 이미 사용 중인 경우

이미 사용 중인 포트를 확인하고 해당 프로세스를 종료합니다:

```powershell
# 포트 사용 확인
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# 프로세스 종료 (PID를 실제 PID로 대체)
taskkill /F /PID <PID>
```

## 5. 파일 구조

- `docker-compose.basic.yml`: Docker 컨테이너 구성
- `cc-manage.ps1`: 관리 스크립트
- `cc-webapp/`: 애플리케이션 코드
  - `backend/`: FastAPI 백엔드
  - `frontend/`: Next.js 프론트엔드
- `data/`: 데이터 저장소
  - `db/`: PostgreSQL 데이터

---

이 간단한 설정을 통해 개발 환경을 빠르게 시작하고 관리할 수 있습니다.

## 부록: E2E(Playwright) 컨테이너 실행

기본 실행:

```powershell
docker compose -f docker-compose.yml -f docker-compose.playwright.yml up --abort-on-container-exit --exit-code-from playwright playwright
```

깊은 시나리오(맵핑/디듀프/상점 동기화) 활성화:

```powershell
docker compose -f docker-compose.yml -f docker-compose.playwright.yml -f docker-compose.playwright.deep.yml up --abort-on-container-exit --exit-code-from playwright playwright
```

엄격 모드(엔드포인트 안정화 후 CI와 동일하게 실패 전환) 예시:

```powershell
$env:E2E_REQUIRE_STATS_PARITY = "1"; $env:E2E_REQUIRE_SHOP_SYNC = "1"; $env:E2E_REQUIRE_REALTIME = "1";
docker compose -f docker-compose.yml -f docker-compose.playwright.yml up --abort-on-container-exit --exit-code-from playwright playwright
```
