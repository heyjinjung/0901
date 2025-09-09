"""
Comprehensive test suite for PersonalizationService.

Following docs/09-testing-guide.md standards for:
- Async service testing with proper mocking
- Exception handling coverage
- Integration testing patterns
- Performance and boundary testing
"""

import json
import pytest
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session

from app.services.personalization_service import PersonalizationService
from app.repositories.game_repository import GameRepository


class TestPersonalizationService:
    """PersonalizationService 단위 테스트"""
    
    def setup_method(self):
        """각 테스트 전 실행되는 설정"""
        self.mock_db = Mock(spec=Session)
        self.mock_repository = Mock(spec=GameRepository)
        
        self.service = PersonalizationService(
            db=self.mock_db,
            repository=self.mock_repository
        )

    def test_service_initialization(self):
        """서비스 초기화 테스트"""
        assert self.service.db == self.mock_db
        assert self.service.repository == self.mock_repository

    @pytest.mark.asyncio
    async def test_cache_recommendations_success(self):
        """추천 캐싱 성공 테스트"""
        user_id = 1
        recommendations = [
            {"type": "game", "id": "roulette", "score": 0.8},
            {"type": "content", "id": "adult_content", "score": 0.6}
        ]
        
        # set_gacha_history 호출 성공
        self.mock_repository.set_gacha_history.return_value = None
        
        # 예외 없이 실행되어야 함
        await self.service.cache_recommendations(user_id, recommendations)
        
        # 올바른 인수로 호출 확인
        expected_data = [json.dumps(rec) for rec in recommendations]
        self.mock_repository.set_gacha_history.assert_called_once_with(user_id, expected_data)

    @pytest.mark.asyncio
    async def test_cache_recommendations_exception_handling(self):
        """추천 캐싱 예외 처리 테스트"""
        user_id = 1
        recommendations = [{"type": "game", "id": "roulette"}]
        
        # repository에서 예외 발생하도록 설정
        self.mock_repository.set_gacha_history.side_effect = Exception("Database error")
        
        with patch('app.services.personalization_service.logger') as mock_logger:
            await self.service.cache_recommendations(user_id, recommendations)
            
            # 로그 에러 기록 확인
            mock_logger.error.assert_called_once()
            assert "Failed to cache recommendations for user 1" in mock_logger.error.call_args[0][0]

    @pytest.mark.asyncio
    async def test_get_recommendations_success_with_cached_data(self):
        """캐시된 추천 조회 성공 테스트"""
        user_id = 1
        cached_recs = [
            '{"type": "game", "id": "roulette", "score": 0.8}',
            '{"type": "content", "id": "adult_content", "score": 0.6}'
        ]
        
        self.mock_repository.get_gacha_history.return_value = cached_recs
        
        result = await self.service.get_recommendations(user_id)
        
        expected = [
            {"type": "game", "id": "roulette", "score": 0.8},
            {"type": "content", "id": "adult_content", "score": 0.6}
        ]
        assert result == expected
        self.mock_repository.get_gacha_history.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_recommendations_no_cached_data(self):
        """캐시된 추천이 없을 때 테스트"""
        user_id = 1
        
        self.mock_repository.get_gacha_history.return_value = []
        
        result = await self.service.get_recommendations(user_id)
        
        assert result == []
        self.mock_repository.get_gacha_history.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_recommendations_none_cached_data(self):
        """캐시된 데이터가 None일 때 테스트"""
        user_id = 1
        
        self.mock_repository.get_gacha_history.return_value = None
        
        result = await self.service.get_recommendations(user_id)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_get_recommendations_invalid_json(self):
        """잘못된 JSON 데이터 처리 테스트"""
        user_id = 1
        
        # 잘못된 JSON 문자열 설정
        self.mock_repository.get_gacha_history.return_value = ['invalid_json', 'not_json_either']
        
        with patch('app.services.personalization_service.logger') as mock_logger:
            result = await self.service.get_recommendations(user_id)
            
            assert result == []
            mock_logger.error.assert_called_once()
            assert "Failed to retrieve recommendations for user 1" in mock_logger.error.call_args[0][0]

    @pytest.mark.asyncio
    async def test_get_recommendations_repository_exception(self):
        """repository 예외 처리 테스트"""
        user_id = 1
        
        self.mock_repository.get_gacha_history.side_effect = Exception("Database connection failed")
        
        with patch('app.services.personalization_service.logger') as mock_logger:
            result = await self.service.get_recommendations(user_id)
            
            assert result == []
            mock_logger.error.assert_called_once()
            assert "Failed to retrieve recommendations for user 1" in mock_logger.error.call_args[0][0]

    @pytest.mark.asyncio
    async def test_generate_recommendations_success(self):
        """추천 생성 성공 테스트"""
        user_id = 1
        
        # cache_recommendations 모킹
        with patch.object(self.service, 'cache_recommendations', new_callable=AsyncMock) as mock_cache:
            result = await self.service.generate_recommendations(user_id)
            
            # 기본 추천 구조 확인
            assert len(result) == 2
            assert result[0]["type"] == "game"
            assert result[0]["id"] == "roulette"
            assert result[0]["score"] == 0.8
            assert result[0]["reason"] == "High engagement history"
            
            assert result[1]["type"] == "content"
            assert result[1]["id"] == "adult_content"
            assert result[1]["score"] == 0.6
            assert result[1]["reason"] == "Potential interest based on past interactions"
            
            # 캐싱 호출 확인
            mock_cache.assert_called_once_with(user_id, result)

    @pytest.mark.asyncio
    async def test_generate_recommendations_caching_exception(self):
        """추천 생성 중 캐싱 예외 테스트"""
        user_id = 1
        
        # cache_recommendations에서 예외 발생하도록 설정
        with patch.object(self.service, 'cache_recommendations', new_callable=AsyncMock) as mock_cache:
            mock_cache.side_effect = Exception("Caching failed")
            
            with patch('app.services.personalization_service.logger') as mock_logger:
                result = await self.service.generate_recommendations(user_id)
                
                # 예외 발생 시 빈 리스트 반환
                assert result == []
                mock_logger.error.assert_called_once()
                assert "Recommendation generation failed for user 1" in mock_logger.error.call_args[0][0]

    @pytest.mark.asyncio
    async def test_generate_recommendations_general_exception(self):
        """추천 생성 중 일반 예외 테스트"""
        user_id = 1
        
        # cache_recommendations에서 예외 발생하도록 패치
        with patch.object(self.service, 'cache_recommendations', side_effect=Exception("Cache failed")):
            with patch('app.services.personalization_service.logger') as mock_logger:
                result = await self.service.generate_recommendations(user_id)
                
                # 예외 발생 시 빈 리스트 반환
                assert result == []
                mock_logger.error.assert_called_once()
                assert "Recommendation generation failed for user 1" in mock_logger.error.call_args[0][0]

    @pytest.mark.asyncio
    async def test_generate_recommendations_boundary_values(self):
        """추천 생성 경계값 테스트"""
        # 최소 사용자 ID
        user_id_min = 1
        
        with patch.object(self.service, 'cache_recommendations', new_callable=AsyncMock):
            result = await self.service.generate_recommendations(user_id_min)
            assert len(result) == 2
            assert all("type" in rec and "id" in rec and "score" in rec for rec in result)
        
        # 높은 사용자 ID
        user_id_max = 999999
        
        with patch.object(self.service, 'cache_recommendations', new_callable=AsyncMock):
            result = await self.service.generate_recommendations(user_id_max)
            assert len(result) == 2
            assert result[0]["score"] == 0.8
            assert result[1]["score"] == 0.6


class TestPersonalizationServiceIntegration:
    """PersonalizationService 통합 테스트"""
    
    def setup_method(self):
        """각 테스트 전 실행되는 설정"""
        self.mock_db = Mock(spec=Session)
        self.mock_repository = Mock(spec=GameRepository)
        
        self.service = PersonalizationService(
            db=self.mock_db,
            repository=self.mock_repository
        )

    @pytest.mark.asyncio
    async def test_complete_recommendation_workflow(self):
        """완전한 추천 워크플로우 테스트"""
        user_id = 1
        
        # 1. 초기 상태 - 캐시된 추천 없음
        self.mock_repository.get_gacha_history.return_value = []
        
        initial_recs = await self.service.get_recommendations(user_id)
        assert initial_recs == []
        
        # 2. 추천 생성 및 캐싱
        with patch.object(self.service, 'cache_recommendations', new_callable=AsyncMock):
            with patch('asyncio.run'):  # asyncio.run 패치로 이벤트 루프 문제 방지
                generated_recs = await self.service.generate_recommendations(user_id)
                
                expected_recs = [
                    {"type": "game", "id": "roulette", "score": 0.8, "reason": "High engagement history"},
                    {"type": "content", "id": "adult_content", "score": 0.6, "reason": "Potential interest based on past interactions"}
                ]
                assert generated_recs == expected_recs
        
        # 3. 캐시된 추천 조회
        self.mock_repository.get_gacha_history.return_value = [json.dumps(rec) for rec in expected_recs]
        
        cached_recs = await self.service.get_recommendations(user_id)
        assert cached_recs == expected_recs

    @pytest.mark.asyncio
    async def test_multiple_users_recommendation_management(self):
        """여러 사용자의 추천 관리 테스트"""
        users = [1, 2, 3]
        
        for user_id in users:
            # 각 사용자별로 추천 생성
            with patch.object(self.service, 'cache_recommendations', new_callable=AsyncMock):
                recommendations = await self.service.generate_recommendations(user_id)
                assert len(recommendations) == 2
                assert all("type" in rec for rec in recommendations)
        
        # 각 사용자별 캐시된 추천 확인
        for user_id in users:
            self.mock_repository.get_gacha_history.return_value = [
                '{"type": "game", "id": "roulette", "score": 0.8}',
                '{"type": "content", "id": "adult_content", "score": 0.6}'
            ]
            
            cached_recs = await self.service.get_recommendations(user_id)
            assert len(cached_recs) == 2

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self):
        """오류 복구 워크플로우 테스트"""
        user_id = 1
        
        # 1. 캐시 조회 실패
        self.mock_repository.get_gacha_history.side_effect = Exception("Cache read failed")
        
        with patch('app.services.personalization_service.logger'):
            cached_recs = await self.service.get_recommendations(user_id)
            assert cached_recs == []
        
        # 2. 추천 생성으로 복구
        self.mock_repository.get_gacha_history.side_effect = None  # 예외 제거
        
        with patch.object(self.service, 'cache_recommendations', new_callable=AsyncMock):
            new_recs = await self.service.generate_recommendations(user_id)
            assert len(new_recs) == 2

    @pytest.mark.asyncio
    async def test_performance_with_large_recommendation_data(self):
        """대량 추천 데이터 성능 테스트"""
        user_id = 1
        
        # 대량 캐시된 추천 시뮬레이션 (100개)
        large_cached_data = [
            json.dumps({"type": "game", "id": f"game_{i}", "score": 0.5 + (i % 5) * 0.1})
            for i in range(100)
        ]
        
        self.mock_repository.get_gacha_history.return_value = large_cached_data
        
        # 성능 측정
        import time
        start_time = time.time()
        
        result = await self.service.get_recommendations(user_id)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 결과 검증
        assert len(result) == 100
        assert all("type" in rec for rec in result)
        
        # 성능 검증 (1초 이내)
        assert execution_time < 1.0, f"Performance test failed: {execution_time:.3f}s > 1.0s"

    @pytest.mark.asyncio
    async def test_empty_recommendation_handling(self):
        """빈 추천 데이터 처리 테스트"""
        user_id = 1
        
        # 빈 추천 캐싱 테스트
        await self.service.cache_recommendations(user_id, [])
        self.mock_repository.set_gacha_history.assert_called_with(user_id, [])
        
        # 빈 캐시 조회 테스트
        self.mock_repository.get_gacha_history.return_value = []
        result = await self.service.get_recommendations(user_id)
        assert result == []

    @pytest.mark.asyncio
    async def test_recommendation_data_types(self):
        """추천 데이터 타입 검증 테스트"""
        user_id = 1
        
        with patch.object(self.service, 'cache_recommendations', new_callable=AsyncMock):
            recommendations = await self.service.generate_recommendations(user_id)
            
            # 데이터 타입 검증
            for rec in recommendations:
                assert isinstance(rec, dict)
                assert isinstance(rec["type"], str)
                assert isinstance(rec["id"], str)
                assert isinstance(rec["score"], float)
                assert isinstance(rec["reason"], str)
                
                # 스코어 범위 검증 (0.0 ~ 1.0)
                assert 0.0 <= rec["score"] <= 1.0
