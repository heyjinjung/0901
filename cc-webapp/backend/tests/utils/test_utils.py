"""
테스트 유틸리티 클래스 - MCP 최적화
중복된 테스트 로직을 통합하여 재사용 가능한 유틸리티 제공
"""

import time
from typing import Dict, Any, List, Optional
from unittest.mock import Mock


class EmotionTestUtils:
    """감정 분석 테스트 유틸리티"""
    
    @staticmethod
    def validate_emotion_result(result):
        """감정 분석 결과 검증"""
        assert hasattr(result, 'emotion')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'language')
        assert 0.0 <= result.confidence <= 1.0
        assert result.emotion in [
            "happy", "sad", "angry", "excited", "neutral", 
            "disappointed", "frustrated", "ecstatic", "uncertain"
        ]
        assert result.language in ["english", "korean", "mixed", "unknown"]
    
    @staticmethod
    def create_mock_emotion_result(emotion="neutral", confidence=0.7, language="english"):
        """Mock 감정 결과 생성"""
        return Mock(
            emotion=emotion,
            confidence=confidence,
            language=language
        )
    
    @staticmethod
    def simulate_emotion_sequence(emotions: List[str]):
        """감정 시퀀스 시뮬레이션"""
        results = []
        for emotion in emotions:
            result = EmotionTestUtils.create_mock_emotion_result(
                emotion=emotion,
                confidence=0.8,
                language="english"
            )
            results.append(result)
        return results


class GachaTestUtils:
    """가차 서비스 테스트 유틸리티"""
    
    @staticmethod
    def validate_gacha_result(result):
        """가차 결과 검증"""
        assert "item_id" in result
        assert "rarity" in result
        assert "user_id" in result
        assert result["rarity"] in ["common", "rare", "epic", "legendary"]
        assert isinstance(result["user_id"], int)
    
    @staticmethod
    def create_mock_gacha_item(item_id="test_item", rarity="common", user_id=1):
        """Mock 가차 아이템 생성"""
        return {
            "item_id": item_id,
            "item_name": f"{rarity.title()} Item",
            "rarity": rarity,
            "user_id": user_id,
            "quantity": 1,
            "obtained_at": "2024-01-01T00:00:00Z"
        }
    
    @staticmethod
    def simulate_rarity_distribution(pulls=100):
        """희귀도 분포 시뮬레이션"""
        distribution = {"common": 0, "rare": 0, "epic": 0, "legendary": 0}
        
        for i in range(pulls):
            if i < pulls * 0.7:  # 70% common
                rarity = "common"
            elif i < pulls * 0.9:  # 20% rare
                rarity = "rare"
            elif i < pulls * 0.98:  # 8% epic
                rarity = "epic"
            else:  # 2% legendary
                rarity = "legendary"
            
            distribution[rarity] += 1
        
        return distribution
    
    @staticmethod
    def validate_rarity_distribution(distribution: Dict[str, int], total_pulls: int):
        """희귀도 분포 검증"""
        # 기본 확률 검증
        common_ratio = distribution["common"] / total_pulls
        rare_ratio = distribution["rare"] / total_pulls
        legendary_ratio = distribution["legendary"] / total_pulls
        
        assert 0.6 <= common_ratio <= 0.8  # 60-80% common
        assert 0.1 <= rare_ratio <= 0.3    # 10-30% rare
        assert legendary_ratio <= 0.1      # <= 10% legendary


class ServiceTestUtils:
    """서비스 레이어 테스트 유틸리티"""
    
    @staticmethod
    def create_mock_user(user_id=1, nickname="testuser"):
        """Mock 사용자 생성"""
        return {
            "user_id": user_id,
            "nickname": nickname,
            "email": f"{nickname}@test.com",
            "gems": 1000,
            "coins": 5000,
            "level": 1,
            "exp": 0
        }
    
    @staticmethod
    def create_mock_service_response(success=True, data=None, error=None):
        """Mock 서비스 응답 생성"""
        response = {
            "success": success,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        if success:
            response["data"] = data or {}
        else:
            response["error"] = error or "Unknown error"
        
        return response
    
    @staticmethod
    def validate_service_response(response):
        """서비스 응답 검증"""
        assert "success" in response
        assert "timestamp" in response
        assert isinstance(response["success"], bool)
        
        if response["success"]:
            assert "data" in response
        else:
            assert "error" in response


class APITestUtils:
    """API 테스트 유틸리티"""
    
    @staticmethod
    def create_mock_client():
        """Mock TestClient 생성"""
        return Mock()
    
    @staticmethod
    def mock_post_request(endpoint: str, payload: Dict, expected_response: Dict, status_code=200):
        """Mock POST 요청 시뮬레이션"""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        return mock_response
    
    @staticmethod
    def mock_get_request(endpoint: str, expected_response: Dict, status_code=200):
        """Mock GET 요청 시뮬레이션"""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        return mock_response
    
    @staticmethod
    def validate_api_response(response, expected_status=200):
        """API 응답 검증"""
        assert response.status_code == expected_status
        
        if expected_status == 200:
            data = response.json()
            assert isinstance(data, dict)
        elif expected_status >= 400:
            error_data = response.json()
            assert "error" in error_data or "detail" in error_data


class PerformanceTestUtils:
    """성능 테스트 유틸리티"""
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """실행 시간 측정"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        return result, execution_time
    
    @staticmethod
    def validate_performance(execution_time: float, max_time: float):
        """성능 검증"""
        assert execution_time <= max_time, f"Execution time {execution_time:.3f}s exceeds limit {max_time}s"
    
    @staticmethod
    def simulate_concurrent_execution(func, args_list: List, max_workers=5):
        """동시 실행 시뮬레이션"""
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(func, *args) for args in args_list]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        return results


class DatabaseTestUtils:
    """데이터베이스 테스트 유틸리티"""
    
    @staticmethod
    def create_mock_connection():
        """Mock 데이터베이스 연결 생성"""
        return Mock()
    
    @staticmethod
    def mock_query_result(rows: List[Dict]):
        """Mock 쿼리 결과 생성"""
        return rows
    
    @staticmethod
    def validate_database_result(result, expected_count=None):
        """데이터베이스 결과 검증"""
        assert isinstance(result, list)
        
        if expected_count is not None:
            assert len(result) == expected_count
        
        for row in result:
            assert isinstance(row, dict)


class ValidationUtils:
    """검증 유틸리티"""
    
    @staticmethod
    def validate_user_id(user_id):
        """사용자 ID 검증"""
        assert isinstance(user_id, int)
        assert user_id > 0
    
    @staticmethod
    def validate_currency_amount(amount):
        """화폐 금액 검증"""
        assert isinstance(amount, (int, float))
        assert amount >= 0
    
    @staticmethod
    def validate_timestamp(timestamp: str):
        """타임스탬프 검증"""
        import re
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?$'
        assert re.match(pattern, timestamp), f"Invalid timestamp format: {timestamp}"
    
    @staticmethod
    def validate_email(email: str):
        """이메일 검증"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        assert re.match(pattern, email), f"Invalid email format: {email}"


class MockDataGenerator:
    """Mock 데이터 생성기"""
    
    @staticmethod
    def generate_users(count=10):
        """사용자 데이터 생성"""
        users = []
        for i in range(count):
            user = ServiceTestUtils.create_mock_user(
                user_id=i + 1,
                nickname=f"user{i+1:03d}"
            )
            users.append(user)
        return users
    
    @staticmethod
    def generate_gacha_items(count=50):
        """가차 아이템 데이터 생성"""
        items = []
        rarities = ["common", "rare", "epic", "legendary"]
        
        for i in range(count):
            rarity = rarities[i % len(rarities)]
            item = GachaTestUtils.create_mock_gacha_item(
                item_id=f"item_{i+1:03d}",
                rarity=rarity,
                user_id=(i % 10) + 1  # 10명의 사용자에게 분배
            )
            items.append(item)
        
        return items
    
    @staticmethod
    def generate_emotion_data(count=20):
        """감정 데이터 생성"""
        emotions = ["happy", "sad", "angry", "excited", "neutral"]
        languages = ["english", "korean"]
        
        data = []
        for i in range(count):
            emotion = emotions[i % len(emotions)]
            language = languages[i % len(languages)]
            
            result = EmotionTestUtils.create_mock_emotion_result(
                emotion=emotion,
                confidence=0.7 + (i % 3) * 0.1,  # 0.7, 0.8, 0.9 순환
                language=language
            )
            data.append(result)
        
        return data


# 테스트 마크 및 설정
class TestMarkers:
    """테스트 마커 상수"""
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    SLOW = "slow"
    EMOTION = "emotion"
    GACHA = "gacha"
    API = "api"
    DATABASE = "database"


# 공통 테스트 설정
class TestConfig:
    """테스트 설정"""
    DEFAULT_TIMEOUT = 5.0
    PERFORMANCE_TIMEOUT = 1.0
    BATCH_SIZE = 100
    MAX_WORKERS = 5
    
    # 확률 설정
    GACHA_RATES = {
        "common": 0.70,
        "rare": 0.20,
        "epic": 0.08,
        "legendary": 0.02
    }
    
    # 감정 신뢰도 임계값
    EMOTION_CONFIDENCE_THRESHOLD = 0.7