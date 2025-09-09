# E2E Testing Guide - Casino-Club F2P

## 개요

이 프로젝트는 Playwright를 사용한 컨테이너 기반 E2E 테스트를 지원합니다. 테스트는 Docker Compose를 통해 격리된 환경에서 실행됩니다.

## 빠른 시작

### 기본 E2E 테스트 실행

```powershell
# 기본 테스트 (스킵 조건이 있는 테스트들은 제외)
./cc-manage.ps1 e2e

# 또는 직접 Docker Compose 사용
docker compose -f docker-compose.yml -f docker-compose.playwright.yml up --abort-on-container-exit --exit-code-from playwright playwright
```

### 특정 테스트 카테고리 활성화

```powershell
# Stats Parity 테스트 포함
./cc-manage.ps1 e2e stats

# 엄격한 Stats Parity 모드
./cc-manage.ps1 e2e strict

# Shop 동기화 테스트 포함
./cc-manage.ps1 e2e shop

# Realtime 이벤트 테스트 포함
./cc-manage.ps1 e2e realtime

# 여러 플래그 조합
./cc-manage.ps1 e2e stats,shop,realtime
```

## 환경 변수 플래그

### 필수 환경 변수

| 변수명 | 기본값 | 설명 |
|--------|---------|------|
| `BASE_URL` | `http://frontend:3000` | 프론트엔드 URL |
| `API_BASE_URL` | `http://backend:8000` | 백엔드 API URL |
| `E2E_INVITE_CODE` | `5858` | 테스트용 초대 코드 |

### 선택적 테스트 플래그

| 플래그 | 환경 변수 | 설명 |
|--------|-----------|------|
| `stats` | `E2E_REQUIRE_STATS_PARITY=1` | UI/API 통계 파리티 테스트 활성화 |
| `strict` | `STRICT_STATS_PARITY=1` | 엄격한 통계 파리티 모드 |
| `shop` | `E2E_REQUIRE_SHOP_SYNC=1` | 상점 동기화 테스트 활성화 |
| `realtime` | `E2E_REQUIRE_REALTIME=1` | 실시간 이벤트 테스트 활성화 |

### 비활성화 플래그

| 환경 변수 | 설명 |
|-----------|------|
| `E2E_DISABLE_STATS_PARITY=1` | 통계 파리티 테스트 완전 비활성화 |

## 테스트 카테고리별 상세

### 1. 기본 테스트 (항상 실행)
- 접근성 테스트
- 반응형 UI 테스트
- SEO 메타데이터 테스트
- 기본 인증 플로우
- 기본 UI 네비게이션

### 2. Stats Parity 테스트 (`E2E_REQUIRE_STATS_PARITY=1`)
- UI 표시 통계와 API 응답 일치성 검증
- 게임 통계 동기화 확인
- 사용자 프로필 데이터 일관성

### 3. Shop 동기화 테스트 (`E2E_REQUIRE_SHOP_SYNC=1`)
- 상점 구매 후 잔액 동기화
- 인벤토리 업데이트 확인
- 골드/젬 잔액 일관성

### 4. Realtime 이벤트 테스트 (`E2E_REQUIRE_REALTIME=1`)
- WebSocket 연결 및 재연결
- 실시간 프로필 업데이트
- 이벤트 중복 제거
- 구매 업데이트 실시간 반영

## 일반적인 스킵 이유

테스트가 스킵되는 일반적인 이유들:

1. **환경 변수 미설정**: 특정 플래그가 활성화되지 않음
2. **API 엔드포인트 불가용**: 개발 중이거나 미구현된 기능
3. **라우터 의존성**: 특정 라우트가 환경에 따라 비활성화됨
4. **외부 서비스 의존성**: Kafka, ClickHouse 등 비활성화된 서비스

## 트러블슈팅

### 일반적인 문제들

#### 1. Docker Compose 경고
```
warning msg="docker-compose.playwright.yml: the attribute `version` is obsolete"
```
**해결**: 이 경고는 무시해도 됩니다. Docker Compose v2에서는 `version` 속성이 더 이상 필요하지 않습니다.

#### 2. PowerShell 링크 오류
```
'http://_vscodecontentref_/5' 용어가 cmdlet으로 인식되지 않습니다
```
**해결**: VSCode가 생성한 링크를 PowerShell이 명령어로 잘못 해석한 것입니다. 파일명을 직접 입력하세요:
```powershell
docker compose -f docker-compose.yml -f docker-compose.playwright.yml up ...
```

#### 3. 테스트 타임아웃
```
[ws_profile_update_smoke] GOLD did not stabilize within timeout
```
**해결**: 네트워크나 서버 응답이 느린 경우 발생할 수 있습니다. 테스트는 여전히 통과할 수 있습니다.

### 환경 문제 진단

```powershell
# 1. 서비스 상태 확인
./cc-manage.ps1 status

# 2. 헬스체크 확인
./cc-manage.ps1 health

# 3. 데이터베이스 연결 확인
./cc-manage.ps1 db-check

# 4. 백엔드 로그 확인
./cc-manage.ps1 logs backend

# 5. 프론트엔드 로그 확인
./cc-manage.ps1 logs frontend
```

## 수동 실행 (고급)

환경 변수를 직접 설정하여 실행:

```powershell
# 환경 변수 설정
$env:E2E_REQUIRE_STATS_PARITY = '1'
$env:STRICT_STATS_PARITY = '1'

# 테스트 실행
docker compose -f docker-compose.yml -f docker-compose.playwright.yml up --abort-on-container-exit --exit-code-from playwright playwright

# 정리
Remove-Item Env:E2E_REQUIRE_STATS_PARITY -ErrorAction SilentlyContinue
Remove-Item Env:STRICT_STATS_PARITY -ErrorAction SilentlyContinue
```

## CI/CD 통합

CI 환경에서는 다음과 같이 사용할 수 있습니다:

```yaml
# GitHub Actions 예시
- name: Run E2E Tests
  env:
    E2E_REQUIRE_STATS_PARITY: "1"
    STRICT_STATS_PARITY: "1"
  run: |
    docker compose -f docker-compose.yml -f docker-compose.playwright.yml up --abort-on-container-exit --exit-code-from playwright playwright
```

## 결과 해석

### 성공적인 실행
- `37 passed / 12 skipped / 0 failed` 형태의 결과
- Exit code 0
- 모든 핵심 기능 테스트 통과

### 실패 진단
- 로그에서 실패한 테스트 확인
- 스크린샷 및 비디오 결과 검토 (`logs/playwright/` 디렉토리)
- 환경 변수 설정 재확인

---

이 가이드를 통해 E2E 테스트를 효과적으로 실행하고 문제를 해결할 수 있습니다.