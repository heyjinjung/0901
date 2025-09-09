"""Tests for gacha service."""

import pytest
import os
import json
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.services.gacha_service import GachaService, GachaPullResult
from app.repositories.game_repository import GameRepository
from app.services.token_service import TokenService


class TestGachaService:
    """Tests for the GachaService class."""

    def setup_method(self):
        """Setup test environment before each test."""
        self.repo = MagicMock(spec=GameRepository)
        self.token_service = MagicMock(spec=TokenService)
        self.db = MagicMock(spec=Session)
        
        # Create service with mocked dependencies
        self.service = GachaService(repository=self.repo, token_service=self.token_service)
        
        # Common setup for tests
        self.user_id = 1

    def test_initialization_with_default_rarity_table(self):
        """Test gacha service initializes with default rarity table."""
        # The service should load the default rarity table on init
        
        # Assert - Updated to include Near_Miss items
        assert len(self.service.rarity_table) == 6
        rarities = [r[0] for r in self.service.rarity_table]
        assert "Legendary" in rarities
        assert "Epic" in rarities
        assert "Rare" in rarities
        assert "Common" in rarities
        assert "Near_Miss_Epic" in rarities
        assert "Near_Miss_Legendary" in rarities
        
        # Probabilities should sum to 1.0
        probability_sum = sum(p for _, p in self.service.rarity_table)
        assert abs(probability_sum - 1.0) < 0.0001

    @patch.dict(os.environ, {"GACHA_RARITY_TABLE": '[["Legendary", 0.01], ["Super", 0.09], ["Normal", 0.9]]'})
    def test_initialization_with_custom_rarity_table(self):
        """Test gacha service loads rarity table from environment variable."""
        # Create a new service to load from the mocked env var
        service = GachaService(repository=self.repo, token_service=self.token_service)
        
        # Assert
        assert len(service.rarity_table) == 3
        rarities = [r[0] for r in service.rarity_table]
        assert "Legendary" in rarities
        assert "Super" in rarities 
        assert "Normal" in rarities

    def test_single_pull(self):
        """Test single gacha pull."""
        # Arrange
        count = 1
        self.token_service.deduct_tokens.return_value = 5000
        self.token_service.get_token_balance.return_value = 95000
        self.repo.get_gacha_count.return_value = 0
        self.repo.get_gacha_history.return_value = []
        
        # Act
        result = self.service.pull(self.user_id, count, self.db)
        
        # Assert
        self.token_service.deduct_tokens.assert_called_once_with(self.user_id, 5000)
        self.repo.record_action.assert_called_once()
        assert isinstance(result, GachaPullResult)
        assert len(result.results) == 1
        assert result.tokens_change == -5000
        assert result.balance == 95000

    def test_ten_pull(self):
        """Test ten-pull gacha (with discount)."""
        # Arrange
        count = 10
        self.token_service.deduct_tokens.return_value = 50000
        self.token_service.get_token_balance.return_value = 500000
        self.repo.get_gacha_count.return_value = 0
        self.repo.get_gacha_history.return_value = []
        
        # Act
        result = self.service.pull(self.user_id, count, self.db)
        
        # Assert
        self.token_service.deduct_tokens.assert_called_once_with(self.user_id, 50000)
        self.repo.record_action.assert_called_once()
        assert isinstance(result, GachaPullResult)
        assert len(result.results) == 10
        assert result.tokens_change == -50000
        assert result.balance == 500000

    def test_insufficient_tokens(self):
        """Test gacha pull with insufficient tokens."""
        # Arrange
        count = 1
        self.token_service.deduct_tokens.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="토큰이 부족합니다"):
            self.service.pull(self.user_id, count, self.db)

    def test_pity_system(self):
        """Test pity system guarantees an Epic after 90 pulls."""
        # Arrange
        count = 1
        self.token_service.deduct_tokens.return_value = 5000
        self.token_service.get_token_balance.return_value = 95000
        self.repo.get_gacha_history.return_value = []
        
        # Set current count to 89 (next pull triggers pity)
        self.repo.get_gacha_count.return_value = 89
        
        # Use patch to ensure we'd normally get a Common (lowest tier)
        with patch('random.random', return_value=0.99):  # This would normally give Common
            # Act
            result = self.service.pull(self.user_id, count, self.db)
            
            # Assert - with pity at 90, we should get at least an Epic
            assert result.results[0] in ["Epic", "Legendary"]
            
            # Pity counter should reset
            self.repo.set_gacha_count.assert_called_once_with(self.user_id, 0)

    def test_history_affects_probability(self):
        """Test that previous pulls affect future probabilities."""
        # Arrange
        count = 1
        self.token_service.deduct_tokens.return_value = 5000
        self.token_service.get_token_balance.return_value = 95000
        self.repo.get_gacha_count.return_value = 10
        
        # User recently got a Legendary
        self.repo.get_gacha_history.return_value = ["Legendary", "Common", "Common"]
        
        # With this setup and random value, user would normally get Legendary again
        # but the history should reduce probability
        with patch('random.random', return_value=0.004):  # Just below normal Legendary threshold
            # Act
            result = self.service.pull(self.user_id, count, self.db)
            
            # Assert - with history penalty, should get lower tier
            assert result.results[0] != "Legendary"
            
    def test_history_tracking(self):
        """Test that pull history is tracked correctly."""
        # Arrange
        count = 1
        self.token_service.deduct_tokens.return_value = 5000
        self.token_service.get_token_balance.return_value = 95000
        self.repo.get_gacha_count.return_value = 10
        original_history = ["Epic", "Common", "Rare", "Common"]
        self.repo.get_gacha_history.return_value = original_history.copy()
        
        # Force a specific result
        with patch('random.random', return_value=0.5):
            # Act
            result = self.service.pull(self.user_id, count, self.db)
            
            # Get what the result should be based on our rarity table
            expected_rarity = "Common"  # With 0.5, this should be Common
            
            # Assert history was updated correctly
            new_history = original_history.copy()
            new_history.insert(0, expected_rarity)
            new_history = new_history[:10]  # Limit to 10 items
            
            self.repo.set_gacha_history.assert_called_once_with(self.user_id, new_history)

    def test_reward_pool_limitation(self):
        """Test reward pool limits item availability."""
        # Arrange
        count = 1
        self.token_service.deduct_tokens.return_value = 5000
        self.token_service.get_token_balance.return_value = 95000
        self.repo.get_gacha_count.return_value = 10
        self.repo.get_gacha_history.return_value = []
        
        # Set up a limited reward pool
        self.service.reward_pool = {
            "Legendary": 0,  # No Legendary items left
            "Epic": 5,
            "Rare": 10,
            "Common": 100
        }
        
        # Force a roll that would give Legendary
        with patch('random.random', return_value=0.001):
            # Act
            result = self.service.pull(self.user_id, count, self.db)
            
            # Assert - should not get Legendary due to pool limitation
            assert result.results[0] != "Legendary"

    def test_update_config(self):
        """Test updating gacha configuration."""
        # Arrange
        new_rarity_table = [("SSR", 0.01), ("SR", 0.19), ("R", 0.80)]
        new_reward_pool = {"SSR": 5, "SR": 20, "R": 100}
        
        # Act
        self.service.update_config(rarity_table=new_rarity_table, reward_pool=new_reward_pool)
        
        # Assert
        assert self.service.rarity_table == new_rarity_table
        assert self.service.reward_pool == new_reward_pool
        
        # Verify get_config returns the updated values
        config = self.service.get_config()
        assert config["rarity_table"] == new_rarity_table
        assert config["reward_pool"] == new_reward_pool


class TestGachaProbabilityDistribution:
    """Tests for gacha probability distribution."""
    
    def setup_method(self):
        """Setup environment for probability tests."""
        self.repo = MagicMock(spec=GameRepository)
        self.token_service = MagicMock(spec=TokenService)
        self.db = MagicMock(spec=Session)
        self.service = GachaService(repository=self.repo, token_service=self.token_service)
        
        # Common setup
        self.user_id = 1
        self.token_service.deduct_tokens.return_value = 450  # For 10-pull
        self.token_service.get_token_balance.return_value = 550
        self.repo.get_gacha_count.return_value = 0
        self.repo.get_gacha_history.return_value = []

    @pytest.mark.skip(reason="This is a statistical test that may be flaky, use for manual verification")
    def test_large_sample_distribution(self):
        """Test distribution of many pulls matches expected probabilities."""
        # This is a statistical test that runs many pulls
        # We'll run 1000 ten-pulls (10,000 total pulls)
        results = {"Legendary": 0, "Epic": 0, "Rare": 0, "Common": 0}
        total_pulls = 0
        
        # Get expected probabilities from the service's rarity table
        expected_probs = {rarity: prob for rarity, prob in self.service.rarity_table}
        
        # Simulate many pulls
        num_samples = 100  # Reduce for normal testing, increase for manual verification
        
        for _ in range(num_samples):
            pull_result = self.service.pull(self.user_id, 10, self.db)
            for rarity in pull_result.results:
                results[rarity] += 1
                total_pulls += 1
        
        # Calculate actual percentages
        actual_probs = {rarity: count/total_pulls for rarity, count in results.items()}
        
        # Check that distributions are close
        # We allow some deviation since this is a random process
        for rarity, expected_prob in expected_probs.items():
            actual_prob = actual_probs.get(rarity, 0)
            # Allow deviation of up to 30% from expected probability
            assert abs(actual_prob - expected_prob) / expected_prob < 0.30, \
                   f"Expected {rarity} prob: {expected_prob}, got: {actual_prob}"
