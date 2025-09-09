# 🚀 Casino-Club F2P: 프론트/데이터/백엔드 연동 작업 가이드

## 1. 프로젝트 아키텍처 개요

### 1.1 기술 스택

#### 백엔드
- **프레임워크**: FastAPI (Python 3.11)
- **데이터베이스**: PostgreSQL
- **캐싱**: Redis
- **메시지 큐**: Kafka
- **백그라운드 태스크**: Celery + APScheduler

#### 프론트엔드
- **프레임워크**: Next.js 15.4.5
- **UI 라이브러리**: React 19.1.0
- **스타일링**: Tailwind CSS 4.0.0
- **애니메이션**: Framer Motion
- **타입 시스템**: TypeScript

### 1.2 배포 환경
- **컨테이너화**: Docker Compose 기반 개발/배포 환경
- **서비스 구성**: 
  - 백엔드 API 서버
  - 웹 프론트엔드 서버
  - PostgreSQL 데이터베이스
  - Redis 캐시 서버
  - Kafka + Zookeeper
  - Celery Worker + Beat

## 2. 최근 완료된 작업

### 2.1 완료된 백엔드 작업
- ✅ **백엔드 API 중복 태그 제거 및 구조 정리** (2025-08-04)
  - API 라우터 구조 재정리 및 명확한 카테고리화
  - 중복 prefix(`/api/api/...`) 문제 해결
  - Swagger 문서 개선 및 태그 정리
- ✅ **Repository 패턴 100% 구현 완료** (2025-08-03)
  - 7개의 전문화된 Repository 클래스 구현
  - 통합 Factory 시스템 구현으로 의존성 주입 개선
  - 타입 안전성 및 확장 가능한 아키텍처 구조 완성
- ✅ **데이터베이스 초기화 스크립트 정리 완료** (2024-01-29)
  - 여러 스크립트에서 단일 초기화 스크립트로 통합
  - 환경변수 기반 설정 지원 추가

### 2.2 완료된 프론트엔드 작업
- ✅ **API 연동 테스트 구현** - 16개 테스트 케이스 전체 통과 (2025-08-04)
- ✅ **NeonSlotGame 컴포넌트 타입 오류 수정** (2025-08-06)
- ✅ **라우팅 구조 정리** - App Router 기반으로 통일

## 3. 현재 문제점 및 해결과제

### 3.1 API 연동 관련 이슈
- 🔴 **프론트엔드와 백엔드 연동 작업이 불완전함**
  - API 클라이언트 구현은 되어 있으나 실제 컴포넌트 연동 미흡
  - 일부 엔드포인트에서 오류 처리 로직 부재
  
- 🔴 **API 응답 데이터 형식 불일치**
  - 백엔드 응답 스키마와 프론트엔드 기대 타입 간 불일치
  - 일부 API에서 중복된 태그 문제 발생 (정리 필요)
  
- 🔴 **프론트엔드 빌드 오류**
  - App Router와 Pages Router 간 충돌 (pages/index.tsx와 app/page.tsx)
  - Next.js 빌드 실패로 Docker 컨테이너 시작 문제 발생

## 4. 우선순위별 작업 계획

### 4.1 최우선 과제: 프론트엔드/백엔드/데이터 연동 작업 ⭐⭐⭐

#### 목표
- 디자인 완성도를 보존하면서 백엔드 API와의 완벽한 통합
- 모든 컴포넌트에서 실제 API 데이터 사용 구현

#### 세부 작업
1. **API 클라이언트 통합**
   - 엔드포인트 그룹별 점진적 통합 접근: `auth → user → game` 순서로 진행
   - API 타입 생성 및 검증 로직 추가
   - 타입스크립트 타입 정의와 백엔드 스키마 동기화

2. **컴포넌트별 API 연동**
   - 디자인 변경 없이 데이터 흐름만 실제 API로 연결
   - 기존 UI/UX 요소 및 애니메이션 보존
   - 로딩/에러 상태 관리 추가

3. **상태 관리 통합**
   - API 상태와 UI 상태 분리하여 관리 (어댑터 패턴 활용)
   - 캐싱 전략 구현 (필요시 SWR/React Query 도입 검토)
   - 전역 상태와 로컬 상태 구분 관리

4. **API 중복 문제 해결**
   - 중복 태그 및 prefix 문제 최종 검증
   - API 클라이언트 내 경로 정리 및 표준화

5. **Docker 개발 환경 설정 문제 해결**
   - 프론트엔드 빌드 오류 해결 (라우팅 충돌 해결)
   - 개발/테스트/프로덕션 환경 설정 분리 개선

**참고 문서**: `PHASE1_API_INTEGRATION_TEST_REPORT.md`, `API_DUPLICATE_REMOVAL_REPORT.md`


### 4.2 상점 UI/기능 완성 ⭐⭐

#### 현재 상태
- UI 컴포넌트: ✅ 완성
- API 연동/상태관리: ⚠️ 일부 구현
- 백엔드 기능: ❌ 미구현

#### 세부 작업
1. **백엔드 기능 구현**
   - 상품 목록 API (`/api/shop/items`) 구현
   - 구매 처리 API (`/api/shop/buy`) 구현
   - 결제 검증 및 아이템 지급 로직 개발
   - 할인/프로모션 기능 구현

2. **결제/아이템 구매 플로우 구현**
   - 구매 확인 및 처리 프로세스 완성
   - 결제 오류 처리 및 재시도 로직 추가
   - 구매 완료 후 인벤토리/사용자 상태 업데이트

3. **API 연동 및 상태 관리 완성**
   - 상점 컴포넌트와 백엔드 API 완전 연동
   - 상점 상태(장바구니, 결제 진행 등) 관리 로직 구현
   - 구매 히스토리 및 관련 통계 추적

**참고 문서**: `20250728-가이드001.md`

### 4.3 관리자 대시보드 기능 완성 ⭐⭐

#### 현재 상태
- UI 컴포넌트: ⚠️ 구현 중
- API 연동/상태관리: ❌ 미구현
- 백엔드 기능: ❌ 미구현

#### 세부 작업
1. **관리자 백엔드 API 구현**
   - 사용자 관리 API (`/api/admin/users`) 구현
   - 통계 및 대시보드 데이터 API (`/api/admin/dashboard`) 구현
   - 관리자 권한 검증 및 인증 로직 강화
   - 로그 및 감사 기능 추가

2. **관리자 대시보드 UI 완성**
   - 사용자 관리 패널 구현
   - 통계 및 분석 차트 구현 (매출, 사용자 활동, 게임 통계 등)
   - 시스템 상태 모니터링 UI
   - 설정 및 구성 관리 인터페이스

3. **API 연동 및 데이터 표시**
   - 실시간 데이터 업데이트 구현
   - 데이터 필터링 및 검색 기능
   - 페이지네이션 및 대용량 데이터 처리

4. **보안 및 권한 관리**
   - 세분화된 관리자 권한 구현
   - 작업 기록 및 변경 내역 추적
   - 민감 작업 승인 프로세스 구현

**참고 문서**: `20250728-가이드001.md`




### 4.4 실시간 기능(WebSocket, 알림 등) 구현 ⭐⭐

#### 현재 상태
- 프론트엔드: ⚠️ Stub 구현
- 백엔드: ❌ 미구현

#### 세부 작업
1. **WebSocket 인프라 구축**
   - FastAPI 기반 WebSocket 서버 구현
   - 연결 관리 및 인증 처리 로직 구현
   - 클라이언트-서버 통신 프로토콜 설계
   - 연결 복구 및 오류 처리 메커니즘 구현

2. **실시간 알림 시스템 구현**
   - 푸시 알림 서비스 통합 (게임 결과, 보상, 이벤트 등)
   - 알림 우선순위 및 분류 체계 구현
   - 사용자 기반 알림 필터링 및 설정 관리

3. **실시간 게임 결과/랭킹 표시**
   - 실시간 랭킹 및 리더보드 업데이트
   - 게임 결과 실시간 브로드캐스팅
   - 멀티플레이어 동기화 기능 구현

**참고 문서**: `20250728-가이드001.md`

### 4.5 프론트엔드 구조 및 빌드 문제 해결 ⭐⭐

#### 현재 문제점
- App Router와 Pages Router 충돌 (pages/index.tsx - app/page.tsx)
- 빌드 시 오류 발생으로 Docker 환경에서 프론트엔드 실행 불가
- 일부 UI 효과 미적용 (글래스 모피즘, 네온 효과)

#### 세부 작업
1. **라우팅 구조 정리**
   - Pages Router 완전 제거 및 App Router로 통일
   - 중복 페이지 (pages/index.tsx, app/page.tsx) 해결
   - 라우팅 방식 일관성 확보

2. **설정 파일 검토 및 수정**
   - next.config.js 최적화 및 구성 검토
   - 타입스크립트 설정 개선
   - 빌드 프로세스 최적화

3. **디자인 시스템 적용 문제 해결**
   - Tailwind CSS 구성 개선 (특히 커스텀 효과)
   - 글래스 모피즘 효과 적용 문제 해결
   - 네온 효과 및 애니메이션 최적화

**참고 문서**: `FRONTEND_ANALYSIS_REPORT.md`

### 4.6 배틀패스/추천 시스템 연동 (낮은 우선순위) ⭐

> **참고**: 현재 개발 계획 없음, 향후 확장 시 참고

#### 현재 상태
- API/컴포넌트: ⚠️ 일부 구현
- 연동: ❌ 미완성

#### 향후 구현 방향 (참고용)
1. **배틀패스 시스템 완성**
   - 시즌별 보상 체계 구현
   - 진행도 추적 및 보상 지급 자동화
   - 유료/무료 트랙 분리 구현

2. **개인화된 추천 시스템 연동**
   - 사용자 행동 기반 추천 알고리즘 구현
   - 세그먼트 기반 타겟팅 및 개인화
   - A/B 테스트 프레임워크 구축

**참고 문서**: `20250728-가이드001.md`


### 4.7 테스트/문서화/체크리스트 동기화 ⭐

#### 현재 상태
- 테스트: ⚠️ 일부 구현 (API 테스트만 완료)
- 문서화: ⚠️ 불완전 (일부 문서 업데이트 필요)
- 체크리스트: ⚠️ 동기화 필요

#### 세부 작업
1. **API 명세와 실제 구현 동기화**
   - OpenAPI 스키마와 실제 구현 일치 여부 검증
   - API 중복 및 일관성 문제 해결
   - API 테스트 커버리지 확대

2. **테스트 강화**
   - 백엔드: 단위 테스트 및 통합 테스트 확장
   - 프론트엔드: 컴포넌트 테스트 및 E2E 테스트 구현
   - CI/CD 파이프라인 내 자동화된 테스트 설정

3. **문서화 개선**
   - 개발자 문서 최신화
   - API 문서 자동 생성 및 유지보수
   - 아키텍처 및 시스템 설계 문서 업데이트

## 5. 환경 설정 및 개발 워크플로우

### 5.1 개발 환경 설정

#### 백엔드 환경 (Docker Compose 기반)
```powershell
# 개발환경 체크
.\docker-manage.ps1 check

# 초기 환경 설정
.\docker-manage.ps1 setup

# 서비스 시작 (개발 도구 포함)
.\docker-manage.ps1 start --tools
```

#### 프론트엔드 환경 (로컬 개발 기반)
```powershell
# 프로젝트 디렉토리로 이동
cd cc-webapp/frontend

# 의존성 설치
npm install

# 개발 서버 시작
npm run dev
```

### 5.2 일일 개발 루틴

#### 1. 아침 개발 시작
```powershell
# 코드 최신화
git pull origin main

# 백엔드 서비스 시작
.\docker-manage.ps1 start --tools

# 프론트엔드 개발 서버 시작
cd cc-webapp/frontend
npm run dev
```

#### 2. 백엔드 개발 작업
```powershell
# 백엔드 컨테이너 진입
.\docker-manage.ps1 shell backend

# 로그 확인
.\docker-manage.ps1 logs backend

# 테스트 실행
.\docker-manage.ps1 test coverage
```

#### 3. 프론트엔드 개발 작업
```powershell
# 프론트엔드 컨테이너 진입 (필요시)
.\docker-manage.ps1 shell frontend

# 로컬에서 직접 작업 (권장)
cd cc-webapp/frontend
code .
```

#### 4. API 연동 워크플로우
1. API 클라이언트 구현 및 연동 
2. 컴포넌트 연동 
3. 디자인 검증
4. 사이클 반복

#### 5. 일일 마무리
```powershell
# 변경사항 커밋
git add .
git commit -m "feat: 기능 구현 내용 설명"

# 필요시 푸시
git push origin main

# 서비스 중지 (필요시)
.\docker-manage.ps1 stop
```



### 5.3 데이터베이스 스키마 확인 및 준비

#### 스키마 내보내기
```powershell
# PostgreSQL 스키마 내보내기
.\docker-manage.ps1 shell postgres
pg_dump -U cc_user -d cc_webapp --schema-only > /tmp/schema.sql

# 스키마 파일 복사
exit
.\docker-manage.ps1 cp postgres:/tmp/schema.sql ./database/schema.sql
```

#### 테스트 데이터 준비
```powershell
# 테스트 데이터 생성 스크립트 실행
.\docker-manage.ps1 shell backend
python scripts/generate_test_data.py

# 데이터 내보내기 (필요시)
python scripts/export_test_data.py
```

## 6. 점진적 연동 구현 전략

### 6.1 API 클라이언트 통합 전략

#### API 엔드포인트 그룹별 우선순위
1. **인증 관련 엔드포인트**
   - `/api/auth/signup`, `/api/auth/login`, `/api/auth/refresh`
   - 사용자 인증 플로우 완성이 최우선

2. **사용자 관련 엔드포인트**
   - `/api/users/profile`, `/api/users/stats`, `/api/users/balance`
   - 사용자 기본 정보 및 통계 연동

3. **게임 관련 엔드포인트**
   - `/api/games/*`, `/api/actions`, `/api/rewards`
   - 핵심 게임 기능 및 보상 시스템 연동

#### 각 엔드포인트 통합 방식
- 타입스크립트 인터페이스 자동 생성 (스키마 기반)
- 요청/응답 유효성 검증 로직 추가
- 에러 처리 및 재시도 전략 구현

### 6.2 컴포넌트별 API 연동 전략

#### 핵심 원칙
- **디자인 보존**: UI/UX 요소 및 애니메이션 완벽 유지
- **점진적 전환**: 컴포넌트별로 Stub 데이터에서 실제 API로 전환
- **코드 분리**: 데이터 로직과 UI 로직 명확히 분리

#### 구현 접근법
- 컴포넌트 속성 유지하면서 데이터 소스만 실제 API로 교체
- 기존 디자인 토큰 및 스타일 시스템 활용
- 점진적 마이그레이션 통한 위험 최소화

### 6.3 상태 관리 통합 전략

#### 어댑터 패턴 활용
- API 응답을 내부 상태 모델로 변환
- UI 컴포넌트는 변환된 내부 모델만 사용
- 백엔드 API 변경에 대비한 격리 계층 구현

#### 상태 관리 접근법
- API 호출 상태(로딩, 성공, 실패) 분리 관리
- 캐싱 및 재검증 전략 적용
- 옵티미스틱 UI 업데이트 적용 (사용자 경험 향상)

## 7. 단계별 구현 계획

### 7.1 세부 구현 단계

#### 1단계: 인증 시스템 연동 (1일)
- 로그인/가입 기능 연동
- 토큰 관리 및 자동 갱신 구현
- 인증 상태 관리 및 보안 강화

#### 2단계: 데이터 모델 및 API 연결 (2-3일)
- 핵심 데이터 모델 통합
- API 클라이언트 라이브러리 구현
- 에러 처리 및 재시도 로직 구현

#### 3단계: UI 컴포넌트 연동 (3-5일)
- 컴포넌트별 API 통합
- 로딩/에러 상태 UI 구현
- 데이터 검증 및 포맷팅

#### 4단계: 상태 관리 및 테스트 (2-3일)
- 전역 상태 관리 최적화
- 테스트 커버리지 확대
- 성능 최적화 및 디버깅

## 8. API 구조 표준화 및 개발 가이드

### 8.1 API 경로 구조 표준화

#### 표준 경로 구조
모든 API 경로는 다음과 같은 구조로 표준화되었습니다:

```
/api/{리소스_그룹}/{리소스_식별자}/{작업}
```

예시:
- `/api/users/profile` - 사용자 프로필 조회
- `/api/games/slot/spin` - 슬롯 게임 스핀 액션
- `/api/admin/users/{id}` - 관리자용 특정 사용자 관리

#### 주요 리소스 그룹 및 경로
| 리소스 그룹 | 기본 경로 | 주요 기능 | 태그 |
|------------|---------|----------|------|
| **인증** | `/api/auth` | 로그인, 회원가입, 토큰 갱신 | Auth |
| **사용자** | `/api/users` | 프로필, 통계, 잔액 관리 | Users |
| **게임** | `/api/games` | 게임별 액션 (슬롯, 가챠 등) | Games |
| **상점** | `/api/shop` | 상품 목록, 구매 처리 | Shop |
| **보상** | `/api/rewards` | 보상 확인 및 수령 | Rewards |
| **배틀패스** | `/api/battlepass` | 진행도, 보상 획득 | BattlePass |
| **이벤트/미션** | `/api/events` | 이벤트 목록, 미션 진행 | Events & Missions |
| **관리자** | `/api/admin` | 관리자용 기능 | Admin |
| **퀴즈** | `/api/quiz` | 사용자 퀴즈 및 설문 | Quiz |
| **채팅** | `/api/chat` | 채팅 및 메시지 | Chat |
| **초대** | `/api/invite` | 초대 코드 관리 | Invite Codes |
| **세그먼트** | `/api/segments` | 사용자 세그먼트 관리 | Segments |
| **대시보드** | `/api/dashboard` | 통계 및 분석 데이터 | Dashboard |

### 8.2 API 태그 표준화

모든 API 라우터는 일관된 태그 네이밍 규칙을 따릅니다:
- 첫 글자 대문자 (예: "Admin", "Users", "Games")
- 복합 태그의 경우 & 사용 (예: "Events & Missions")
- 태그는 라우터 정의에서만 지정하고 등록 시 재정의하지 않음

### 8.3 새로운 API 개발 가이드

#### 1. 백엔드 API 라우터 구현 패턴

```python
# 권장 패턴 (admin_router.py)
from fastapi import APIRouter, Depends

# 1. 태그는 라우터 정의 시 명확히 지정 (첫 글자 대문자)
router = APIRouter(prefix="/api/admin", tags=["Admin"])

# 2. 엔드포인트는 명확한 HTTP 메서드와 경로로 정의
@router.get("/users", response_model=List[UserResponse])
async def get_users(
    offset: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user)
):
    """사용자 목록 조회 (관리자용)."""
    # 3. 적절한 의존성 주입 사용
    # 4. Repository 패턴 적용
    users_repo = UserRepository()
    return await users_repo.get_users(offset=offset, limit=limit)
```

#### 2. 메인 앱 라우터 등록 패턴

```python
# main.py
from fastapi import FastAPI
import admin_router, users_router, games_router

app = FastAPI(
    title="Casino-Club F2P API",
    description="사용자 참여와 수익화를 극대화하는 카지노 클럽 F2P API",
    version="1.0.0"
)

# 중요: 라우터 등록 시 태그 재정의하지 않음
app.include_router(admin_router.router)  # tags 파라미터 사용하지 않음
app.include_router(users_router.router)
app.include_router(games_router.router)
```

#### 3. 새 API 모듈 추가 단계

1. **라우터 모듈 생성**:
   - `cc-webapp/backend/app/routers/{리소스명}_router.py` 생성
   - 대문자로 시작하는 적절한 태그 설정

2. **스키마 정의**:
   - `cc-webapp/backend/app/schemas/{리소스명}.py` 생성
   - Pydantic 모델로 요청/응답 스키마 정의

3. **Repository 구현**:
   - `cc-webapp/backend/app/repositories/{리소스명}_repository.py` 생성
   - 필요한 데이터 액세스 메서드 구현

4. **Service 구현** (필요시):
   - `cc-webapp/backend/app/services/{리소스명}_service.py` 생성
   - 비즈니스 로직 구현

5. **메인 앱에 라우터 등록**:
   - `main.py`에 import 추가
   - `app.include_router()` 호출 (태그 재정의 없이)

6. **테스트 작성**:
   - `cc-webapp/backend/tests/test_{리소스명}.py` 생성
   - 엔드포인트별 테스트 케이스 구현

### 8.4 프론트엔드 API 클라이언트 패턴

#### API 클라이언트 구현

```typescript
// api-client.ts
// 1. 기본 URL 설정 (중요: '/api'를 포함하지 않음)
const API_BASE_URL = 'http://localhost:8000';

// 2. 리소스별 클라이언트 클래스 구현
export class UserApiClient {
  // 3. 표준 경로 구조 따르기
  async getProfile(): Promise<UserProfile> {
    const response = await fetch(`${API_BASE_URL}/api/users/profile`, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`
      }
    });
    
    if (!response.ok) {
      throw new ApiError('프로필 조회 실패', response.status);
    }
    
    return response.json();
  }
}

// 4. 타입 정의는 백엔드 스키마와 동기화
export interface UserProfile {
  id: string;
  nickname: string;
  vip_tier: string;
  battlepass_level: number;
  // ...추가 필드
}
```

#### 컴포넌트에서 API 사용

```tsx
// ProfileComponent.tsx
import { UserApiClient } from '../api/api-client';
import { useEffect, useState } from 'react';

export function ProfileComponent() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const userClient = new UserApiClient();
  
  useEffect(() => {
    async function loadProfile() {
      try {
        const data = await userClient.getProfile();
        setProfile(data);
        setError(null);
      } catch (err) {
        setError('프로필을 불러올 수 없습니다');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    
    loadProfile();
  }, []);
  
  // ...렌더링 로직
}
```

### 8.5 API 중복 문제 최종 해결 방안

#### 프론트엔드 측 해결책
```typescript
// 변경 전 (문제 있는 코드)
const API_BASE_URL = 'http://localhost:8000/api';
const fetchUser = () => fetch(`${API_BASE_URL}/api/users/profile`);

// 변경 후 (수정된 코드)
const API_BASE_URL = 'http://localhost:8000';
const fetchUser = () => fetch(`${API_BASE_URL}/api/users/profile`);
```

#### 백엔드 측 해결책
- API 라우터의 prefix 표준화 (`/api/{리소스_그룹}`)
- 라우터 정의 시에만 태그 지정, 등록 시 태그 재정의 않음
- 명확하고 일관된 태그 네이밍 (첫 글자 대문자)

### 8.6 테마별 API 그룹화 전략

#### Neon 테마 적용을 위한 API 그룹화

Neon 테마는 "Futuristic Neon Cyberpunk" 디자인을 지원하기 위해 특정 API 엔드포인트들을 그룹화하여 관리합니다:

1. **시각적 테마 관련 API**
   - `/api/themes/neon/settings` - 사용자별 테마 설정 관리
   - `/api/themes/neon/elements` - 네온 UI 요소 및 애니메이션 설정

2. **게임 스타일링 API**
   - `/api/games/{game_id}/themes/neon` - 게임별 네온 테마 적용
   - `/api/games/effects/neon` - 네온 이펙트 및 애니메이션 설정

3. **UI 효과 API**
   - `/api/ui/effects/glow` - 네온 글로우 효과 설정
   - `/api/ui/effects/pulse` - 펄싱 애니메이션 설정
   - `/api/ui/effects/flicker` - 네온 깜빡임 효과 설정

이러한 API들은 "Neon Theme" 태그로 그룹화하여 관리하는 것을 권장합니다.

이 문서는 Casino-Club F2P 프로젝트의 프론트엔드/백엔드/데이터 연동 작업을 위한 종합적인 가이드입니다. 디자인 보존과 효율적인 연동을 위해 점진적이고 체계적인 접근법을 제시합니다.

각 작업 단계에서 우선순위와 의존성을 고려하여 진행하며, 특히 API 중복 문제 해결에 주의를 기울여 개발해야 합니다.