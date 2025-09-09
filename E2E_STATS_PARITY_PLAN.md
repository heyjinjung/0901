# 🎮 E2E Stats Parity 승격 계획 (2025-09-07)

## 📊 현황 분석

### 1. 현재 상태
- Alembic head: 단일 (63d16ce09e51 - add_game_stats_fields_to_users)
- `/api/games/stats/me` 엔드포인트: 정상 작동 확인
- 프론트엔드 통계 정규화 시스템: 구현 완료 (gameStatsNormalizer.ts)
- 엔드포인트 포맷: `{ success: true, stats: {...} }` 표준화 완료
- 훅 마이그레이션: 레거시 훅 제거 및 useGlobalSync/useGameStats로 대체 완료

### 2. 해결해야 할 문제
- E2E_REQUIRE_STATS_PARITY=1 게이트 검증 미완료
- 전역 동기화 완전 검증 필요

## 🚀 실행 계획

### 1단계: 게이트 검증 실행
- `/api/games/stats/me` 200 확인 테스트 실행 (2회 연속)
- UI=API 파리티 PASS 테스트 실행 (3회 연속)

### 2단계: 파리티 적용 및 전환 확인
- E2E_REQUIRE_STATS_PARITY=1 상태로 추가 그린 테스트 실행
- 필요 시 deep 테스트 실행

### 3단계: STRICT 승격 및 문서화
- STRICT_STATS_PARITY=1 적용 및 테스트
- 변경사항 문서화 (api docs/20250808.md)
- OpenAPI 스키마 재수출 확인

## 📝 작업 체크리스트
- [ ] E2E_REQUIRE_STATS_PARITY=1 게이트 검증
  - [ ] `/api/games/stats/me` 200 확인 #1
  - [ ] `/api/games/stats/me` 200 확인 #2
  - [ ] UI=API 파리티 PASS #1
  - [ ] UI=API 파리티 PASS #2
  - [ ] UI=API 파리티 PASS #3

- [ ] 파리티 ON 상태 테스트
  - [ ] E2E_REQUIRE_STATS_PARITY=1 기본 테스트 그린
  - [ ] E2E_REQUIRE_STATS_PARITY=1 deep 테스트 그린

- [ ] 최종 승격 및 문서화
  - [ ] STRICT_STATS_PARITY=1 테스트 그린
  - [ ] api docs/20250808.md 변경 요약 추가
  - [ ] OpenAPI 스키마 재수출

## 🔍 검증 메서드
```powershell
# 1) 베이스 프로파일에서 게이트 검증(임시 parity ON)
$env:E2E_REQUIRE_STATS_PARITY = "1"; .\cc-manage.ps1 e2e:playwright; Remove-Item Env:E2E_REQUIRE_STATS_PARITY -ErrorAction SilentlyContinue

# 2) parity ON 상태로 1회 추가 그린 + deep(선택) 1회
$env:E2E_REQUIRE_STATS_PARITY = "1"; .\cc-manage.ps1 e2e:playwright; Remove-Item Env:E2E_REQUIRE_STATS_PARITY -ErrorAction SilentlyContinue
$env:E2E_REQUIRE_STATS_PARITY = "1"; .\cc-manage.ps1 e2e:playwright:deep; Remove-Item Env:E2E_REQUIRE_STATS_PARITY -ErrorAction SilentlyContinue

# 3) 안정화 후 STRICT 승격
$env:STRICT_STATS_PARITY = "1"; .\cc-manage.ps1 e2e:playwright; Remove-Item Env:STRICT_STATS_PARITY -ErrorAction SilentlyContinue
```
