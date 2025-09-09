# 🚀 Casino-Club F2P API 맵핑 문서 (Consolidated)

## 📋 개요
이 문서는 Casino-Club F2P 프로젝트의 백엔드 API 구조와 실제 동작 현황, 그리고 인증 시스템 문제 진단/해결 내역을 하나의 문서로 통합 제공합니다. 중복 문서를 제거하고 이 파일(`API_MAPPING.md`)만을 최신 소스로 유지합니다.

## 🏗️ API 구조

### 1) 인증 시스템 (Authentication)
| 라우터 파일 | 엔드포인트 접두사 | 주요 기능 | 상태 |
|------------|-----------------|---------|------|
| `auth.py` | `/api/auth` | JWT 인증, 로그인/회원가입 | 통합 완료 ✅ |

#### 1.1 인증 API 목록과 명세

| 기능 | 메소드 | 경로 | 설명 | 인증 |
|------|--------|-----|------|-----|
| 초대코드 검사 | POST | `/api/auth/verify-invite` | 초대 코드 유효성 검사 | 불필요 |
| 회원가입 | POST | `/api/auth/signup` | 새로운 사용자 등록 | 불필요 |
| 로그인 | POST | `/api/auth/login` | 일반 사용자 로그인 | 불필요 |
| 관리자 로그인 | POST | `/api/auth/admin/login` | 관리자 로그인 | 불필요 |
| 토큰 갱신 | POST | `/api/auth/refresh` | 리프레시 토큰으로 액세스 토큰 재발급 | 필요(리프레시) |
| 로그아웃 | POST | `/api/auth/logout` | 액세스 토큰 블랙리스트 처리 등 | 필요 |

요청/응답 예시(핵심)
- 회원가입 요청
   {
      "site_id": "string",
      "password": "string",    // 최소 4자 이상
      "nickname": "string",
      "phone_number": "string",
      "invite_code": "5858"
   }
- 회원가입 성공 응답
   {
      "user_id": 1,
      "site_id": "string",
      "nickname": "string",
      "message": "signup success"
   }

검증 규칙
- 초대 코드 5858 확인(개발환경: 무한 재사용 허용)
- 비밀번호 4자 이상
- 아이디/닉네임/전화번호 중복 검사
- 보안 이벤트 로깅

토큰 수명(권장)
- access: 1시간
- refresh: 7일

### 2) 사용자 관리 (User Management)
| 라우터 파일 | 엔드포인트 접두사 | 주요 기능 | 상태 |
|------------|-----------------|---------|------|
| `users.py` | `/api/users` | 사용자 프로필, 설정 | 활성화 |
| `invite_router.py` | `/api/invite` | 초대 코드 시스템 | 활성화 |
| `segments.py` | `/api/segments` | 사용자 세그먼트 관리 | 활성화 |

### 3) 게임 시스템 (Game Systems)
| 라우터 파일 | 엔드포인트 접두사 | 주요 기능 | 상태 |
|------------|-----------------|---------|------|
| `games.py` | `/api/games` | 게임 컬렉션 | 활성화 |
| `prize_roulette.py` | `/api/games/roulette` | 룰렛 게임 | 활성화 |
| `gacha.py` | `/api/gacha` | 가챠 시스템 (레거시) | Deprecated/삭제 예정 |
| `games.py` | `/api/games/gacha` | 가챠 시스템(통합) | 활성화 |
| `rps.py` | `/api/games/rps` | 가위바위보 게임 | 활성화 |
| `game_api.py` | `/api/game` | 통합 게임 API | 개발 중 |

### 4) 보상 시스템 (Reward Systems)
| 라우터 파일 | 엔드포인트 접두사 | 주요 기능 | 상태 |
|------------|-----------------|---------|------|
| `rewards.py` | `/api/rewards` | 보상 관리 | 활성화 |
| `unlock.py` | `/api/unlock` | 컨텐츠 잠금해제 | 활성화 |
| `adult_content.py` | `/api/adult` | 성인 컨텐츠 관리 | 활성화 |

### 5) 참여 시스템 (Engagement Systems)
| 라우터 파일 | 엔드포인트 접두사 | 주요 기능 | 상태 |
|------------|-----------------|---------|------|
| `missions.py` | `/api/missions` | 미션 시스템 | 활성화 |
| `events.py` | `/api/events` | 이벤트 관리 | 활성화 |
| `quiz.py` | `/api/quiz` | 심리 테스트 | 활성화 |
| `admin_events.py` | `/api/admin/events` | 관리자 이벤트 CRUD/강제보상/시드 | 신규 반영 ✅ |

#### 5.1 관리자 이벤트(Admin Events) 상세

| 기능 | 메소드 | 경로 | 설명 | 인증 |
|------|--------|------|------|------|
| 이벤트 생성 | POST | `/api/admin/events/` | 이벤트 신규 생성 | 관리자 |
| 이벤트 목록 | GET | `/api/admin/events/` | 활성(기본) / 비활성 포함(optional) 조회 | 관리자 |
| 이벤트 수정 | PUT | `/api/admin/events/{event_id}` | 필드 일부/전체 업데이트 | 관리자 |
| 이벤트 비활성화 | POST | `/api/admin/events/{event_id}/deactivate` | is_active False 처리 | 관리자 |
| 참여 목록 | GET | `/api/admin/events/{event_id}/participations` | 완료/보상 필터 조회 | 관리자 |
| 강제 보상 지급 | POST | `/api/admin/events/{event_id}/force-claim/{user_id}` | 완료 여부 무관 지급(중복 시 "이미 보상 수령") | 관리자 |
| 모델 지수 이벤트 시드 | POST | `/api/admin/events/seed/model-index` | 없으면 생성, 있으면 기존 반환 (idempotent) | 관리자 |

보상/요구사항 구조 예시
```json
{
   "rewards": { "gold": 5000, "exp": 1000 },
   "requirements": { "model_index_points": 1000 }
}
```

일반 사용자 이벤트 상호작용 (events.py)
| 기능 | 메소드 | 경로 | 설명 |
|------|--------|------|------|
| 참여 | POST | `/api/events/join` | {"event_id": number} 로 참여 (중복 참여 시 기존 participation 반환) |
| 진행 업데이트 | PUT | `/api/events/progress/{event_id}` | {"progress": {"model_index_points": 1000}} 식 누적/병합 |
| 보상 수령 | POST | `/api/events/claim/{event_id}` | 완료 & 미수령 조건 충족 시 지급 |

테스트 커버리지 (2025-08-21)
| 테스트 파일 | 검증 범위 |
|-------------|-----------|
| `app/tests/test_admin_events.py` | 생성/목록/시드 멱등/참여-진행-완료-보상/강제보상 멱등 |

설계 노트
1. force-claim 은 완료 상태가 아니어도 지급 (추후 감사 로그 필요 TODO)
2. 진행(progress)은 JSON merge 방식 (키 단위 overwrite) → 향후 누적 로직 필요 시 서비스 계층 확장
3. participation_count 는 EventService.get_active_events 시 집계 후 임시 속성 부여 → 직렬화 스키마 반영
4. 관리자 시드 이벤트는 title 고정("모델 지수 도전 이벤트") 으로 존재 여부 판단 -> 향후 다국어 시 title+type 조합 키 고려


### 6) 상점 및 결제 (Shop & Payments)
| 라우터 파일 | 엔드포인트 접두사 | 주요 기능 | 상태 |
|------------|-----------------|---------|------|
| `shop.py` | `/api/shop` | 상점 시스템 | 활성화 |
| `corporate.py` | `/v1/corporate` | 기업 연동 | 활성화 |

### 7) 커뮤니케이션 (Communication)
| 라우터 파일 | 엔드포인트 접두사 | 주요 기능 | 상태 |
|------------|-----------------|---------|------|
| `chat.py` | `/api/chat` | 채팅 시스템 | 활성화 |
| `notification.py` | `/api/notification` | 알림 시스템 | 활성화 |
| `feedback.py` | `/api/feedback` | 피드백 관리 | 활성화 |

### 8) AI 및 개인화 (AI & Personalization)
| 라우터 파일 | 엔드포인트 접두사 | 주요 기능 | 상태 |
|------------|-----------------|---------|------|
| `ai.py` | `/api/ai` | AI 서비스 | 활성화 |
| `personalization.py` | `/api/personalize` | 개인화 시스템 | 활성화 |
| `recommendation.py` | `/api/recommendation` | 추천 시스템 | 활성화 |

### 9) 분석 및 관리자 (Analytics & Admin)
| 라우터 파일 | 엔드포인트 접두사 | 주요 기능 | 상태 |
|------------|-----------------|---------|------|
| `admin.py` | `/api/admin` | 관리자 기능 | 활성화 |
| `tracking.py` | `/api/tracking` | 사용자 행동 추적 | 활성화 |
| `analyze.py` | `/api/analyze` | 데이터 분석 | 활성화 |
| `dashboard.py` | `/api/dashboard` | 대시보드 | 활성화 |

## 🧩 인증 시스템 문제 진단과 해결 내역(통합)

문제 요약
- `/api/auth/signup` 404, 실제는 `/auth/register` 존재 등 라우팅 불일치
- `app/routers/auth.py`와 `app/routers/auth/` 디렉토리 공존으로 import 충돌 가능성
- User, SecurityEvent 등 모델 관계 설정 일부 미비

권장 해결책(적용 지침)
1. 라우터 단일화: `app/routers/auth/` 디렉토리를 제거하고 `app/routers/auth.py`만 사용
2. prefix 일원화: 모두 `/api/auth` 사용(클라이언트도 동일 경로로 수정)
3. 엔드포인트 정리: verify-invite/signup/login/admin/login/refresh/logout 제공
4. 모델 관계 보정: User ↔ SecurityEvent FK 등 정상화

참고 구조
```
app/
├─ routers/
│  ├─ auth.py               # main.py에서 참조되는 단일 라우터
│  └─ ...
└─ auth/
    └─ auth_endpoints.py     # 기능은 auth.py로 흡수/정리
```

HTTP 상태 코드 가이드
- 200: 성공
- 400: 잘못된 요청(유효하지 않은 초대 코드, 중복 계정 등)
- 401: 인증 실패(잘못된 자격증명)
- 403: 권한 없음
- 404: 경로 없음
- 500: 서버 내부 오류

## 🔄 API 통합 계획(요약)

1) 인증 시스템: 통합 완료, 프리픽스/엔드포인트 정리 및 테스트 지속
2) 사용자/세그먼트/초대: 엔드포인트 활성 유지, 검증/문서 보강
3) 게임: 레거시 `gacha.py` 제거 예정, `games.py` 통합 경로 우선
4) 보상/참여/상점/커뮤니케이션/AI/관리: 현행 유지 + 응답 포맷 표준화

## 📊 상태 대시보드(요약)

| 카테고리 | 구현 | 테스트 | FE 연동 |
|---------|-----|-------|--------|
| 인증 | ✅ | 진행 중 | 진행 중 |
| 사용자 | ✅ | 일부 | 진행 중 |
| 게임 | 대부분 | 일부 | 진행 중 |
| 보상/참여/상점/커뮤니케이션/AI/관리 | 활성 | 일부 | 진행 중 |

## 📝 연동 체크리스트(요약)

- [ ] 모든 엔드포인트 문서 최신화(OpenAPI 포함)
- [ ] 응답 형식 표준화 및 에러 포맷 통일
- [ ] CORS/보안 검토 및 부하 테스트
- [ ] 프론트엔드 연동 점검

## 🗃️ 파일 통합 보고(요약)

- auth.py ← auth_simple.py 기능 흡수, 단일화 완료
- dependencies/config/models 관련 simple 파생본 정리, 중복 제거
- 유지 대상 simple 모듈은 특수 목적 한정(simple_logging.py 등)

## 변경 이력
- 2025-08-12: `API_MAPPING.md`와 `API_MAPPING_UPDATED.md`를 통합하여 이 파일만 유지. 인증 엔드포인트 명세와 문제 해결 내역 반영.
- 2025-08-21: Admin Events 섹션 및 Streak status 엔드포인트 스펙/테스트 추가 (`/api/streak/status`).

### 부록: Streak API 주요 엔드포인트 요약
| 기능 | 메소드 | 경로 | 파라미터 | 설명 |
|------|--------|------|----------|------|
| 현재 상태 | GET | `/api/streak/status` | `action_type` (query, 기본 SLOT_SPIN) | 현재 카운트/TTL/다음 보상 힌트 |
| 증가(Tick) | POST | `/api/streak/tick` | `{action_type?}` | 하루 1회 증가(일일 lock), 출석 기록 |
| 미리보기 | GET | `/api/streak/preview` | `action_type` | 오늘/내일 보상 수치, claimable 플래그 |
| 보상 수령 | POST | `/api/streak/claim` | `{action_type?}` | 일일 보상(멱등키 기반) |
| 보호 토글 | POST | `/api/streak/protection` | `{action_type?, enabled}` | 보호 설정 on/off |
| 보호 상태 | GET | `/api/streak/protection` | `action_type` | 현재 보호 여부 |
| 출석 히스토리 | GET | `/api/streak/history` | `action_type, year, month` | 월별 출석 일자 목록 |

프론트 404 원인 분석 요약: Next dev에서 BASE 미설정 시 상대 `/api/streak/status` 호출이 Next 자체 라우트로 흘러 404 → simpleApi.js 내 fallback(포트 3000 조건) 이미 존재. 실제 404 발생 시 환경변수(NEXT_PUBLIC_API_BASE) 미설정/토큰 인증 문제 우선 확인.
