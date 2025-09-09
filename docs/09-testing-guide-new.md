# 백엔드 테스트 가이드 및 커버리지 현황

## 📊 현재 테스트 커버리지 상태 (2025-06-19 기준)

### 🎯 전체 커버리지: **68%** (3162 라인 중 1014 라인 미커버)

### 📈 **우수한 커버리지** (90% 이상)
- `app/models.py`: **100%** ✨
- `app/schemas.py`: **100%** ✨  
- `app/routers/doc_titles.py`: **100%** ✨
- `app/routers/notification.py`: **100%** ✨
- `app/services/age_verification_service.py`: **100%** ✨
- `app/services/ltv_service.py`: **100%** ✨
- `app/services/notification_service.py`: **100%** ✨
- `app/services/personalization_service.py`: **100%** ✨
- `app/services/reward_service.py`: **100%** ✨
- `app/services/rfm_service.py`: **100%** ✨
- `app/services/roulette_service.py`: **100%** ✨
- `app/services/rps_service.py`: **100%** ✨
- `app/services/tracking_service.py`: **100%** ✨
- `app/services/game_service.py`: **96%** 🔥
- `app/services/slot_service.py`: **96%** 🔥
- `app/services/vip_content_service.py`: **95%** 🔥
- `app/services/gacha_service.py`: **91%** 🔥
- `app/services/emotion_feedback_service.py`: **91%** 🔥
- `app/services/user_segment_service.py`: **91%** 🔥

### ⚡ **양호한 커버리지** (70-89%)
- `app/repositories/game_repository.py`: **85%**
- `app/main.py`: **83%**
- `app/routers/user_segments.py`: **83%**
- `app/services/recommendation_service.py`: **82%**
- `app/routers/games.py`: **79%**
- `app/routers/tracking.py`: **78%**
- `app/routers/segments.py`: **78%**
- `app/services/cj_ai_service.py`: **76%**
- `app/services/user_service.py`: **71%**
- `app/services/token_service.py`: **70%**
- `app/routers/gacha.py`: **70%**

### ⚠️ **개선 필요 영역** (50% 미만)
- `app/services/adult_content_service_old.py`: **0%** (사용되지 않는 파일)
- `app/services/flash_offer_service.py`: **0%** ❌
- `app/apscheduler_jobs.py`: **31%** ❌
- `app/routers/unlock.py`: **33%** ❌
- `app/utils/segment_utils.py`: **35%** ❌
- `app/websockets/chat.py`: **36%** ❌
- `app/routers/feedback.py`: **36%** ❌
- `app/routers/recommendation.py`: **38%** ❌
- `app/services/adult_content_service.py`: **42%** ❌
- `app/utils/reward_utils.py`: **42%** ❌
- `app/routers/chat.py`: **43%** ❌
- `app/routers/actions.py`: **49%** ❌
- `app/utils/sentiment_analyzer.py`: **49%** ❌

## 🎯 우선 개선 목표

### 1. **핵심 비즈니스 로직** (우선순위 HIGH)
- `app/services/adult_content_service.py`: 42% → 85%+
- `app/services/flash_offer_service.py`: 0% → 90%+
- `app/utils/reward_utils.py`: 42% → 80%+

### 2. **API 라우터** (우선순위 MEDIUM)
- `app/routers/unlock.py`: 33% → 75%+
- `app/routers/recommendation.py`: 38% → 70%+
- `app/routers/feedback.py`: 36% → 70%+

### 3. **유틸리티 함수** (우선순위 LOW)
- `app/utils/segment_utils.py`: 35% → 60%+
- `app/utils/sentiment_analyzer.py`: 49% → 70%+

## 📋 테스트 실행 가이드

### 기본 테스트 실행
```bash
# 모든 테스트 실행
python -m pytest tests/ -v

# 커버리지와 함께 실행
python -m pytest --cov=app --cov-report=term-missing --cov-report=html tests/ -q

# 특정 파일만 테스트
python -m pytest tests/test_adult_content_router_fixed.py -v

# 실패한 테스트만 다시 실행
python -m pytest --lf -v
```

### 커버리지 리포트 확인
```bash
# HTML 리포트 생성 (htmlcov/index.html)
python -m pytest --cov=app --cov-report=html tests/

# 터미널에서 누락된 라인 확인
python -m pytest --cov=app --cov-report=term-missing tests/
```

## 🏗️ 테스트 작성 가이드

### TDD 접근법
1. **실패하는 테스트 먼저 작성**
2. **최소한의 코드로 테스트 통과**
3. **리팩토링으로 코드 품질 향상**

### 테스트 구조
```python
# 테스트 파일 예시: tests/test_service_name.py
import pytest
from unittest.mock import Mock, patch
from app.services.service_name import ServiceName

class TestServiceName:
    def setup_method(self):
        """각 테스트 메서드 전에 실행"""
        self.service = ServiceName()
    
    def test_method_name_success(self):
        """성공 케이스 테스트"""
        # Given
        # When
        # Then
        assert result == expected
    
    def test_method_name_error_handling(self):
        """에러 처리 테스트"""
        with pytest.raises(ExpectedException):
            # When
            pass
```

### Mock 사용 가이드
```python
# 외부 의존성 모킹
@patch('app.services.external_service')
def test_with_external_dependency(self, mock_service):
    mock_service.return_value = expected_result
    # 테스트 로직
```

## 🚀 최근 개선 사항 (2025-06-19)

### ✅ 해결된 이슈
- **타입 에러 완전 해결**: 모든 백엔드 파일의 타입 에러 0개
- **테스트 안정성**: 365개 테스트 중 365개 통과 (100% 성공률)
- **코드 품질**: Clean Architecture & SOLID 원칙 준수

### 🔧 수정된 파일들
- `app/routers/recommendation.py`: 매개변수 이름 일치, 비동기 호출 수정
- `app/routers/unlock.py`: SQLAlchemy Column 타입 에러 해결
- `app/routers/adult_content.py`: Dict → UnlockHistoryItem 변환 추가
- `app/routers/gacha.py`: Pydantic 자동 타입 변환 구현
- `tests/test_emotion_feedback_service.py`: None 매개변수 수정

## 📝 다음 단계

### 단기 목표 (1주 내)
1. `flash_offer_service.py` 테스트 커버리지 0% → 90%+
2. `adult_content_service.py` 테스트 강화 42% → 70%+
3. `unlock.py` 라우터 테스트 개선 33% → 60%+

### 중기 목표 (1개월 내)
1. 전체 커버리지 68% → 80%+
2. 핵심 서비스 레이어 90%+ 달성
3. 통합 테스트 추가

### 장기 목표
1. 전체 커버리지 85%+ 유지
2. 성능 테스트 추가
3. E2E 테스트 구축
