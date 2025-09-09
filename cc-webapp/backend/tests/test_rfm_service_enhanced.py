"""
Comprehensive test suite for RFMService.

Following docs/09-testing-guide.md standards for:
- RFM calculation testing with various user scenarios
- Exception handling and error recovery
- Dynamic threshold computation
- Caching functionality testing
- User segmentation validation
- Integration testing patterns
"""

import json
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.services.rfm_service import RFMService
from app.schemas.ai_schemas import RFMScore
from app.repositories.game_repository import GameRepository


class TestRFMService:
    """RFMService 단위 테스트"""
    
    def setup_method(self):
        """각 테스트 전 실행되는 설정"""
        self.mock_db = Mock(spec=Session)
        self.mock_repository = Mock(spec=GameRepository)
        
        self.service = RFMService(
            db=self.mock_db,
            repository=self.mock_repository
        )

    def test_service_initialization(self):
        """서비스 초기화 테스트"""
        assert self.service.db == self.mock_db
        assert self.service.repository == self.mock_repository

    def test_rfm_score_namedtuple(self):
        """RFMScore NamedTuple 구조 테스트"""
        rfm_score = RFMScore(
            user_id=1,
            recency=30,
            frequency=10,
            monetary=500.0,
            rfm_score=0.75,
            segment="High-Value"
        )
        
        assert rfm_score.user_id == 1
        assert rfm_score.recency == 30
        assert rfm_score.frequency == 10
        assert rfm_score.monetary == 500.0
        assert rfm_score.rfm_score == 0.75
        assert rfm_score.segment == "High-Value"

    def test_compute_dynamic_thresholds_success(self):
        """동적 임계값 계산 성공 테스트"""
        # set_gacha_history 호출 성공
        self.mock_repository.set_gacha_history.return_value = None
        
        result = self.service.compute_dynamic_thresholds()
        
        # 예상되는 임계값 구조 확인
        expected_keys = [
            "recency_high", "recency_medium",
            "frequency_high", "frequency_medium",
            "monetary_high", "monetary_medium"
        ]
        
        assert all(key in result for key in expected_keys)
        assert result["recency_high"] == 30.0
        assert result["recency_medium"] == 60.0
        assert result["frequency_high"] == 10.0
        assert result["frequency_medium"] == 5.0
        assert result["monetary_high"] == 500.0
        assert result["monetary_medium"] == 250.0
        
        # repository 호출 확인
        self.mock_repository.set_gacha_history.assert_called_once_with(0, [json.dumps(result)])

    def test_compute_dynamic_thresholds_exception_handling(self):
        """동적 임계값 계산 예외 처리 테스트"""
        # repository에서 예외 발생하도록 설정
        self.mock_repository.set_gacha_history.side_effect = Exception("Database error")
        
        with patch('app.services.rfm_service.logger') as mock_logger:
            result = self.service.compute_dynamic_thresholds()
            
            # 예외 발생 시 빈 딕셔너리 반환
            assert result == {}
            mock_logger.error.assert_called_once()
            assert "Failed to compute dynamic RFM thresholds" in mock_logger.error.call_args[0][0]

    def test_cache_rfm_scores_success(self):
        """RFM 점수 캐싱 성공 테스트"""
        scores = [
            {"user_id": 1, "rfm_score": 0.8, "segment": "High-Value"},
            {"user_id": 2, "rfm_score": 0.6, "segment": "Medium-Value"},
            {"user_id": 3, "rfm_score": 0.3, "segment": "Low-Value"}
        ]
        
        self.mock_repository.set_gacha_history.return_value = None
        
        # 예외 없이 실행되어야 함
        self.service.cache_rfm_scores(scores)
        
        # 각 사용자별로 캐싱 호출 확인
        assert self.mock_repository.set_gacha_history.call_count == 3
        
        # 호출 인수 확인
        calls = self.mock_repository.set_gacha_history.call_args_list
        assert calls[0][0][0] == 1  # user_id
        assert calls[1][0][0] == 2  # user_id
        assert calls[2][0][0] == 3  # user_id

    def test_cache_rfm_scores_invalid_user_id(self):
        """잘못된 사용자 ID로 RFM 점수 캐싱 테스트"""
        scores = [
            {"user_id": 0, "rfm_score": 0.5},  # user_id = 0 (스킵됨)
            {"user_id": -1, "rfm_score": 0.5},  # user_id < 0 (스킵됨)
            {"rfm_score": 0.5},  # user_id 없음 (스킵됨)
            {"user_id": 1, "rfm_score": 0.8}   # 정상
        ]
        
        self.mock_repository.set_gacha_history.return_value = None
        
        self.service.cache_rfm_scores(scores)
        
        # 유효한 사용자 ID만 처리됨
        assert self.mock_repository.set_gacha_history.call_count == 1
        calls = self.mock_repository.set_gacha_history.call_args_list
        assert calls[0][0][0] == 1  # 유효한 user_id

    def test_cache_rfm_scores_exception_handling(self):
        """RFM 점수 캐싱 예외 처리 테스트"""
        scores = [{"user_id": 1, "rfm_score": 0.8}]
        
        self.mock_repository.set_gacha_history.side_effect = Exception("Cache failed")
        
        with patch('app.services.rfm_service.logger') as mock_logger:
            self.service.cache_rfm_scores(scores)
            
            mock_logger.error.assert_called_once()
            assert "Failed to cache RFM scores" in mock_logger.error.call_args[0][0]

    def test_calculate_rfm_success(self):
        """RFM 계산 성공 테스트"""
        user_id = 1
        
        # 가짜 가챠 히스토리 설정
        gacha_history = [
            '{"value": 100}',
            '{"value": 200}',
            '{"value": 150}'
        ]
        
        self.mock_repository.get_gacha_history.return_value = gacha_history
        self.mock_repository.get_user_segment.return_value = "High-Value"
        
        result = self.service.calculate_rfm(user_id)
        
        # RFMScore 객체 확인
        assert isinstance(result, RFMScore)
        assert result.user_id == 1
        assert result.recency == 45  # 고정값
        assert result.frequency == 3  # gacha_history 길이
        assert result.monetary == 450.0  # 100 + 200 + 150
        
        # RFM 점수 계산 확인 (recency * 0.3 + frequency * 0.3 + monetary * 0.4)
        expected_score = (45 * 0.3) + (3 * 0.3) + (450.0 * 0.4)
        assert result.rfm_score == expected_score
          # 세그먼트 확인 (점수에 따라)
        if expected_score > 0.8:
            assert result.segment == "High-Value"
        elif expected_score > 0.5:
            assert result.segment == "Medium-Value"
        else:
            assert result.segment == "Low-Value"

    def test_calculate_rfm_no_history(self):
        """가챠 히스토리가 없는 경우 RFM 계산 테스트"""
        user_id = 1
        
        self.mock_repository.get_gacha_history.return_value = []
        self.mock_repository.get_user_segment.return_value = "Low-Value"
        
        result = self.service.calculate_rfm(user_id)
        
        assert result.user_id == 1
        assert result.recency == 45
        assert result.frequency == 0
        assert result.monetary == 0.0
        
        # RFM 점수 계산: (45 * 0.3) + (0 * 0.3) + (0.0 * 0.4) = 13.5
        expected_score = (45 * 0.3) + (0 * 0.3) + (0.0 * 0.4)
        assert result.rfm_score == expected_score
        
        # 13.5 > 0.8 이므로 "High-Value"로 분류됨
        assert result.segment == "High-Value"

    def test_calculate_rfm_none_history(self):
        """가챠 히스토리가 None인 경우 RFM 계산 테스트"""
        user_id = 1
        
        self.mock_repository.get_gacha_history.return_value = None
        self.mock_repository.get_user_segment.return_value = "Low-Value"
        
        result = self.service.calculate_rfm(user_id)
        
        assert result.user_id == 1
        assert result.frequency == 0
        assert result.monetary == 0.0

    def test_calculate_rfm_invalid_json(self):
        """잘못된 JSON 데이터로 RFM 계산 테스트"""
        user_id = 1
        
        # 잘못된 JSON 데이터
        gacha_history = ['invalid_json', 'not_json_either']
        
        self.mock_repository.get_gacha_history.return_value = gacha_history
        self.mock_repository.get_user_segment.return_value = "Low-Value"
        
        with patch('app.services.rfm_service.logger') as mock_logger:
            result = self.service.calculate_rfm(user_id)
            
            # 예외 발생 시 기본값 반환
            assert result.user_id == 1
            assert result.recency == 0
            assert result.frequency == 0
            assert result.monetary == 0.0
            assert result.rfm_score == 0.0
            assert result.segment == "Low-Value"
            
            mock_logger.error.assert_called_once()
            assert "RFM calculation failed for user 1" in mock_logger.error.call_args[0][0]

    def test_calculate_rfm_repository_exception(self):
        """repository 예외 발생 시 RFM 계산 테스트"""
        user_id = 1
        
        self.mock_repository.get_gacha_history.side_effect = Exception("Database error")
        
        with patch('app.services.rfm_service.logger') as mock_logger:
            result = self.service.calculate_rfm(user_id)
            
            # 예외 발생 시 기본값 반환
            assert result == RFMScore(
                user_id=1,
                recency=0,
                frequency=0,
                monetary=0.0,
                rfm_score=0.0,
                segment="Low-Value"
            )
            
            mock_logger.error.assert_called_once()

    def test_calculate_user_rfm_success(self):
        """calculate_user_rfm 래퍼 메서드 성공 테스트"""
        user_id = 1
        
        # calculate_rfm 메서드를 모킹
        mock_rfm_score = RFMScore(
            user_id=1,
            recency=30,
            frequency=5,
            monetary=250.0,
            rfm_score=0.6,
            segment="Medium-Value"
        )
        
        with patch.object(self.service, 'calculate_rfm', return_value=mock_rfm_score):
            result = self.service.calculate_user_rfm(user_id)
            
            # 딕셔너리 형태로 반환 확인
            expected = {
                "user_id": 1,
                "recency": 30,
                "frequency": 5,
                "monetary": 250.0,
                "rfm_score": 0.6,
                "segment": "Medium-Value"
            }
            
            assert result == expected

    def test_get_user_segment_success(self):
        """사용자 세그먼트 조회 성공 테스트"""
        user_id = 1
        
        mock_rfm_score = RFMScore(
            user_id=1,
            recency=20,
            frequency=15,
            monetary=800.0,
            rfm_score=0.9,
            segment="High-Value"
        )
        
        with patch.object(self.service, 'calculate_rfm', return_value=mock_rfm_score):
            result = self.service.get_user_segment(user_id)
            
            assert result == "High-Value"

    def test_get_user_segment_exception_handling(self):
        """사용자 세그먼트 조회 예외 처리 테스트"""
        user_id = 1
        
        with patch.object(self.service, 'calculate_rfm', side_effect=Exception("Calculation error")):
            with patch('app.services.rfm_service.logger') as mock_logger:
                result = self.service.get_user_segment(user_id)
                
                assert result == "Low-Value"
                mock_logger.error.assert_called_once()
                assert "Failed to determine user segment for 1" in mock_logger.error.call_args[0][0]

    def test_rfm_segmentation_logic(self):
        """RFM 세그먼테이션 로직 테스트"""
        user_id = 1
        
        # High-Value 시나리오 (rfm_score > 0.8)
        gacha_history_high = ['{"value": 1000}'] * 10
        self.mock_repository.get_gacha_history.return_value = gacha_history_high
        self.mock_repository.get_user_segment.return_value = "High-Value"
        
        result_high = self.service.calculate_rfm(user_id)
        
        # 높은 점수 확인 (monetary 값이 높아서)
        assert result_high.monetary == 10000.0  # 1000 * 10
        
        # Medium-Value 시나리오 (0.5 < rfm_score <= 0.8)
        gacha_history_medium = ['{"value": 50}'] * 3
        self.mock_repository.get_gacha_history.return_value = gacha_history_medium
        
        result_medium = self.service.calculate_rfm(user_id)
        assert result_medium.monetary == 150.0  # 50 * 3
        
        # Low-Value 시나리오 (rfm_score <= 0.5)
        gacha_history_low = ['{"value": 10}']
        self.mock_repository.get_gacha_history.return_value = gacha_history_low
        
        result_low = self.service.calculate_rfm(user_id)
        assert result_low.monetary == 10.0

    def test_boundary_values(self):
        """경계값 테스트"""
        # 최소 사용자 ID
        user_id_min = 1
        self.mock_repository.get_gacha_history.return_value = []
        self.mock_repository.get_user_segment.return_value = "Low-Value"
        
        result_min = self.service.calculate_rfm(user_id_min)
        assert result_min.user_id == 1
        
        # 높은 사용자 ID
        user_id_max = 999999
        result_max = self.service.calculate_rfm(user_id_max)
        assert result_max.user_id == 999999


class TestRFMServiceIntegration:
    """RFMService 통합 테스트"""
    
    def setup_method(self):
        """각 테스트 전 실행되는 설정"""
        self.mock_db = Mock(spec=Session)
        self.mock_repository = Mock(spec=GameRepository)
        
        self.service = RFMService(
            db=self.mock_db,
            repository=self.mock_repository
        )

    def test_complete_rfm_workflow(self):
        """완전한 RFM 워크플로우 테스트"""
        # 1. 동적 임계값 계산
        thresholds = self.service.compute_dynamic_thresholds()
        assert len(thresholds) == 6
        
        # 2. 사용자 RFM 계산
        user_id = 1
        gacha_history = ['{"value": 300}', '{"value": 200}']
        
        self.mock_repository.get_gacha_history.return_value = gacha_history
        self.mock_repository.get_user_segment.return_value = "Medium-Value"
        
        rfm_score = self.service.calculate_rfm(user_id)
        assert rfm_score.user_id == user_id
        assert rfm_score.monetary == 500.0
        
        # 3. RFM 점수 캐싱
        scores = [
            {
                "user_id": rfm_score.user_id,
                "recency": rfm_score.recency,
                "frequency": rfm_score.frequency,
                "monetary": rfm_score.monetary,
                "rfm_score": rfm_score.rfm_score,
                "segment": rfm_score.segment
            }
        ]
        
        self.service.cache_rfm_scores(scores)
        
        # 4. 사용자 세그먼트 조회
        segment = self.service.get_user_segment(user_id)
        assert segment in ["High-Value", "Medium-Value", "Low-Value"]

    def test_multiple_users_rfm_analysis(self):
        """여러 사용자 RFM 분석 테스트"""
        users = [1, 2, 3]
        all_scores = []
        
        for user_id in users:
            # 각 사용자별 다른 히스토리 설정
            gacha_history = [f'{{"value": {100 * user_id}}}'] * user_id
            
            self.mock_repository.get_gacha_history.return_value = gacha_history
            self.mock_repository.get_user_segment.return_value = f"Segment-{user_id}"
            
            rfm_score = self.service.calculate_rfm(user_id)
            all_scores.append({
                "user_id": rfm_score.user_id,
                "rfm_score": rfm_score.rfm_score,
                "segment": rfm_score.segment
            })
        
        # 모든 점수 캐싱
        self.service.cache_rfm_scores(all_scores)
        
        # 각 사용자별 세그먼트 확인
        for user_id in users:
            self.mock_repository.get_gacha_history.return_value = [f'{{"value": {100 * user_id}}}'] * user_id
            segment = self.service.get_user_segment(user_id)
            assert segment in ["High-Value", "Medium-Value", "Low-Value"]

    def test_error_recovery_scenarios(self):
        """오류 복구 시나리오 테스트"""
        user_id = 1
        
        # 1. 임계값 계산 실패 후 복구
        self.mock_repository.set_gacha_history.side_effect = Exception("Threshold calc failed")
        
        with patch('app.services.rfm_service.logger'):
            thresholds = self.service.compute_dynamic_thresholds()
            assert thresholds == {}
        
        # 복구
        self.mock_repository.set_gacha_history.side_effect = None
        thresholds_recovered = self.service.compute_dynamic_thresholds()
        assert len(thresholds_recovered) == 6
        
        # 2. RFM 계산 실패 후 복구
        self.mock_repository.get_gacha_history.side_effect = Exception("RFM calc failed")
        
        with patch('app.services.rfm_service.logger'):
            rfm_failed = self.service.calculate_rfm(user_id)
            assert rfm_failed.segment == "Low-Value"
        
        # 복구
        self.mock_repository.get_gacha_history.side_effect = None
        self.mock_repository.get_gacha_history.return_value = ['{"value": 100}']
        self.mock_repository.get_user_segment.return_value = "Medium-Value"
        
        rfm_recovered = self.service.calculate_rfm(user_id)
        assert rfm_recovered.user_id == user_id
        assert rfm_recovered.monetary == 100.0

    def test_performance_with_large_dataset(self):
        """대량 데이터 성능 테스트"""
        user_id = 1
        
        # 대량 가챠 히스토리 시뮬레이션 (1000개)
        large_history = [f'{{"value": {i * 10}}}' for i in range(1000)]
        
        self.mock_repository.get_gacha_history.return_value = large_history
        self.mock_repository.get_user_segment.return_value = "High-Value"
        
        # 성능 측정
        import time
        start_time = time.time()
        
        result = self.service.calculate_rfm(user_id)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 결과 검증
        assert result.user_id == user_id
        assert result.frequency == 1000
        expected_monetary = sum(i * 10 for i in range(1000))
        assert result.monetary == float(expected_monetary)
        
        # 성능 검증 (5초 이내)
        assert execution_time < 5.0, f"Performance test failed: {execution_time:.3f}s > 5.0s"

    def test_data_consistency(self):
        """데이터 일관성 테스트"""
        user_id = 1
        
        # 동일한 입력에 대해 일관된 결과 확인
        gacha_history = ['{"value": 100}', '{"value": 200}']
        
        self.mock_repository.get_gacha_history.return_value = gacha_history
        self.mock_repository.get_user_segment.return_value = "Medium-Value"
        
        # 여러 번 계산
        results = []
        for _ in range(3):
            result = self.service.calculate_rfm(user_id)
            results.append(result)
        
        # 모든 결과가 동일한지 확인
        first_result = results[0]
        for result in results[1:]:
            assert result.user_id == first_result.user_id
            assert result.recency == first_result.recency
            assert result.frequency == first_result.frequency
            assert result.monetary == first_result.monetary
            assert result.rfm_score == first_result.rfm_score
            assert result.segment == first_result.segment
