# API 매핑 및 인증 시스템 문제 해결 가이드

## 문제 진단

현재 Casino-Club F2P 백엔드에서는 다음과 같은 문제가 발생하고 있습니다:

1. `/api/auth/signup` 엔드포인트가 404 Not Found 오류를 반환함
2. 실제로는 `/auth/register` 엔드포인트가 존재하지만 이 또한 500 Internal Server Error 반환함
3. API 구조가 일관성 없이 분리되어 있음

## 원인 분석

### 1. 모듈 구조 문제

- `app/routers/auth.py` 파일과 `app/routers/auth/` 디렉토리가 동시에 존재
- Python의 모듈 시스템에서 디렉토리가 우선순위를 가지므로, `import auth`는 항상 디렉토리를 가리킴
- `app/routers/auth/__init__.py`에서 `from ..auth import router`를 시도하여 순환 임포트 발생

### 2. 엔드포인트 불일치

- 클라이언트는 `/api/auth/signup`을 호출하지만 실제 API는 `/auth/register` 제공
- 두 라우터 간에 prefix와 경로 이름이 일치하지 않음

### 3. 데이터베이스 모델 관계 문제

- User 모델과 SecurityEvent 모델 간의 관계 정의에 문제 존재
- Foreign Key 정의가 없거나 잘못 설정됨

## 해결 방안

### 방안 1: 통합된 auth.py 사용 (권장)

1. `app/routers/auth/` 디렉토리를 삭제
2. `app/routers/auth.py`만 사용하도록 수정
3. 라우터의 prefix를 `/api/auth`로 통일
4. 데이터베이스 모델의 관계 수정

### 방안 2: auth_endpoints.py 구조 수정

1. `app/auth/auth_endpoints.py` 파일의 라우터 prefix를 `/api/auth`로 변경
2. `app/routers/auth.py` 파일 삭제
3. `app/routers/auth/__init__.py`에서 올바른 경로로 임포트

### 방안 3: 클라이언트 코드 수정

1. 클라이언트에서 `/api/auth/signup` 대신 `/auth/register` 호출하도록 변경
2. 데이터베이스 모델의 관계 수정

## 인증 시스템 검증 체크리스트

### 1. 회원가입
- [x] 초대 코드 확인 기능 검증
  - 유효한 초대 코드: `5858` (무한 재사용 가능)
  - 잘못된 초대 코드 입력 시 오류 메시지 표시 
- [x] 회원가입 폼 작동 확인
  - 필수 필드: 아이디, 비밀번호(4글자 이상), 닉네임, 전화번호, 초대 코드
- [x] 유효한 초대 코드로 회원가입 성공
  - 초대 코드 `5858` 사용 ✅ 무한 재사용 가능
- [x] 중복 아이디 검사 기능
  - 이미 등록된 아이디/닉네임/전화번호로 가입 시도 시 적절한 오류 메시지
- [x] 비밀번호 강도 검사
  - 요구사항: 4자리 이상

### 2. 로그인
- [x] 아이디/비밀번호 로그인 기본 구조 
- [x] 잘못된 자격증명 시 적절한 오류 메시지
- [x] JWT 토큰 생성 로직
- [x] 일반 사용자 로그인 완전 테스트
- [x] 관리자 로그인 완전 테스트
- [ ] 로그인 후 메인 화면으로 리디렉션 (프론트엔드 구현 필요)

### 3. 토큰 관리
- [x] 토큰 생성 및 검증 로직
- [x] 토큰 파싱 및 사용자 인증
- [x] 관리자 권한 토큰 검증
- [x] 토큰 만료 시 자동 갱신 기능
- [x] 갱신 토큰 만료 처리
- [x] 로그아웃 시 토큰 제거 

## 관련 파일 구조

```
app/
├── routers/
│   ├── auth.py                 # 현재 main.py에서 참조하는 파일
│   ├── auth/                   # 디렉토리도 동시에 존재하여 충돌 발생
│   │   └── __init__.py         # 문제가 되는 임포트 구문 존재
├── auth/
│   └── auth_endpoints.py       # 실제 등록된 라우터 (prefix="/auth")
```

## 실제 사용 가능한 인증 엔드포인트

현재 상황에서 수정된 인증 관련 엔드포인트는 다음과 같습니다:

| 엔드포인트 | 메소드 | 설명 | 요청 본문 | 응답 |
|------------|--------|------|-----------|------|
| `/api/auth/verify-invite` | POST | 초대 코드 유효성 검증 | `{"inviteCode": "string"}` | `{"valid": true/false, "message": "string"}` |
| `/api/auth/signup` | POST | 새로운 사용자 등록 | `{"username": "string", "password": "string", "nickname": "string", "inviteCode": "string"}` | JWT 토큰 + 사용자 정보 |
| `/api/auth/login` | POST | 일반 사용자 로그인 | `{"username": "string", "password": "string"}` | JWT 토큰 + 사용자 정보 |
| `/api/auth/admin/login` | POST | 관리자 로그인 | `{"site_id": "string", "password": "string"}` | JWT 토큰 + 사용자 정보 |
| `/api/auth/refresh` | POST | 토큰 갱신 | `{"refreshToken": "string"}` | 새로운 액세스 토큰 |
| `/api/auth/logout` | POST | 로그아웃 | _Bearer 토큰 필요_ | `{"message": "string"}` |

### API 응답 형식

#### 성공 응답 (200 OK)
```json
{
    "access_token": "string",
    "token_type": "bearer",
    "user": {
        "id": "number",
        "site_id": "string",
        "nickname": "string",
        "phone_number": "string",
        "cyber_token_balance": "number",
        "created_at": "datetime",
        "last_login": "datetime",
        "is_admin": "boolean",
        "is_active": "boolean"
    }
}
```

#### 오류 응답 
```json
{
    "detail": "string"  // 오류 메시지
}
```

### HTTP 상태 코드
- 200: 성공
- 400: 잘못된 요청 (유효하지 않은 초대 코드, 중복된 사용자 등)
- 401: 인증 실패 (잘못된 자격증명)
- 403: 권한 없음
- 404: 리소스를 찾을 수 없음
- 500: 서버 내부 오류

### 특이사항
1. 초대 코드 `5858`은 개발 환경에서 무한 재사용 가능
2. 비밀번호는 최소 4자리 이상 필요
3. 토큰 만료 시간
   - 액세스 토큰: 1시간
   - 리프레시 토큰: 7일
| `/auth/logout` | POST | 로그아웃 | 미확인 |
| `/auth/profile` | GET | 사용자 프로필 조회 | 미확인 |
| `/auth/sessions` | GET | 활성 세션 목록 조회 | 미확인 |

def authenticate_user(self, username: str, password: str) -> User
def authenticate_admin(self, username: str, password: str) -> User
def verify_token(self, token: str) -> dict
def create_refresh_token(self, data: dict) -> str
def verify_refresh_token(self, token: str) -> dict
def blacklist_token(self, token: str) -> None
def is_token_blacklisted(self, token: str) -> bool

class TokenBlacklist:
    token: str
    expires_at: datetime
    blacklisted_at: datetime
    blacklisted_by: int  # user_id




## 권장 최종 해결책

1. `app/routers/auth/` 디렉토리 삭제
2. `app/routers/auth.py` 파일에 라우터 정의 통합
3. `app/auth/auth_endpoints.py` 파일의 기능을 `app/routers/auth.py`로 병합
4. 데이터베이스 모델의 관계 수정 (User와 SecurityEvent 모델)
5. 클라이언트 코드에서는 `/api/auth/signup` 엔드포인트 사용

## 진행 상황

- [x] 문제 진단 완료
- [x] 원인 분석 완료
- [ ] 모듈 구조 수정
- [ ] 데이터베이스 모델 수정
- [ ] API 엔드포인트 통일
- [ ] 인증 시스템 완전 테스트
