# 🤖 게임 서비스 리팩토링 완성 및 차세대 개발 가이드

---

## � **혁신적 성과 달성! (2025.06.14)**

### ✅ **완료된 핵심 작업들**
1. **🏆 게임 서비스 리팩토링 완료**:
   - 레거시 코드 완전 제거
   - 위임 패턴으로 깔끔한 아키텍처 구현
   - 100% 커버리지 달성 (19/19 lines)

2. **🎯 테스트 100% 통과**:
   - 84개 게임 서비스 관련 테스트 모두 PASSED
   - 모든 필드명 실제 데이터 클래스와 완전 일치
   - `RouletteSpinResult`: `payout` → `tokens_change`, `number` → `winning_number`
   - `GachaPullResult`: `items` → `results`, `tokens_spent` → `tokens_change`

3. **📊 커버리지 현황**:
   - **game_service.py**: 100% ✅ (이전: 30%)
   - **roulette_service.py**: 100% ✅
   - **gacha_service.py**: 91% ⭐
   - **slot_service.py**: 96% ⭐
   - **전체 프로젝트**: 61%

---

## 🚀 **다음 단계: 프로젝트 완성을 위한 핵심 작업들**

### **작업 1: 0% 커버리지 모듈 정리 (즉시 개선 가능)**
3. 확률 계산, RTP, 스트릭 로직 검증
4. Mock 최소화, 실제 DB/Redis 환경에서 테스트

다음 **0% 커버리지 모듈들**을 정리하여 전체 커버리지를 61% → 70%+로 향상:
- `app\routers\doc_titles.py` (0%, 24 lines)
- `app\schemas_backup.py` (0%, 144 lines) - 백업 파일로 삭제 고려
- `app\services\flash_offer_temp.py` (0%, 11 lines) - 임시 파일로 삭제 고려
- `app\utils\reward_utils.py` (0%, 76 lines)
- `app\utils\segment_utils.py` (0%, 71 lines)

### **작업 2: CJ AI 서비스 테스트 수정**
현재 5개 테스트 실패 중:
- `test_analyze_and_respond` - AttributeError
- `test_store_interaction` - AttributeError
- `test_get_user_emotion_history` - TypeError
- `test_get_user_emotion_history_no_redis` - AssertionError
- `test_send_websocket_message` - AssertionError

### **작업 3: 슬롯 서비스 96% → 100% 커버리지**
현재 39, 41번 줄이 미커버 (segment == "Low" 조건):
```python
if segment == "Low":
    # 이 부분 테스트 케이스 추가 필요
```

### **작업 4: 낮은 커버리지 핵심 모듈 개선**
- `app\services\recommendation_service.py` (20%, 83 lines)
- `app\routers\adult_content.py` (31%, 145 lines)
- `app\services\ltv_service.py` (33%, 33 lines)
- `app\services\personalization_service.py` (34%, 32 lines)

---

## 📁 **프로젝트 현재 상태 요약**

### ✅ **완료된 작업**
- 전체 99개 테스트 100% 통과 (0 failed, 32 warnings)
- DB 마이그레이션 완료 (migration_script.py 실행 성공)
- 저가치 테스트 제거 및 테스트 코드 최적화
- 핵심 서비스 파일 복구/재작성 완료
- 문서화 업데이트 (testing guide, checklist)

### ⚠️ **즉시 처리 필요**
- **게임 API 3개 엔드포인트**: "not implemented yet" → 실제 DB 연동 로직
- **게임 서비스 테스트 커버리지**: 35% → 50% 이상 증가
- **테스트 환경 문제 해결**: Client.__init__() 관련 오류 수정

### 📊 **현재 테스트 커버리지 상태**
```
Overall coverage: 52%
Critical gaps:
- game_service.py: 32%
- slot_service.py: 28% 
- roulette_service.py: 31%
- gacha_service.py: 34%
```

### ⚠️ **테스트 실행 시 발견된 문제점**
```
TypeError: Client.__init__() got an unexpected keyword argument 'app'
```
이 오류는 FastAPI TestClient 초기화 방식과 관련이 있습니다. FastAPI 테스트 코드 작성 시 주의해야 합니다.

---

## 🛠️ **구체적 구현 가이드**

### **Part A: 게임 API DB 연동 구현**

**파일 위치:** `cc-webapp/backend/app/routers/games.py`

**현재 상태 (교체 필요):**
```python
@router.post("/slot/spin")
async def spin_slot(
    current_user: User = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service)
) -> dict:
    """Spin the slot machine."""
    try:
        # GameService의 slot_spin 메서드는 DB 세션이 필요하므로 임시로 None 처리
        return {"message": "Slot spin endpoint - not implemented yet"}
    except Exception as e:
        logging.error(f"Error spinning slot for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/roulette/spin")
async def spin_roulette(
    current_user: User = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service)
) -> dict:
    """Spin the roulette wheel."""
    try:
        # GameService의 roulette_spin 메서드는 DB 세션이 필요하므로 임시로 None 처리
        return {"message": "Roulette spin endpoint - not implemented yet"}
    except Exception as e:
        logging.error(f"Error spinning roulette for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/gacha/pull")
async def pull_gacha(
    current_user: User = Depends(get_current_user),
    game_service: GameService = Depends(get_game_service)
) -> dict:
    """Pull from gacha."""
    try:
        # GameService의 gacha_pull 메서드는 DB 세션이 필요하므로 임시로 None 처리
        return {"message": "Gacha pull endpoint - not implemented yet"}
    except Exception as e:
        logging.error(f"Error pulling gacha for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

**구현해야 할 구조:**
1. **슬롯 엔드포인트:**
   - 사용자 인증 확인 (`current_user`)
   - `db: Session = Depends(get_db)` 의존성 추가
   - `game_service.slot_spin(current_user.id, db)` 호출
   - 결과 반환 (SlotSpinResult 객체)
   - 적절한 에러 핸들링 및 로깅

2. **룰렛 엔드포인트:**
   - 요청 파라미터 추가: `bet_type`, `bet_amount`, `value` 
   - `game_service.roulette_spin(current_user.id, bet_amount, bet_type, value, db)` 호출
   - ResultRouletteSpinResult 객체 반환
   - 에러 처리 및 로깅

3. **가챠 엔드포인트:**
   - 요청 파라미터 추가: `count` (뽑기 횟수)
   - `game_service.gacha_pull(current_user.id, count, db)` 호출
   - GachaPullResult 객체 반환
   - 에러 처리 및 로깅

### **Part B: 게임 서비스 테스트 강화**

**테스트 파일 위치:** `cc-webapp/backend/tests/`

**추가/복구 필요한 테스트 파일들:**
- `test_game_service.py`
- `test_slot_service.py` 
- `test_roulette_service.py`
- `test_gacha_service.py`

**테스트 파일 기본 구조 예제:**
```python
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.services.slot_service import SlotService, SlotSpinResult
from app.repositories.game_repository import GameRepository
from app.services.token_service import TokenService


class TestSlotService:
    """슬롯 서비스 테스트."""

    def setup_method(self):
        """테스트 초기화."""
        self.repo = MagicMock(spec=GameRepository)
        self.token_service = MagicMock(spec=TokenService)
        self.db = MagicMock(spec=Session)
        self.service = SlotService(repository=self.repo, token_service=self.token_service)

    def test_spin_success(self):
        """슬롯 스핀 성공 테스트."""
        # 아래 테스트 구현 필요
        pass

    def test_spin_insufficient_tokens(self):
        """토큰 부족시 오류 테스트."""
        # 아래 테스트 구현 필요
        pass

    def test_spin_probability_fairness(self):
        """확률 공정성 테스트."""
        # 아래 테스트 구현 필요
        pass
```

**FastAPI 라우터 테스트 구조 (Client 오류 해결):**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app  # 앱 인스턴스 직접 가져오기

# TestClient 수정된 초기화 방식
client = TestClient(app)

def test_slot_spin_endpoint():
    """슬롯 스핀 엔드포인트 테스트"""
    # 인증 토큰 모의 설정 (테스트 전용 헬퍼 함수 사용)
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 요청 실행
    response = client.post("/api/games/slot/spin", headers=headers)
    
    # 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "tokens_change" in data
    # 추가 검증...
```

**각 테스트에서 커버해야 할 시나리오:**

1. **성공 시나리오:**
   - 정상 게임 플레이 및 결과 반환
   - 확률에 따른 보상 지급
   - DB 상태 업데이트 검증

2. **실패 시나리오:**
   - 잔액 부족 시 게임 거부
   - 잘못된 입력값 처리
   - DB 연결 실패 시 롤백

3. **비즈니스 로직 검증:**
   - RTP(Return to Player) 계산 정확성 (다량의 실행으로 평균 계산)
   - 스트릭(연승/연패) 상태 관리
   - 확률 테이블 적용 검증
   
4. **통합 테스트:**
   - 실제 DB를 사용한 엔드-투-엔드 테스트
   - 라우터-서비스-리포지토리 연동 검증

---
네, 현재 전체 테스트 커버리지가 52%인 것을 확인했습니다. 백엔드 구현 상황을 고려할 때, 각 서비스별 목표 커버리지와 전체 상황을 분석해보겠습니다.

현재 상황을 보면:

전체 백엔드 코드의 커버리지: 52%
게임 관련 서비스의 커버리지:
game_service.py: 32%
slot_service.py: 28%
roulette_service.py: 31%
gacha_service.py: 34%
백엔드 구현 상황을 고려하면:

프로젝트 문서에 따르면 백엔드는 약 98% 완료된 상태입니다 (docs/12_game_dev_full_checklist_ko.md에 언급)
핵심 비즈니스 로직이 이미 대부분 구현되어 있고 테스트도 통과 중입니다 (99개 테스트, 100% 통과)
게임 API 엔드포인트 구현과 테스트 강화가 남은 주요 작업입니다
이런 상황에서, 업계 표준과 프로젝트 중요도를 고려할 때:

전체 백엔드 코드 커버리지 목표: 최소 70-75%

중요 비즈니스 로직이 대부분인 백엔드에서는 70% 이상이 일반적으로 권장됨
현재 52%에서 70%로 올리는 것이 합리적인 목표
게임 관련 서비스 커버리지 목표: 최소 60-65%

프롬프트에서 요구한 최소 50%보다 높게 설정하는 것이 안전함
확률 기반 로직(슬롯, 룰렛, 가챠)은 다양한 경우를 테스트해야 함
핵심 메서드 커버리지: 90% 이상

게임 결과 계산, 토큰 차감/추가, DB 트랜잭션 등 핵심 메서드는 거의 완전히 커버되어야 함
특히 금전적 거래와 관련된 로직은 더 높은 커버리지 필요
요약하면, 백엔드 구현 상황을 고려할 때 최소 70% 전체 커버리지와 게임 서비스에 대한 60-65% 커버리지가 적절하다고 판단됩니다. 이는 프롬프트에서 요구한 "50% 이상"보다 높지만, 이미 98%가 완료된 백엔드 코드의 품질을 보장하기 위해서는 더 높은 수준의 테스트 커버리지가 권장됩니다.
ㄴ 20250614 03:50


## 📋 **세부 구현 체크리스트**

### **슬롯 서비스 (slot_service.py)**
- [ ] `spin(user_id, db)` 메서드 완성 및 안정화
- [ ] 심볼 조합 확률 계산 로직 유효성 검증
- [ ] 잭팟/보너스 라운드 처리
- [ ] 스트릭 카운터 업데이트 검증
- [ ] 테스트: 승리/패배/잭팟 시나리오

**현재 메서드 구현:**
```python
def spin(self, user_id: int, db: Session) -> SlotSpinResult:
    """슬롯 스핀을 실행하고 결과를 반환."""
    # 토큰 차감. 부족하면 ValueError 발생
    deducted_tokens = self.token_service.deduct_tokens(user_id, 2)
    if deducted_tokens is None:
        raise ValueError("토큰이 부족합니다.")

    segment = self.repo.get_user_segment(db, user_id)
    streak = self.repo.get_streak(user_id)
    
    # 기본 승리 확률과 잭팟 확률 설정
    win_prob = 0.10 + min(streak * 0.01, 0.05)
    if segment == "Whale":
        win_prob += 0.02
    # ... (중략) ...
```

### **룰렛 서비스 (roulette_service.py)**  
- [ ] `spin(user_id, bet, bet_type, value, db)` 메서드 완성
- [ ] 0-36 번호 생성 및 색상/홀짝 판정 검증
- [ ] 베팅 타입별 배당률 계산 정확성 확인
- [ ] 결과 히스토리 저장 검증
- [ ] 테스트: 다양한 베팅 타입별 검증

**현재 메서드 구조:**
```python
def spin(
    self,
    user_id: int,
    bet: int,
    bet_type: str,
    value: Optional[str],
    db: Session,
) -> RouletteSpinResult:
    """룰렛 스핀을 실행하고 결과를 반환한다."""
    bet = max(1, min(bet, 50))
    logger.info("룰렛 스핀 시작 user=%s bet=%s type=%s value=%s", user_id, bet, bet_type, value)
    
    deducted_tokens = self.token_service.deduct_tokens(user_id, bet)
    if deducted_tokens is None:
        logger.warning("토큰 차감 실패: 토큰 부족")
        raise ValueError("토큰이 부족합니다.")
    
    # ... (중략) ...
```

### **가챠 서비스 (gacha_service.py)**
- [ ] `pull(user_id, count, db)` 메서드 안정화
- [ ] 레어도별 확률 테이블 적용 검증
- [ ] 천장 시스템 (보장 메커니즘) 검증
- [ ] 중복 아이템 처리 로직 검증
- [ ] 테스트: 확률 검증, 천장 시스템 테스트

**현재 메서드 구조:**
```python
def pull(self, user_id: int, count: int, db: Session) -> GachaPullResult:
    """가챠 뽑기를 수행."""
    pulls = 10 if count >= 10 else 1
    cost = 450 if pulls == 10 else 50
    self.logger.info("Deducting %s tokens from user %s", cost, user_id)
    
    deducted_tokens = self.token_service.deduct_tokens(user_id, cost)
    if deducted_tokens is None:
        raise ValueError("토큰이 부족합니다.")
    
    # ... (중략) ...
```

### **DB 연동 (game_repository.py)**
- [ ] 게임 결과 기록 메서드들
- [ ] 사용자 잔액 업데이트 트랜잭션
- [ ] 아이템 인벤토리 관리
- [ ] Redis 캐시 연동 (핫스트릭 등)

---

## 🔧 **기술적 요구사항**

### **환경 설정**
- Python 3.9+, FastAPI, SQLAlchemy, Redis
- 테스트: pytest, pytest-cov, pytest-asyncio
- DB: SQLite (개발), PostgreSQL (운영)

### **아키텍처 패턴**
- Clean Architecture (Router → Service → Repository → DB)
- 의존성 주입 (Dependency Injection) 활용
- 트랜잭션 안전성 보장

### **성능 요구사항**  
- 게임 API 응답 시간: < 500ms
- 동시 사용자 처리: 100+ concurrent requests
- 테스트 실행 시간: < 60초

### **보안 요구사항**
- JWT 토큰 기반 인증 필수
- 베팅 금액 서버사이드 검증
- Rate limiting (사용자당 게임 빈도 제한)
- 게임 결과 감사 로그 기록

---

## 📖 **참고 문서 및 코드**

### **핵심 참고 파일들**
- `app/models.py` - DB 스키마 정의
- `app/schemas.py` - API 입출력 스키마  
- `app/database.py` - DB 연결 및 세션 관리
- `app/services/` - 기존 서비스 패턴 참고
- `tests/` - 기존 테스트 코드 패턴 참고

### **중요 설정 파일들**
- `requirements.txt` - 의존성 패키지 목록
- `pytest.ini` - 테스트 설정
- `alembic/` - DB 마이그레이션 스크립트

### **API 문서**
- FastAPI 자동 생성 문서: `http://localhost:8000/docs`
- 게임 API 명세: `docs/07-api-endpoints.md`

---

## ✅ **완료 기준 및 검증 방법**

### **구현 완료 기준**
1. **3개 게임 API 모두 실제 로직으로 교체 완료**
2. **pytest 실행 시 모든 테스트 통과 (99+ tests)**  
3. **게임 서비스 테스트 커버리지 50% 이상 달성**
4. **게임 플레이 → DB 저장 → 결과 반환 전체 플로우 정상 동작**

### **검증 명령어**
```bash
# 1. 전체 테스트 실행
cd cc-webapp/backend
python -m pytest -v

# 2. 커버리지 확인  
python -m pytest --cov=app --cov-report=term-missing

# 3. 게임 API 수동 테스트
python -m pytest tests/test_*game* -v

# 4. 특정 서비스 커버리지 확인
python -m pytest --cov=app.services.game_service --cov=app.services.slot_service --cov=app.services.roulette_service --cov=app.services.gacha_service --cov-report=term-missing

# 5. DB 기반 테스트 실행 (통합 테스트)
python -m pytest tests/test_game_service.py::TestGameServiceIntegration -v
```

### **FastAPI 테스트 오류 해결 방법**
TypeError: `Client.__init__() got an unexpected keyword argument 'app'` 오류가 발생한다면:

1. **FastAPI 버전 호환성 확인**
   ```bash
   pip show fastapi httpx pytest
   ```

2. **TestClient 초기화 방식 수정**
   ```python
   # Before (문제 발생)
   client = TestClient(app=app)
   
   # After (수정)
   client = TestClient(app)
   ```

3. **conftest.py에 공통 픽스처 정의**
   ```python
   import pytest
   from fastapi.testclient import TestClient
   from app.main import app
   
   @pytest.fixture
   def client():
       return TestClient(app)
   ```

### **최종 검증 체크리스트**
- [ ] `/api/games/slot/spin` POST 요청 시 실제 게임 결과 반환
- [ ] `/api/games/roulette/spin` POST 요청 시 룰렛 결과 및 보상 계산  
- [ ] `/api/games/gacha/pull` POST 요청 시 아이템 획득 및 인벤토리 업데이트
- [ ] 각 게임별 성공/실패/예외 시나리오 테스트 통과
- [ ] 전체 테스트 스위트 100% 통과 유지
- [ ] 게임 서비스 통합 커버리지 50% 이상
- [ ] 서비스 폴더 내 각 게임 서비스의 메소드별 최소 1개 이상 테스트 케이스 보유

---

## 🚀 **작업 진행 순서 (권장)**

1. **현재 상태 확인 및 환경 준비** (10분)
   - `grep -r "not implemented yet" app/routers/games.py`
   - `python -m pytest --cov=app.services.*game* --cov-report=term`
   - 테스트 환경 문제 확인 및 해결
   - 코드 베이스 파악 및 부족한 부분 식별

2. **테스트 환경 설정 수정** (15분)
   - TestClient 초기화 문제 해결
   - conftest.py 설정 확인 및 수정
   - 테스트 헬퍼 함수 구현 (토큰 생성 등)
   ```python
   # conftest.py 수정 예시
   import pytest
   from fastapi.testclient import TestClient
   from app.main import app

   @pytest.fixture
   def client():
       return TestClient(app)
   
   @pytest.fixture
   def auth_headers():
       # 테스트용 토큰 생성
       token = "test-token"
       return {"Authorization": f"Bearer {token}"}
   ```

3. **DB 세션 의존성 설정** (10분)
   - 게임 라우터에 DB 세션 의존성 추가
   - 필요한 요청 모델 작성 또는 확인
   ```python
   # 라우터 DB 세션 의존성 예제
   from ..database import get_db
   
   @router.post("/slot/spin")
   async def spin_slot(
       current_user: User = Depends(get_current_user),
       game_service: GameService = Depends(get_game_service),
       db: Session = Depends(get_db)
   ) -> dict:
       # 구현 필요
   ```

4. **슬롯 API 우선 구현** (30분)
   - 슬롯 서비스 테스트 파일 작성
   - 라우터-서비스 연결 구현
   - 기본 테스트 케이스 추가

5. **룰렛 & 가챠 API 구현** (40분)
   - 동일한 패턴으로 순차 구현
   - 각각의 비즈니스 로직에 맞는 구현
   - 라우터-서비스 연결 및 에러 처리

6. **테스트 강화** (40분)
   - 각 서비스별 테스트 파일 작성
   - 다양한 시나리오 및 경계값 테스트
   - 커버리지 50% 달성까지 보완

7. **통합 검증 및 문제 해결** (25분)
   - 엔드-투-엔드 통합 테스트 추가
   - 테스트 실행 시 발생하는 오류 해결
   - 전체 테스트 스위트 실행 
   - API 수동 테스트 및 최종 확인

**예상 총 소요 시간: 약 2시간 50분**

---

이 프롬프트를 외부 AI에게 전달하면, 게임 API DB 연동 완성과 테스트 커버리지 향상 작업을 체계적으로 수행할 수 있습니다.

---

## 📚 **추가 컨텍스트 및 참고 자료**

### **프로젝트 아키텍처 문서**
- `docs/01_architecture_en.md` - 전체 시스템 구조 및 F2P 게임 메커니즘
- `docs/CC_backend_refactor_guideline_ko.md` - 백엔드 리팩토링 가이드라인  
- `docs/17_game.md` - 게임 서비스 계층 구조 및 핵심 모듈 설계

### **기술 구현 참고**
- `docs/07-api-endpoints.md` - API 엔드포인트 명세
- `docs/security_authentication_en.md` - 인증 및 보안 구현 가이드
- `docs/09-testing-guide.md` - 현재 테스트 상태 및 가이드 (99 tests, 100% pass)

### **현재 서비스 구현 상태**

**게임 서비스 클래스 구조:**
```
GameService
├── 의존성: GameRepository, SlotService, RouletteService, GachaService
├── 메서드: slot_spin(), roulette_spin(), gacha_pull()
└── 역할: 각 게임별 서비스로 요청 위임

SlotService / RouletteService / GachaService
├── 의존성: GameRepository, TokenService
├── 핵심 메서드: spin()/pull()
└── 역할: 게임 로직 처리, 확률 계산, 보상 지급
```

**핵심 종속성:**
- `TokenService`: 토큰(게임 화폐) 관리
- `GameRepository`: 게임 데이터 DB 액세스
- `UserSegmentService`: 사용자 세그먼트 정보로 확률 조정

### **테스트 환경 해결 가이드**
테스트 실행 시 오류가 발생하면 다음 단계를 시도하세요:

1. **FastAPI 및 관련 패키지 버전 확인/업데이트**
   ```bash
   pip install --upgrade fastapi pytest httpx
   ```

2. **테스트 의존성 명시적 설치**
   ```bash
   pip install pytest-asyncio pytest-cov
   ```

3. **conftest.py 설정 업데이트**
   ```python
   # cc-webapp/backend/tests/conftest.py
   import pytest
   from fastapi.testclient import TestClient
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker, Session
   
   from app.main import app
   from app.database import get_db, Base
   
   # 테스트용 인메모리 SQLite DB 설정
   TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
   engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)
   TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
   
   @pytest.fixture
   def db():
       """테스트용 DB 세션 제공"""
       Base.metadata.create_all(bind=engine)
       db = TestingSessionLocal()
       try:
           yield db
       finally:
           db.close()
   
   @pytest.fixture
   def client():
       """테스트 클라이언트 제공"""
       return TestClient(app)
   ```

4. **TestClient 초기화 방식 확인**
   ```python
   # 변경 전
   from fastapi.testclient import TestClient
   client = TestClient(app=app)  # 오류 발생
   
   # 변경 후
   client = TestClient(app)  # 올바른 방식
   ```

### **개발 체크리스트**  
- `docs/12_game_dev_full_checklist_ko.md` - 전체 개발 진행 현황 (백엔드 98% 완료)
- `docs/PROJECT_PROGRESS_CHECKLIST.md` - 프로젝트 전체 진행 상황

### **중요 제약사항**
- **윈도우 환경**: PowerShell 명령어 사용 시 `;` (세미콜론) 사용
- **Clean Architecture**: Router → Service → Repository → DB 계층 준수
- **TDD 원칙**: 테스트 코드와 함께 구현, Mock 최소화
- **보안 요구사항**: JWT 인증, 서버사이드 검증, Rate limiting 필수
- **에러 처리**: 모든 예외 상황에 대한 적절한 응답 코드와 메시지 제공

### **테스트 작성 가이드**
- 단위 테스트: `pytest` 사용, `pytest-mock`으로 의존성 Mock
- 통합 테스트: 실제 DB 사용, `@pytest.mark.asyncio` 사용
- 테스트 데이터: `conftest.py`에 fixture 정의
- 확률 검증: 반복 실행 통계로 검증 (100회 이상 실행)

### **환경 설정 파일**
- `cc-webapp/backend/requirements.txt` - Python 의존성
- `cc-webapp/backend/pytest.ini` - 테스트 설정
- `cc-webapp/backend/alembic.ini` - DB 마이그레이션 설정

---

**이 프롬프트로 외부 AI가 수행해야 할 핵심 작업:**
1. **게임 API 3개 엔드포인트 실제 구현** (슬롯/룰렛/가챠)
2. **게임 서비스 테스트 커버리지 50% 이상 달성**
3. **모든 테스트 통과 상태 유지** (99+ tests)
4. **DB 연동 안전성 및 성능 보장**
5. **테스트 환경 구성 문제 해결 및 안정화** (`Client.__init__()` 오류 수정)

완료 후 아래 명령어로 검증 및 기록:
```bash
# 전체 테스트 실행
python -m pytest -v

# 커버리지 확인
python -m pytest --cov=app --cov-report=term

# 특정 게임 서비스만 커버리지 확인
python -m pytest --cov=app.services.game_service --cov=app.services.slot_service --cov=app.services.roulette_service --cov=app.services.gacha_service --cov-report=term-missing
```