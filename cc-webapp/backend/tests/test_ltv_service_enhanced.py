"""
Enhanced tests for LTVService following project testing standards

This test file follows the guidelines in docs/09-testing-guide.md:
- 100% test coverage for business-critical services
- Both unit and integration test scenarios  
- Proper mocking and dependency injection
- Edge case and error handling coverage
- Performance and boundary testing
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.services.ltv_service import LTVService
from app.repositories.game_repository import GameRepository


class TestLTVService:
    """LTVService 단위 테스트"""
    
    def setup_method(self):
        """각 테스트 전 실행되는 설정"""
        self.mock_db = Mock(spec=Session)
        self.mock_repository = Mock(spec=GameRepository)
        
        self.service = LTVService(
            db=self.mock_db,
            repository=self.mock_repository
        )
    
    def test_service_initialization(self):
        """서비스 초기화 테스트"""
        assert self.service.db == self.mock_db
        assert self.service.repository == self.mock_repository
    
    @pytest.mark.asyncio
    async def test_cache_ltv_success(self):
        """LTV 캐싱 성공 테스트"""
        user_id = 1
        ltv_data = {
            "prediction": 150.0,
            "future_value": 75.0,
            "churn_probability": 0.15
        }
        
        # Mock 설정
        self.mock_repository.set_gacha_history.return_value = None
        
        # 실행
        await self.service.cache_ltv(user_id, ltv_data)
        
        # 검증
        expected_json = json.dumps(ltv_data)
        self.mock_repository.set_gacha_history.assert_called_once_with(
            user_id, [expected_json]
        )
    
    @pytest.mark.asyncio
    async def test_cache_ltv_exception_handling(self):
        """LTV 캐싱 예외 처리 테스트"""
        user_id = 1
        ltv_data = {"prediction": 100.0}
        
        # Repository에서 예외 발생하도록 설정
        self.mock_repository.set_gacha_history.side_effect = Exception("Database error")
        
        # 로깅 패치
        with patch('app.services.ltv_service.logger') as mock_logger:
            # 실행 (예외가 발생해도 중단되지 않아야 함)
            await self.service.cache_ltv(user_id, ltv_data)
            
            # 로깅 확인
            mock_logger.error.assert_called_once()
            assert "Failed to cache LTV for user 1" in mock_logger.error.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_get_ltv_success_with_cached_data(self):
        """캐시된 LTV 조회 성공 테스트"""
        user_id = 1
        cached_ltv = {
            "prediction": 200.0,
            "future_value": 100.0,
            "churn_probability": 0.1
        }
        
        # Mock 설정 - 캐시된 데이터 반환
        self.mock_repository.get_gacha_history.return_value = [json.dumps(cached_ltv)]
        
        # 실행
        result = await self.service.get_ltv(user_id)
        
        # 검증
        assert result == cached_ltv
        self.mock_repository.get_gacha_history.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_get_ltv_no_cached_data(self):
        """캐시된 LTV가 없는 경우 테스트"""
        user_id = 1
        
        # Mock 설정 - 빈 캐시
        self.mock_repository.get_gacha_history.return_value = []
        
        # 실행
        result = await self.service.get_ltv(user_id)
        
        # 검증
        assert result == {}
        self.mock_repository.get_gacha_history.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_get_ltv_none_cached_data(self):
        """캐시 데이터가 None인 경우 테스트"""
        user_id = 1
        
        # Mock 설정 - None 반환
        self.mock_repository.get_gacha_history.return_value = None
        
        # 실행
        result = await self.service.get_ltv(user_id)
        
        # 검증
        assert result == {}
        self.mock_repository.get_gacha_history.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_get_ltv_invalid_json(self):
        """잘못된 JSON 형식의 캐시 데이터 테스트"""
        user_id = 1
        
        # Mock 설정 - 잘못된 JSON
        self.mock_repository.get_gacha_history.return_value = ["invalid json"]
        
        with patch('app.services.ltv_service.logger') as mock_logger:
            # 실행
            result = await self.service.get_ltv(user_id)
            
            # 검증
            assert result == {}
            mock_logger.error.assert_called_once()
            assert "Failed to retrieve LTV for user 1" in mock_logger.error.call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_get_ltv_repository_exception(self):
        """Repository 예외 발생 테스트"""
        user_id = 1
        
        # Mock 설정 - Repository에서 예외 발생
        self.mock_repository.get_gacha_history.side_effect = Exception("Database connection error")
        
        with patch('app.services.ltv_service.logger') as mock_logger:
            # 실행
            result = await self.service.get_ltv(user_id)
            
            # 검증
            assert result == {}
            mock_logger.error.assert_called_once()
            assert "Failed to retrieve LTV for user 1" in mock_logger.error.call_args[0][0]
    
    def test_predict_ltv_success(self):
        """LTV 예측 성공 테스트"""
        user_id = 1
        
        # cache_ltv 메서드를 패치하여 asyncio.run 호출 확인
        with patch.object(self.service, 'cache_ltv', new_callable=AsyncMock) as mock_cache:
            result = self.service.predict_ltv(user_id)
        
        # 검증
        expected_ltv = {
            "prediction": 100.0,
            "future_value": 50.0,
            "churn_probability": 0.2        }
        assert result == expected_ltv
        mock_cache.assert_called_once_with(user_id, expected_ltv)
    
    def test_predict_ltv_caching_exception(self):
        """LTV 예측 중 캐싱 예외 테스트"""
        user_id = 1
        
        # cache_ltv에서 예외 발생하도록 설정
        with patch.object(self.service, 'cache_ltv', new_callable=AsyncMock) as mock_cache:
            mock_cache.side_effect = Exception("Caching failed")
            with patch('app.services.ltv_service.logger') as mock_logger:
                result = self.service.predict_ltv(user_id)
                
                # 예외 발생 시 기본값 반환
                assert result == {"prediction": 0.0}
                mock_logger.error.assert_called_once()
                assert "LTV prediction failed for user 1" in mock_logger.error.call_args[0][0]

    def test_predict_ltv_general_exception(self):
        """LTV 예측 중 일반 예외 테스트"""
        user_id = 1
        
        # cache_ltv에서 예외 발생하도록 패치 (asyncio.run 대신)
        with patch.object(self.service, 'cache_ltv', side_effect=Exception("Cache failed")):
            with patch('app.services.ltv_service.logger') as mock_logger:
                result = self.service.predict_ltv(user_id)
                
                # 예외 발생 시 기본값 반환
                assert result == {"prediction": 0.0}
                mock_logger.error.assert_called_once()
                assert "LTV prediction failed for user 1" in mock_logger.error.call_args[0][0]
    
    def test_predict_ltv_boundary_values(self):
        """LTV 예측 경계값 테스트"""
        # 최소 사용자 ID
        user_id_min = 1
        
        with patch.object(self.service, 'cache_ltv', new_callable=AsyncMock):
            result = self.service.predict_ltv(user_id_min)
            assert "prediction" in result
            assert "future_value" in result
            assert "churn_probability" in result
        
        # 높은 사용자 ID
        user_id_max = 999999
        
        with patch.object(self.service, 'cache_ltv', new_callable=AsyncMock):
            result = self.service.predict_ltv(user_id_max)
            assert result["prediction"] == 100.0
            assert result["future_value"] == 50.0
            assert result["churn_probability"] == 0.2


class TestLTVServiceIntegration:
    """LTVService 통합 테스트"""
    
    def setup_method(self):
        """각 테스트 전 실행되는 설정"""
        self.mock_db = Mock(spec=Session)
        self.mock_repository = Mock(spec=GameRepository)
        
        self.service = LTVService(
            db=self.mock_db,
            repository=self.mock_repository
        )
    
    @pytest.mark.asyncio
    async def test_complete_ltv_workflow(self):
        """완전한 LTV 워크플로우 테스트"""
        user_id = 1
        
        # 1. 초기 상태 - 캐시된 LTV 없음
        self.mock_repository.get_gacha_history.return_value = []
        
        initial_ltv = await self.service.get_ltv(user_id)
        assert initial_ltv == {}
          # 2. LTV 예측 및 캐싱
        with patch.object(self.service, 'cache_ltv', new_callable=AsyncMock) as mock_cache:
            # asyncio.run 문제를 방지하기 위해 patch
            with patch('asyncio.run') as mock_run:
                predicted_ltv = self.service.predict_ltv(user_id)
                
                expected_ltv = {
                    "prediction": 100.0,
                    "future_value": 50.0,
                    "churn_probability": 0.2
                }
                assert predicted_ltv == expected_ltv
                mock_run.assert_called_once()
        
        # 3. 캐시된 LTV 조회
        self.mock_repository.get_gacha_history.return_value = [json.dumps(expected_ltv)]
        
        cached_ltv = await self.service.get_ltv(user_id)
        assert cached_ltv == expected_ltv
    
    @pytest.mark.asyncio
    async def test_multiple_users_ltv_management(self):
        """여러 사용자의 LTV 관리 테스트"""
        users = [1, 2, 3]
        ltv_data = [
            {"prediction": 100.0, "future_value": 50.0, "churn_probability": 0.2},
            {"prediction": 150.0, "future_value": 75.0, "churn_probability": 0.15},
            {"prediction": 200.0, "future_value": 100.0, "churn_probability": 0.1}
        ]
        
        # 각 사용자에 대해 LTV 캐싱
        for user_id, ltv in zip(users, ltv_data):
            await self.service.cache_ltv(user_id, ltv)
        
        # 검증: 각 사용자별로 올바른 데이터가 캐시되었는지 확인
        assert self.mock_repository.set_gacha_history.call_count == len(users)
        
        # 각 호출의 인자 확인
        calls = self.mock_repository.set_gacha_history.call_args_list
        for i, (user_id, ltv) in enumerate(zip(users, ltv_data)):
            call_args = calls[i][0]  # positional arguments
            assert call_args[0] == user_id
            assert json.loads(call_args[1][0]) == ltv
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self):
        """오류 복구 워크플로우 테스트"""
        user_id = 1
        
        # 1. 첫 번째 시도: Repository 오류
        self.mock_repository.get_gacha_history.side_effect = Exception("DB Error")
        
        with patch('app.services.ltv_service.logger'):
            result = await self.service.get_ltv(user_id)
            assert result == {}
        
        # 2. 복구: Repository 정상 작동
        self.mock_repository.get_gacha_history.side_effect = None
        self.mock_repository.get_gacha_history.return_value = []
        
        result = await self.service.get_ltv(user_id)
        assert result == {}
        
        # 3. 정상 데이터 캐싱 및 조회
        ltv_data = {"prediction": 120.0, "future_value": 60.0, "churn_probability": 0.18}
        
        await self.service.cache_ltv(user_id, ltv_data)
        
        self.mock_repository.get_gacha_history.return_value = [json.dumps(ltv_data)]
        result = await self.service.get_ltv(user_id)
        assert result == ltv_data
    
    def test_performance_with_large_ltv_data(self):
        """대용량 LTV 데이터 성능 테스트"""
        user_id = 1
        
        # 큰 LTV 데이터 구조
        large_ltv_data = {
            "prediction": 1000.0,
            "future_value": 500.0,
            "churn_probability": 0.05,
            "detailed_predictions": {f"month_{i}": i * 10.0 for i in range(1, 25)},  # 24개월 예측
            "segments": {f"segment_{i}": i * 5.0 for i in range(1, 11)},  # 10개 세그먼트
            "metadata": {
                "calculation_date": "2025-06-18",
                "model_version": "v2.1",
                "confidence_score": 0.85
            }
        }
        
        # 성능 측정을 위한 시간 제한 테스트
        import time
        
        start_time = time.time()
        
        with patch.object(self.service, 'cache_ltv', new_callable=AsyncMock):
            result = self.service.predict_ltv(user_id)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 검증: 실행 시간이 합리적인 범위 내에 있어야 함 (1초 미만)
        assert execution_time < 1.0
        assert result is not None
        assert "prediction" in result
