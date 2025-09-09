"""Extended tests for game_service.py to improve coverage."""

import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
import pytest

from app.services.game_service import GameService
from app.repositories.game_repository import GameRepository
from app.services.slot_service import SlotSpinResult
from app.services.roulette_service import RouletteSpinResult
from app.services.gacha_service import GachaPullResult


class TestGameServiceInteractions(unittest.TestCase):
    """Test the GameService class and its interactions with other services."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_repo = MagicMock(spec=GameRepository)
        self.mock_db = MagicMock(spec=Session)
        
        # Create the service with mock repository
        self.service = GameService(repository=self.mock_repo)
        
        # Setup mocks for the underlying services
        self.service.slot_service = MagicMock()
        self.service.roulette_service = MagicMock()
        self.service.gacha_service = MagicMock()

    def test_initialization_with_repository(self):
        """Test initialization with a provided repository."""
        service = GameService(repository=self.mock_repo)
        assert service.repo == self.mock_repo

    def test_initialization_without_repository(self):
        """Test initialization without a repository creates a new one."""
        with patch('app.services.game_service.GameRepository') as mock_repo_class:
            mock_repo_instance = MagicMock()
            mock_repo_class.return_value = mock_repo_instance
            
            service = GameService()
            
            mock_repo_class.assert_called_once()
            assert service.repo == mock_repo_instance

    def test_slot_spin_delegates_correctly(self):
        """Test that slot_spin delegates to the slot service correctly."""
        # Setup mock return value for slot service
        mock_result = MagicMock(spec=SlotSpinResult)
        self.service.slot_service.spin.return_value = mock_result
        
        # Call the method
        result = self.service.slot_spin(user_id=123, db=self.mock_db)
        
        # Verify the delegation worked correctly
        self.service.slot_service.spin.assert_called_once_with(123, self.mock_db)
        assert result == mock_result

    def test_roulette_spin_delegates_correctly(self):
        """Test that roulette_spin delegates to the roulette service correctly."""
        # Setup mock return value for roulette service
        mock_result = MagicMock(spec=RouletteSpinResult)
        self.service.roulette_service.spin.return_value = mock_result
        
        # Call the method
        result = self.service.roulette_spin(
            user_id=123, 
            bet=10, 
            bet_type="color", 
            value="red", 
            db=self.mock_db
        )
        
        # Verify the delegation worked correctly
        self.service.roulette_service.spin.assert_called_once_with(
            123, 10, "color", "red", self.mock_db
        )
        assert result == mock_result

    def test_gacha_pull_delegates_correctly(self):
        """Test that gacha_pull delegates to the gacha service correctly."""
        # Setup mock return value for gacha service
        mock_result = MagicMock(spec=GachaPullResult)
        self.service.gacha_service.pull.return_value = mock_result
        
        # Call the method
        result = self.service.gacha_pull(user_id=123, count=5, db=self.mock_db)
        
        # Verify the delegation worked correctly
        self.service.gacha_service.pull.assert_called_once_with(123, 5, self.mock_db)
        assert result == mock_result

    def test_service_initialization_creates_all_subservices(self):
        """Test that all game subservices are initialized."""
        service = GameService(repository=self.mock_repo)
        
        # Verify all required services are initialized
        assert hasattr(service, 'slot_service')
        assert hasattr(service, 'roulette_service')
        assert hasattr(service, 'gacha_service')


# Pytest-style tests for integration scenarios
@pytest.fixture
def game_service_with_mocks():
    """Fixture to create a GameService with all dependencies mocked."""
    mock_repo = MagicMock(spec=GameRepository)
    service = GameService(repository=mock_repo)
    
    # Replace the actual service instances with mocks
    service.slot_service = MagicMock()
    service.roulette_service = MagicMock()
    service.gacha_service = MagicMock()
    
    return service, mock_repo


def test_game_service_error_handling_slot(game_service_with_mocks):
    """Test error handling in the slot_spin method."""
    service, mock_repo = game_service_with_mocks
    mock_db = MagicMock()
    
    # Configure the mock to raise an exception
    service.slot_service.spin.side_effect = ValueError("Insufficient tokens")
    
    # Test that the exception is propagated
    with pytest.raises(ValueError, match="Insufficient tokens"):
        service.slot_spin(user_id=123, db=mock_db)


def test_game_service_error_handling_roulette(game_service_with_mocks):
    """Test error handling in the roulette_spin method."""
    service, mock_repo = game_service_with_mocks
    mock_db = MagicMock()
    
    # Configure the mock to raise an exception
    service.roulette_service.spin.side_effect = ValueError("Invalid bet type")
    
    # Test that the exception is propagated
    with pytest.raises(ValueError, match="Invalid bet type"):
        service.roulette_spin(user_id=123, bet=10, bet_type="invalid", value=None, db=mock_db)


def test_game_service_error_handling_gacha(game_service_with_mocks):
    """Test error handling in the gacha_pull method."""
    service, mock_repo = game_service_with_mocks
    mock_db = MagicMock()
    
    # Configure the mock to raise an exception
    service.gacha_service.pull.side_effect = ValueError("Invalid pull count")
    
    # Test that the exception is propagated
    with pytest.raises(ValueError, match="Invalid pull count"):
        service.gacha_pull(user_id=123, count=0, db=mock_db)
