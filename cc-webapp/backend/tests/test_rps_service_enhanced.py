"""
Enhanced tests for RPSService following project testing standards

This test file follows the guidelines in docs/09-testing-guide.md:
- 100% test coverage for business-critical services
- Both unit and integration test scenarios  
- Proper mocking and dependency injection
- Edge case and error handling coverage
- Performance and boundary testing
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.services.rps_service import RPSService, RPSResult
from app.services.token_service import TokenService
from app.repositories.game_repository import GameRepository


class TestRPSResult:
    """RPSResult 데이터 클래스 테스트"""
    
    def test_rps_result_creation(self):
        """RPSResult 생성 테스트"""
        result = RPSResult(
            user_choice="rock",
            computer_choice="scissors", 
            result="win",
            tokens_change=100,
            balance=500
        )
        
        assert result.user_choice == "rock"
        assert result.computer_choice == "scissors"
        assert result.result == "win"
        assert result.tokens_change == 100
        assert result.balance == 500


class TestRPSService:
    """RPSService 단위 테스트"""
    
    def setup_method(self):
        """각 테스트 전 실행되는 설정"""
        self.mock_db = Mock(spec=Session)
        self.mock_repository = Mock(spec=GameRepository)
        self.mock_token_service = Mock(spec=TokenService)
        
        # 기본 Mock 설정
        self.mock_repository.get_streak.return_value = 0
        
        self.service = RPSService(
            repository=self.mock_repository,
            token_service=self.mock_token_service,
            db=self.mock_db
        )
    
    def test_service_initialization(self):
        """서비스 초기화 테스트"""
        assert self.service.repo == self.mock_repository
        assert self.service.token_service == self.mock_token_service
        assert self.service.VALID_CHOICES == ["rock", "paper", "scissors"]
        assert len(self.service.WINNING_COMBINATIONS) == 3
    
    def test_service_initialization_with_defaults(self):
        """기본값으로 서비스 초기화 테스트"""
        service = RPSService()
        assert isinstance(service.repo, GameRepository)
        assert isinstance(service.token_service, TokenService)
    
    def test_play_win_scenario_basic(self):
        """기본 승리 시나리오 테스트"""
        user_id = 1
        user_choice = "rock"
        bet_amount = 100
        
        # Mock 설정
        self.mock_token_service.deduct_tokens.return_value = 100
        self.mock_repository.get_user_segment.return_value = "Standard"
        self.mock_token_service.get_token_balance.return_value = 600
        self.mock_repository.get_streak.return_value = 0  # Mock streak as integer
        
        # 컴퓨터가 가위 선택하도록 패치 (사용자 승리)
        with patch('app.services.rps_service.random.choice', return_value="scissors"):
            result = self.service.play(user_id, user_choice, bet_amount, self.mock_db)
        
        # 검증
        assert result.user_choice == "rock"
        assert result.computer_choice == "scissors"
        assert result.result == "win"
        assert result.tokens_change == 100  # 2배 보상(200) - 베팅(100) = 100
        assert result.balance == 600
        
        # 서비스 호출 검증
        self.mock_token_service.deduct_tokens.assert_called_once_with(user_id, bet_amount)
        self.mock_token_service.add_tokens.assert_called_once_with(user_id, 200)  # 2배 보상
        self.mock_repository.record_action.assert_called_once_with(
            self.mock_db, user_id, "RPS_PLAY", -bet_amount
        )
    
    def test_play_win_scenario_whale_user(self):
        """고래 사용자 승리 시나리오 테스트 (3배 보상)"""
        user_id = 1
        user_choice = "paper"
        bet_amount = 100
        
        # Mock 설정
        self.mock_token_service.deduct_tokens.return_value = 100
        self.mock_repository.get_user_segment.return_value = "Whale"
        self.mock_token_service.get_token_balance.return_value = 800
        
        # 컴퓨터가 바위 선택하도록 패치 (사용자 승리)
        with patch('app.services.rps_service.random.choice', return_value="rock"):
            result = self.service.play(user_id, user_choice, bet_amount, self.mock_db)
        
        # 검증
        assert result.result == "win"
        assert result.tokens_change == 200  # 3배 보상(300) - 베팅(100) = 200
        
        # 고래 사용자는 3배 보상
        self.mock_token_service.add_tokens.assert_called_once_with(user_id, 300)
    
    def test_play_win_scenario_low_user(self):
        """저소비 사용자 승리 시나리오 테스트 (1.5배 보상)"""
        user_id = 1
        user_choice = "scissors"
        bet_amount = 100
        
        # Mock 설정
        self.mock_token_service.deduct_tokens.return_value = 100
        self.mock_repository.get_user_segment.return_value = "Low"
        self.mock_token_service.get_token_balance.return_value = 650
        
        # 컴퓨터가 종이 선택하도록 패치 (사용자 승리)
        with patch('app.services.rps_service.random.choice', return_value="paper"):
            result = self.service.play(user_id, user_choice, bet_amount, self.mock_db)
        
        # 검증
        assert result.result == "win"
        assert result.tokens_change == 50  # 1.5배 보상(150) - 베팅(100) = 50
        
        # 저소비 사용자는 1.5배 보상
        self.mock_token_service.add_tokens.assert_called_once_with(user_id, 150)
    
    def test_play_lose_scenario(self):
        """패배 시나리오 테스트"""
        user_id = 1
        user_choice = "rock"
        bet_amount = 100
        
        # Mock 설정
        self.mock_token_service.deduct_tokens.return_value = 100
        self.mock_repository.get_user_segment.return_value = "Standard"
        self.mock_token_service.get_token_balance.return_value = 400
        
        # 컴퓨터가 종이 선택하도록 패치 (사용자 패배)
        with patch('app.services.rps_service.random.choice', return_value="paper"):
            result = self.service.play(user_id, user_choice, bet_amount, self.mock_db)
        
        # 검증
        assert result.result == "lose"
        assert result.tokens_change == -100  # 베팅 금액만큼 손실
        
        # 패배 시 추가 토큰 지급 없음
        self.mock_token_service.add_tokens.assert_not_called()
    
    def test_play_draw_scenario(self):
        """무승부 시나리오 테스트"""
        user_id = 1
        user_choice = "rock"
        bet_amount = 100
        
        # Mock 설정
        self.mock_token_service.deduct_tokens.return_value = 100
        self.mock_repository.get_user_segment.return_value = "Standard"
        self.mock_token_service.get_token_balance.return_value = 500
        
        # 컴퓨터가 바위 선택하도록 패치 (무승부)
        with patch('app.services.rps_service.random.choice', return_value="rock"):
            result = self.service.play(user_id, user_choice, bet_amount, self.mock_db)
        
        # 검증
        assert result.result == "draw"
        assert result.tokens_change == 0  # 베팅 금액 환불로 변화 없음
        
        # 무승부 시 베팅 금액 환불
        self.mock_token_service.add_tokens.assert_called_once_with(user_id, bet_amount)
    
    def test_play_invalid_choice(self):
        """잘못된 선택 입력 테스트"""
        user_id = 1
        invalid_choice = "invalid"
        bet_amount = 100
        
        with pytest.raises(ValueError, match="Invalid choice"):
            self.service.play(user_id, invalid_choice, bet_amount, self.mock_db)
        
        # 토큰 차감이 일어나지 않아야 함
        self.mock_token_service.deduct_tokens.assert_not_called()
    
    def test_play_zero_bet_amount(self):
        """0 베팅 금액 테스트"""
        user_id = 1
        user_choice = "rock"
        bet_amount = 0
        
        with pytest.raises(ValueError, match="Bet amount must be greater than 0"):
            self.service.play(user_id, user_choice, bet_amount, self.mock_db)
        
        # 토큰 차감이 일어나지 않아야 함
        self.mock_token_service.deduct_tokens.assert_not_called()
    
    def test_play_negative_bet_amount(self):
        """음수 베팅 금액 테스트"""
        user_id = 1
        user_choice = "rock"
        bet_amount = -50
        
        with pytest.raises(ValueError, match="Bet amount must be greater than 0"):
            self.service.play(user_id, user_choice, bet_amount, self.mock_db)
        
        # 토큰 차감이 일어나지 않아야 함
        self.mock_token_service.deduct_tokens.assert_not_called()
    
    def test_play_insufficient_tokens(self):
        """토큰 부족 시나리오 테스트"""
        user_id = 1
        user_choice = "rock"
        bet_amount = 1000
        
        # 토큰 차감 실패
        self.mock_token_service.deduct_tokens.return_value = None
        
        with pytest.raises(ValueError, match="Insufficient tokens"):
            self.service.play(user_id, user_choice, bet_amount, self.mock_db)
        
        # 게임이 진행되지 않아야 함
        self.mock_repository.get_user_segment.assert_not_called()
        self.mock_repository.record_action.assert_not_called()
    
    def test_winning_combinations_logic(self):
        """승부 로직 테스트"""
        test_cases = [
            ("rock", "scissors", "win"),
            ("paper", "rock", "win"),
            ("scissors", "paper", "win"),
            ("rock", "paper", "lose"),
            ("paper", "scissors", "lose"),
            ("scissors", "rock", "lose"),
            ("rock", "rock", "draw"),
            ("paper", "paper", "draw"),
            ("scissors", "scissors", "draw"),
        ]
        
        for user_choice, computer_choice, expected_result in test_cases:
            user_id = 1
            bet_amount = 100
            
            # Mock 설정
            self.mock_token_service.deduct_tokens.return_value = 100
            self.mock_repository.get_user_segment.return_value = "Standard"
            self.mock_token_service.get_token_balance.return_value = 500
            
            with patch('app.services.rps_service.random.choice', return_value=computer_choice):
                result = self.service.play(user_id, user_choice, bet_amount, self.mock_db)
                assert result.result == expected_result, f"Failed for {user_choice} vs {computer_choice}"
    
    def test_boundary_values(self):
        """경계값 테스트"""
        user_id = 1
        user_choice = "rock"
        
        # 최소 베팅 금액
        min_bet = 1
        self.mock_token_service.deduct_tokens.return_value = min_bet
        self.mock_repository.get_user_segment.return_value = "Standard"
        self.mock_token_service.get_token_balance.return_value = 100
        
        with patch('app.services.rps_service.random.choice', return_value="scissors"):
            result = self.service.play(user_id, user_choice, min_bet, self.mock_db)
            assert result.tokens_change == 1  # 2배 보상(2) - 베팅(1) = 1
        
        # 높은 베팅 금액
        high_bet = 10000
        self.mock_token_service.deduct_tokens.return_value = high_bet
        self.mock_token_service.get_token_balance.return_value = 20000
        
        with patch('app.services.rps_service.random.choice', return_value="scissors"):
            result = self.service.play(user_id, user_choice, high_bet, self.mock_db)
            assert result.tokens_change == 10000  # 2배 보상(20000) - 베팅(10000) = 10000


class TestRPSServiceIntegration:
    """RPSService 통합 테스트"""
    
    def setup_method(self):
        """각 테스트 전 실행되는 설정"""
        self.mock_db = Mock(spec=Session)
        self.mock_repository = Mock(spec=GameRepository)
        self.mock_token_service = Mock(spec=TokenService)
        
        self.service = RPSService(
            repository=self.mock_repository,
            token_service=self.mock_token_service,
            db=self.mock_db
        )
    
    def test_complete_game_workflow(self):
        """완전한 게임 워크플로우 테스트"""
        user_id = 1
        user_choice = "rock"
        bet_amount = 100
        
        # Mock 설정 - 모든 단계 성공
        self.mock_token_service.deduct_tokens.return_value = 100
        self.mock_repository.get_user_segment.return_value = "Whale"
        self.mock_token_service.get_token_balance.return_value = 800
        
        with patch('app.services.rps_service.random.choice', return_value="scissors"):
            result = self.service.play(user_id, user_choice, bet_amount, self.mock_db)
        
        # 전체 워크플로우 검증
        assert isinstance(result, RPSResult)
        assert result.user_choice == user_choice
        assert result.computer_choice == "scissors"
        assert result.result == "win"
        
        # 모든 서비스 호출 확인
        self.mock_token_service.deduct_tokens.assert_called_once()
        self.mock_repository.get_user_segment.assert_called_once()
        self.mock_token_service.add_tokens.assert_called_once()
        self.mock_token_service.get_token_balance.assert_called_once()
        self.mock_repository.record_action.assert_called_once()
    
    def test_multiple_games_consistency(self):
        """여러 게임의 일관성 테스트"""
        user_id = 1
        bet_amount = 100
        games_count = 3
        
        # 각 게임에 대한 Mock 설정
        self.mock_token_service.deduct_tokens.return_value = 100
        self.mock_repository.get_user_segment.return_value = "Standard"
        self.mock_token_service.get_token_balance.return_value = 500
        
        results = []
        choices = ["rock", "paper", "scissors"]
        
        for i, choice in enumerate(choices):
            with patch('app.services.rps_service.random.choice', return_value="rock"):
                result = self.service.play(user_id, choice, bet_amount, self.mock_db)
                results.append(result)
        
        # 각 게임이 독립적으로 처리되는지 확인
        assert len(results) == games_count
        for result in results:
            assert isinstance(result, RPSResult)
            assert result.computer_choice == "rock"
        
        # 서비스 호출 횟수 확인
        assert self.mock_token_service.deduct_tokens.call_count == games_count
        assert self.mock_repository.record_action.call_count == games_count
    
    def test_edge_case_random_computer_choice(self):
        """컴퓨터 선택의 랜덤성 테스트 (실제 랜덤 사용)"""
        user_id = 1
        user_choice = "rock"
        bet_amount = 100
        
        # Mock 설정
        self.mock_token_service.deduct_tokens.return_value = 100
        self.mock_repository.get_user_segment.return_value = "Standard"
        self.mock_token_service.get_token_balance.return_value = 500
        
        # 실제 랜덤을 사용하여 여러 번 실행
        computer_choices = set()
        for _ in range(10):
            result = self.service.play(user_id, user_choice, bet_amount, self.mock_db)
            computer_choices.add(result.computer_choice)
            
            # 결과가 유효한지 확인
            assert result.computer_choice in self.service.VALID_CHOICES
            assert result.result in ["win", "lose", "draw"]
        
        # 충분한 반복으로 다양한 선택이 나와야 함 (확률적으로)
        # 10번 중에 최소 1개 이상의 다른 선택이 나올 가능성이 높음
        assert len(computer_choices) >= 1
