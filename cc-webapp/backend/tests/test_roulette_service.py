"""Tests for roulette game service."""

import pytest
from unittest.mock import MagicMock, patch
import random
from sqlalchemy.orm import Session

from app.services.roulette_service import RouletteService, RouletteSpinResult
from app.repositories.game_repository import GameRepository
from app.services.token_service import TokenService


@pytest.mark.skip(reason="Old roulette system has been replaced with prize roulette")
class TestRouletteService:
    """Tests for the RouletteService class."""

    def setup_method(self):
        """Setup test environment before each test."""
        self.repo = MagicMock(spec=GameRepository)
        self.token_service = MagicMock(spec=TokenService)
        self.token_service.db = None  # Add db attribute to mock
        self.db = MagicMock(spec=Session)
        self.service = RouletteService(repository=self.repo)  # Remove token_service parameter
        
        # Common setup for tests
        self.user_id = 1
        self.bet = 10

    def test_spin_with_insufficient_tokens(self):
        """Test roulette spin with insufficient tokens."""
        # Arrange
        self.token_service.deduct_tokens.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="토큰이 부족합니다"):
            self.service.spin(self.user_id, self.bet, "color", "red", self.db)

    @patch('random.randint')
    def test_spin_number_win(self, mock_randint):
        """Test roulette spin with a winning number bet."""
        # Arrange
        bet_type = "number"
        bet_value = "17"
        mock_randint.return_value = 17  # Force spin to land on 17
        self.token_service.deduct_tokens.return_value = self.bet
        self.token_service.get_token_balance.return_value = 1000
        self.repo.get_user_segment.return_value = "Medium"
        self.repo.get_streak.return_value = 0
        
        # Act
        result = self.service.spin(self.user_id, self.bet, bet_type, bet_value, self.db)
        
        # Assert
        assert result.winning_number == 17
        assert result.result == "win"
        assert result.tokens_change > 0
        self.token_service.add_tokens.assert_called_once()

    @patch('random.randint')
    def test_spin_color_win_red(self, mock_randint):
        """Test roulette spin with a winning red color bet."""
        # Arrange
        bet_type = "color"
        bet_value = "red"
        mock_randint.return_value = 1  # Red number (assuming odd numbers are red)
        self.token_service.deduct_tokens.return_value = self.bet
        self.token_service.get_token_balance.return_value = 1000
        self.repo.get_user_segment.return_value = "Medium"
        self.repo.get_streak.return_value = 0
        
        # Act
        result = self.service.spin(self.user_id, self.bet, bet_type, bet_value, self.db)
        
        # Assert
        assert result.winning_number == 1
        assert result.result == "win"
        assert result.tokens_change > 0
        self.token_service.add_tokens.assert_called_once()

    @patch('random.randint')
    def test_spin_color_win_black(self, mock_randint):
        """Test roulette spin with a winning black color bet."""
        # Arrange
        bet_type = "color"
        bet_value = "black"
        mock_randint.return_value = 2  # Black number (assuming even numbers are black)
        self.token_service.deduct_tokens.return_value = self.bet
        self.token_service.get_token_balance.return_value = 1000
        self.repo.get_user_segment.return_value = "Medium"
        self.repo.get_streak.return_value = 0
        
        # Act
        result = self.service.spin(self.user_id, self.bet, bet_type, bet_value, self.db)
        
        # Assert
        assert result.winning_number == 2
        assert result.result == "win"
        assert result.tokens_change > 0
        self.token_service.add_tokens.assert_called_once()

    @patch('random.randint')
    def test_spin_odd_even_win_odd(self, mock_randint):
        """Test roulette spin with a winning odd bet."""
        # Arrange
        bet_type = "odd_even"
        bet_value = "odd"
        mock_randint.return_value = 35  # Odd number
        self.token_service.deduct_tokens.return_value = self.bet
        self.token_service.get_token_balance.return_value = 1000
        self.repo.get_user_segment.return_value = "Medium"
        self.repo.get_streak.return_value = 0
        
        # Act
        result = self.service.spin(self.user_id, self.bet, bet_type, bet_value, self.db)
        
        # Assert
        assert result.winning_number == 35
        assert result.result == "win"
        assert result.tokens_change > 0
        self.token_service.add_tokens.assert_called_once()

    @patch('random.randint')
    def test_spin_odd_even_win_even(self, mock_randint):
        """Test roulette spin with a winning even bet."""
        # Arrange
        bet_type = "odd_even"
        bet_value = "even"
        mock_randint.return_value = 10  # Even number
        self.token_service.deduct_tokens.return_value = self.bet
        self.token_service.get_token_balance.return_value = 1000
        self.repo.get_user_segment.return_value = "Medium"
        self.repo.get_streak.return_value = 0
        
        # Act
        result = self.service.spin(self.user_id, self.bet, bet_type, bet_value, self.db)
        
        # Assert
        assert result.winning_number == 10
        assert result.result == "win"
        assert result.tokens_change > 0
        self.token_service.add_tokens.assert_called_once()
        
    @patch('random.randint')
    def test_spin_zero_always_loses(self, mock_randint):
        """Test that zero causes all normal bets to lose."""
        # Arrange
        mock_randint.return_value = 0  # Force spin to land on zero
        self.token_service.deduct_tokens.return_value = self.bet
        self.token_service.get_token_balance.return_value = 1000 - self.bet
        self.repo.get_user_segment.return_value = "Medium"
        self.repo.get_streak.return_value = 0
        
        # Color bet on red
        result = self.service.spin(self.user_id, self.bet, "color", "red", self.db)
        assert result.result == "lose"
        assert result.tokens_change == -self.bet
        
        # Odd/even bet
        result = self.service.spin(self.user_id, self.bet, "odd_even", "odd", self.db)
        assert result.result == "lose"
        assert result.tokens_change == -self.bet

    @patch('random.randint')
    def test_spin_jackpot_on_zero_number_bet(self, mock_randint):
        """Test jackpot when betting on zero and winning."""
        # Arrange
        bet_type = "number"
        bet_value = "0"
        mock_randint.return_value = 0  # Force spin to land on zero
        self.token_service.deduct_tokens.return_value = self.bet
        self.token_service.get_token_balance.return_value = 1000
        self.repo.get_user_segment.return_value = "Medium"
        self.repo.get_streak.return_value = 0
        
        # Act
        result = self.service.spin(self.user_id, self.bet, bet_type, bet_value, self.db)
        
        # Assert - jackpot should pay extra when hitting zero
        assert result.winning_number == 0
        assert result.result == "jackpot"
        assert result.tokens_change > 0
        assert result.animation == "jackpot"
        self.token_service.add_tokens.assert_called_once()
        
    def test_bet_amount_limits(self):
        """Test bet amount is clamped to valid range."""
        # Arrange - bet below minimum
        self.token_service.deduct_tokens.return_value = 1  # Min bet
        self.token_service.get_token_balance.return_value = 999
        self.repo.get_user_segment.return_value = "Medium"
        self.repo.get_streak.return_value = 0
        
        with patch('random.randint', return_value=1):
            # Act with bet below minimum (should be clamped to 1)
            result = self.service.spin(self.user_id, -5, "color", "red", self.db)
            
            # Assert
            self.token_service.deduct_tokens.assert_called_once_with(self.user_id, 1)
        
        # Reset mocks
        self.token_service.reset_mock()
        
        # Arrange - bet above maximum
        self.token_service.deduct_tokens.return_value = 50  # Max bet
        self.token_service.get_token_balance.return_value = 950
        
        with patch('random.randint', return_value=1):
            # Act with bet above maximum (should be clamped to 50)
            result = self.service.spin(self.user_id, 100, "color", "red", self.db)
            
            # Assert
            self.token_service.deduct_tokens.assert_called_once_with(self.user_id, 50)

    def test_streak_handling(self):
        """Test streak counter updates correctly."""
        # Arrange
        self.token_service.deduct_tokens.return_value = self.bet
        self.token_service.get_token_balance.return_value = 1000
        self.repo.get_user_segment.return_value = "Medium"
        self.repo.get_streak.return_value = 3
        
        # Act - Lose
        with patch('random.randint', return_value=0):
            result = self.service.spin(self.user_id, self.bet, "color", "red", self.db)
        
        # Assert - streak should increment
        self.repo.set_streak.assert_called_with(self.user_id, 4)
        
        # Reset mocks
        self.repo.reset_mock()
        
        # Act - Win
        with patch('random.randint', return_value=1):
            result = self.service.spin(self.user_id, self.bet, "color", "red", self.db)
        
        # Assert - streak should reset
        self.repo.set_streak.assert_called_with(self.user_id, 0)


class TestRoulettePayouts:
    """Tests for roulette payout calculations."""
    
    def setup_method(self):
        """Setup for payout tests."""
        self.repo = MagicMock(spec=GameRepository)
        self.token_service = MagicMock(spec=TokenService)
        self.token_service.db = None  # Add db attribute to mock
        self.db = MagicMock(spec=Session)
        self.service = RouletteService(repository=self.repo)  # Remove token_service parameter
        
        self.user_id = 1
        self.bet = 10
        
        # Setup basic mocks
        self.token_service.deduct_tokens.return_value = self.bet
        self.token_service.get_token_balance.return_value = 1000
        self.repo.get_streak.return_value = 0

    def test_segment_adjusted_house_edge(self):
        """Test house edge adjusts based on segment."""
        # Arrange
        test_cases = [
            {"segment": "Whale", "expected_edge": 0.05},
            {"segment": "Medium", "expected_edge": 0.10},
            {"segment": "Low", "expected_edge": 0.15},
            {"segment": "Unknown", "expected_edge": 0.10}  # Should default
        ]
        
        for case in test_cases:
            # Setup for this case
            self.repo.get_user_segment.return_value = case["segment"]
            
            # Reset add_tokens to check payout
            self.token_service.reset_mock()
            
            # Act - with guaranteed win on number bet (35x payout)
            with patch('random.randint', return_value=7):
                self.service.spin(self.user_id, self.bet, "number", "7", self.db)
            
            # Assert
            expected_payout = int(self.bet * 35 * (1 - case["expected_edge"]))
            self.token_service.add_tokens.assert_called_once_with(self.user_id, expected_payout)
