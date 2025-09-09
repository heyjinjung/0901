# 🗄️ 데이터베이스 초기화 스크립트 사용법

## 📋 개요

`init_database.py`는 Casino-Club F2P 프로젝트의 메인 데이터베이스 초기화 스크립트입니다.
Repository 패턴과 완전 호환되며, 환경변수 기반 설정을 지원합니다.

## 🚀 빠른 시작

### 기본 사용법
```bash
# 기본 초기화 (개발 환경)
cd database/scripts
python init_database.py
```

### Docker 환경에서 사용
```bash
# PostgreSQL 컨테이너 실행 확인
docker-compose up -d postgres

# 데이터베이스 초기화 실행
python database/scripts/init_database.py
```

## ⚙️ 환경변수 설정

스크립트는 다음 환경변수들을 지원합니다:

### 필수 환경변수
```bash
# 데이터베이스 연결 (Docker compose에서 자동 설정)
DATABASE_URL=postgresql://cc_user:cc_password@localhost:5432/cc_webapp
```

### 선택적 환경변수
```bash
# 초기화 모드 (development/production/testing)
export DB_INIT_MODE=development

# 테스트 데이터 생성 여부 (true/false)  
export CREATE_TEST_DATA=true

# 관리자 비밀번호 (기본값: admin123)
export ADMIN_PASSWORD=your_admin_password

# 테스트 사용자 비밀번호 (기본값: test123)
export TEST_PASSWORD=your_test_password

# 기본 초대코드 (기본값: 5858)
export DEFAULT_INVITE_CODE=your_invite_code
```

## 📊 생성되는 데이터

### 항상 생성되는 데이터
1. **관리자 계정**
   - 사이트ID: `admin`
   - 닉네임: `관리자`
   - 폰번호: `01000000000`
   - 비밀번호: `ADMIN_PASSWORD` 환경변수 값 (기본: admin123)
   - 권한: 관리자

2. **초대코드**
   - 코드: `DEFAULT_INVITE_CODE` 환경변수 값 (기본: 5858)
   - 사용 횟수: 무제한 (999999)
   - 상태: 활성

### 조건부 생성되는 데이터 (CREATE_TEST_DATA=true)
3. **테스트 계정**
   - 사이트ID: `testuser`
   - 닉네임: `테스터`
   - 폰번호: `01012345678`
   - 비밀번호: `TEST_PASSWORD` 환경변수 값 (기본: test123)
   - 권한: 일반 사용자

## 🎯 사용 시나리오

### 1. 개발 환경 초기화
```bash
# .env 파일 또는 환경변수 설정
export DB_INIT_MODE=development
export CREATE_TEST_DATA=true
export ADMIN_PASSWORD=dev123
export TEST_PASSWORD=test123

# 초기화 실행
python database/scripts/init_database.py
```

### 2. 프로덕션 환경 초기화
```bash
# 보안 강화된 설정
export DB_INIT_MODE=production
export CREATE_TEST_DATA=false
export ADMIN_PASSWORD=complex_secure_password
export DEFAULT_INVITE_CODE=secure_invite_code

# 초기화 실행 (테스트 계정 없이)
python database/scripts/init_database.py
```

### 3. 테스트 환경 초기화
```bash
# 테스트 전용 설정
export DB_INIT_MODE=testing
export CREATE_TEST_DATA=true
export ADMIN_PASSWORD=testadmin123
export TEST_PASSWORD=testuser123

# 초기화 실행
python database/scripts/init_database.py
```

## 🛡️ 보안 고려사항

### 프로덕션 환경
- `ADMIN_PASSWORD`를 반드시 강력한 비밀번호로 변경
- `DEFAULT_INVITE_CODE`를 예측하기 어려운 값으로 설정
- `CREATE_TEST_DATA=false`로 설정하여 테스트 계정 생성 방지

### 개발 환경
- `.env` 파일을 `.gitignore`에 추가
- 개발팀 내에서만 공유되는 안전한 기본값 사용

## 🔍 실행 로그

스크립트 실행 시 다음과 같은 로그가 출력됩니다:

```
🔄 Casino-Club F2P 데이터베이스 초기화 시작...
📊 초기화 모드: development
🧪 테스트 데이터 생성: True
🗑️ 기존 테이블 삭제 중...
🏗️ 새 테이블 생성 중...
✅ 데이터베이스 테이블 생성 완료
✅ 관리자 계정 생성 완료: admin / admin123
✅ 초대코드 생성 완료: 5858 (무제한)
✅ 테스트 계정 생성 완료: testuser / test123
   - 닉네임: 테스터
   - 폰번호: 01012345678
✅ 초기화 검증 완료 - 모든 필수 데이터가 정상적으로 생성되었습니다
🎉 데이터베이스 초기화 완료!
🔑 관리자 로그인: admin / admin123
🧪 테스트 로그인: testuser / test123
📧 초대코드: 5858
```

## ❌ 오류 해결

### 자주 발생하는 오류

#### 1. Import Error
```
ImportError: app.models.auth_models could not be resolved
```
**해결책**: 백엔드 디렉토리에서 실행하거나 PYTHONPATH 설정
```bash
cd cc-webapp/backend
python ../../database/scripts/init_database.py
```

#### 2. Database Connection Error
```
❌ 데이터베이스 연결 실패: connection refused
```
**해결책**: PostgreSQL 컨테이너 상태 확인
```bash
docker-compose ps postgres
docker-compose up -d postgres
```

#### 3. Permission Error
```
❌ 관리자 계정 생성 실패: permission denied
```
**해결책**: 데이터베이스 권한 확인
```bash
# PostgreSQL 컨테이너에서 권한 확인
docker exec -it cc_postgres psql -U cc_user -d cc_webapp -c "\\du"
```

## 🔄 Repository 패턴 호환성

이 스크립트는 다음 Repository들과 호환됩니다:

- `UserRepository`: 사용자 데이터 관리
- `AuthRepository`: 인증 관련 데이터 관리
- `BaseRepository`: 기본 CRUD 작업

### Repository 사용 예시
```python
from app.repositories import UserRepository

# 초기화 후 Repository 사용
db = SessionLocal()
user_repo = UserRepository(db)

# 생성된 관리자 확인
admin = await user_repo.get_by_site_id("admin")
print(f"관리자: {admin.nickname}")
```

## 🚀 다음 단계

초기화 완료 후:

1. **API 서버 시작**
   ```bash
   cd cc-webapp/backend
   uvicorn app.main:app --reload
   ```

2. **프론트엔드 시작**
   ```bash
   cd cc-webapp/frontend  
   npm run dev
   ```

3. **로그인 테스트**
   - http://localhost:3000 접속
   - admin / admin123 또는 testuser / test123으로 로그인

---
*Repository 패턴 및 환경변수 기반 설정 지원*
*Last updated: 2024-01-29*
