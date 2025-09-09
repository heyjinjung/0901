# 2025-09-09 E2E 실패 테스트 티켓 초안 (3건)

## 개요
현재 Playwright 기준 통과 33/48 (68.8%), 실패 3건 집중 해결 필요. 나머지 12건 skip/조건부. 본 문서는 실패 3건을 추적 가능한 티켓 형식으로 구조화.

## 공통 환경
- 브라우저: Chromium (컨테이너)
- 환경 플래그: E2E_REQUIRE_STATS_PARITY=true, E2E_SHOP_SYNC=true
- Backend: /api/games/stats/me 정상(200)
- Frontend: /healthz 200, GlobalStore 하이드레이션 완료

---
## 1. Admin Points UI Guard Locator 불일치
- TestID: `admin_points_ui.spec.ts`
- 증상: data-testid='admin-guard-banner' 요소 미검출 → 테스트 실패
- 원인 추정: Admin Points 페이지 접근 전 가드 배너 렌더 타이밍 지연 또는 testid 누락/오탈자
- 재현 단계:
  1) 비관리자 계정 로그인
  2) /admin/points 이동
  3) guard banner 존재 대기 → timeout
- 기대 결과: 비관리자 접근 시 상단 경고 배너(data-testid='admin-guard-banner') 렌더
- 해결 방안:
  - 컴포넌트 마운트 즉시 렌더 (조건부 lazy 제거)
  - testid 상수화: `const ADMIN_GUARD_TESTID = 'admin-guard-banner'`
  - Playwright: `await page.getByTestId('admin-guard-banner').waitFor({ state: 'visible' });`
- 작업 항목:
  - [ ] 컴포넌트 testid 추가/확인
  - [ ] 지연 렌더 조건 제거
  - [ ] 테스트 재실행
- 담당/ETA: TBA / 0.5d

---
## 2. Auth Migration Legacy 토큰 마이그레이션 로직
- TestID: `auth_migration.spec.ts` (가칭)
- 증상: 레거시 저장소(예: localStorage 기존 키) → 신규 토큰 구조 전환 실패로 401 발생
- 원인 추정: 마이그레이션 훅 실행 순서가 GlobalStore hydrate 이전 혹은 키 명칭 mismatch
- 재현 단계:
  1) localStorage에 legacy_token_key=... 세팅
  2) 앱 최초 로드 → 자동 전환 기대
  3) /dashboard 접근 시 401
- 기대 결과: 마이그레이션 훅이 legacy 토큰 발견 → decode/검증 후 신규 storage 키로 저장 → 정상 인증 흐름
- 해결 방안:
  - 마이그레이션 로직을 App 루트 useEffect 최상단 배치
  - 실패 시 사용자에게 재로그인 유도 + 로컬 legacy 키 삭제
  - unifiedApi 초기화 이전 수행
- 작업 항목:
  - [ ] legacy 키 명세 문서화
  - [ ] 마이그레이션 함수 단위 테스트
  - [ ] E2E 재검증
- 담당/ETA: TBA / 0.5d

---
## 3. Daily Reward 버튼 타임아웃 / 모달 가시성
- TestID: `daily_reward_duplicate_toast.spec.ts` (및 관련)
- 증상: data-testid="open-daily-reward" 버튼 대기 중 timeout / 모달 감지 실패
- 원인 추정: 초기 렌더 시 조건부 상태로 버튼 비표시 또는 testid 동적 붙임 지연
- 재현 단계:
  1) user001 로그인
  2) 대시보드 로드 후 버튼 탐색 → timeout
- 기대 결과: 대시보드 첫 렌더 내 testid 포함 버튼 즉시 존재 → 클릭 후 모달 표시
- 해결 방안:
  - 버튼을 조건부 숨김 대신 disabled 상태로 유지 (UX 영향 최소)
  - testid 정적 부착
  - 모달 root에 고정 testid (예: daily-reward-modal)
  - Playwright: locator.fallback 전략 (getByTestId → role/button name 순)
- 작업 항목:
  - [ ] 컴포넌트 testid 정적화
  - [ ] disabled 전략 적용
  - [ ] 모달 testid 추가
  - [ ] 테스트 재실행
- 담당/ETA: TBA / 0.5d

---
## 우선순위/KPI
| 티켓 | 우선순위 | KPI 영향 | 비고 |
|------|----------|----------|------|
| Admin Guard | High | 권한 가드 신뢰성 | 보안/UI 테스트 안정성 |
| Auth Migration | High | 로그인 전환율 | 레거시 사용자 이탈 방지 |
| Daily Reward | High | 초기 리텐션/도파민 루프 | 핵심 루프 진입점 |

## 공통 완료 정의 (DoD)
- 관련 코드 PR 머지 + 테스트 green (Playwright 최소 3회 연속) + 0909.md 섹션 업데이트 + 개선안2 Drift Note 반영

## 후속
- 해결 후 0909.md P0 항목 체크 → E2E 통과율 KPI 섹션 갱신

(끝)
