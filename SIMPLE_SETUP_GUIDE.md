# 카지노 클럽 F2P 간소화 버전 가이드

이 가이드는 카지노 클럽 F2P 프로젝트의 간소화된 버전을 실행하기 위한 안내입니다. 복잡한 모델과 종속성을 제거하고 기본적인 기능만 포함하여 쉽게 시작할 수 있도록 구성했습니다.

## 1. 폴더 구조

```
cc-webapp/
├── backend/               # FastAPI 백엔드
│   ├── app/
│   │   ├── main_simple.py        # 간소화된 메인 앱
│   │   ├── dependencies_simple.py # 간소화된 의존성
│   │   ├── routers/
│   │   │   └── auth_simple.py    # 간소화된 인증 라우터
│   │   └── models/
│   │       └── simple_auth_models.py # 간소화된 모델
│   └── init_simple_db.py  # 초기 데이터베이스 설정
└── frontend/              # Next.js 프론트엔드
```

## 2. 시작하기

### Docker 환경 시작

```powershell
# 기본 서비스만 시작
.\docker-manage-simple.ps1 start

# 개발 도구(pgAdmin)까지 포함하여 시작
.\docker-manage-simple.ps1 start --tools
```

### 데이터베이스 초기화

```powershell
# 데이터베이스 테이블 생성 및 초기 데이터 입력
.\docker-manage-simple.ps1 init-db
```

## 3. 기본 사용자 계정

데이터베이스 초기화 시 다음 계정이 자동으로 생성됩니다:

1. **관리자 계정**
   - ID: admin
   - 비밀번호: admin123

2. **테스트 계정**
   - ID: test
   - 비밀번호: test123

3. **초대 코드**
   - 코드: 5858

## 4. API 엔드포인트

### 인증 관련

- `POST /api/auth/login`: 로그인
- `POST /api/auth/signup`: 회원가입
- `GET /api/auth/me`: 현재 로그인한 사용자 정보 조회

## 5. 유용한 명령어

```powershell
# 서비스 상태 확인
.\docker-manage-simple.ps1 status

# 로그 확인
.\docker-manage-simple.ps1 logs
.\docker-manage-simple.ps1 logs backend
.\docker-manage-simple.ps1 logs frontend

# 컨테이너 셸 접속
.\docker-manage-simple.ps1 shell backend
.\docker-manage-simple.ps1 shell frontend

# 도움말 보기
.\docker-manage-simple.ps1 help
```

## 6. 서비스 접속

- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050
  - Email: admin@casino-club.local
  - Password: admin123

## 7. 문제해결

### 서비스가 시작되지 않는 경우
```powershell
# 서비스 상태 확인
.\docker-manage-simple.ps1 status

# 로그 확인
.\docker-manage-simple.ps1 logs backend
```

### 포트가 이미 사용 중인 경우
```powershell
# Windows에서 포트 사용 확인
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# PID를 확인한 후 해당 프로세스 종료
taskkill /F /PID <PID>
```
