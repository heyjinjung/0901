"""Tests for token_service.py with DB-based implementation."""

import unittest
from unittest.mock import MagicMock, patch
import pytest
from sqlalchemy.orm import Session

from app.services.token_service import TokenService
from app.repositories.game_repository import GameRepository
from app.models import User


class TestTokenService(unittest.TestCase):
    """Test case for TokenService class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_repo = MagicMock(spec=GameRepository)
        self.mock_db = MagicMock(spec=Session)
        self.token_service = TokenService(db=self.mock_db, repository=self.mock_repo)

    def test_init_with_repository(self):
        """Test initialization with a provided repository."""
        assert self.token_service.repository == self.mock_repo
        assert self.token_service.db == self.mock_db

    def test_init_without_repository(self):
        """Test initialization without a repository creates a new one."""
        with patch('app.services.token_service.GameRepository') as mock_repo_class:
            mock_repo_instance = MagicMock()
            mock_repo_class.return_value = mock_repo_instance
            
            service = TokenService(db=self.mock_db)
            
            mock_repo_class.assert_called_once()
            assert service.repository == mock_repo_instance
            assert service.db == self.mock_db

    def test_get_token_balance_success(self):
        """Test successful token balance retrieval."""
        # Mock user with token balance
        mock_user = MagicMock()
        mock_user.cyber_token_balance = 100
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        balance = self.token_service.get_token_balance(user_id=123)
        assert balance == 100

    def test_get_token_balance_no_user(self):
        """Test token balance retrieval when user doesn't exist."""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        balance = self.token_service.get_token_balance(user_id=123)
        assert balance == 0

    def test_get_token_balance_no_db(self):
        """Test token balance retrieval without database session."""
        service = TokenService(db=None)
        balance = service.get_token_balance(user_id=123)
        assert balance == 0

    def test_add_tokens_success(self):
        """Test successful token addition."""
        # Mock user with initial balance
        mock_user = MagicMock()
        mock_user.cyber_token_balance = 100
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        new_balance = self.token_service.add_tokens(user_id=123, amount=50)
        
        # Check that balance was updated
        assert mock_user.cyber_token_balance == 150
        assert new_balance == 150
        self.mock_db.commit.assert_called_once()

    def test_add_tokens_no_user(self):
        """Test token addition when user doesn't exist."""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        new_balance = self.token_service.add_tokens(user_id=123, amount=50)
        assert new_balance == 0

    def test_add_tokens_exception(self):
        """Test token addition with exception."""
        mock_user = MagicMock()
        mock_user.cyber_token_balance = 100
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_db.commit.side_effect = Exception("Database error")
        
        with patch('app.services.token_service.logger') as mock_logger:
            # Mock get_token_balance to return original balance
            with patch.object(self.token_service, 'get_token_balance', return_value=100):
                result = self.token_service.add_tokens(user_id=123, amount=50)
                assert result == 100  # Should return original balance

    def test_deduct_tokens_success(self):
        """Test successful token deduction."""
        mock_user = MagicMock()
        mock_user.cyber_token_balance = 100
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        new_balance = self.token_service.deduct_tokens(user_id=123, amount=50)
        
        assert mock_user.cyber_token_balance == 50
        assert new_balance == 50
        self.mock_db.commit.assert_called_once()

    def test_deduct_tokens_insufficient(self):
        """Test token deduction with insufficient tokens."""
        mock_user = MagicMock()
        mock_user.cyber_token_balance = 30  # Less than required
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = self.token_service.deduct_tokens(user_id=123, amount=50)
        assert result is None

    def test_deduct_tokens_no_user(self):
        """Test token deduction when user doesn't exist."""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.token_service.deduct_tokens(user_id=123, amount=50)
        assert result is None

    def test_deduct_tokens_exception(self):
        """Test token deduction with exception."""
        mock_user = MagicMock()
        mock_user.cyber_token_balance = 100
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_db.commit.side_effect = Exception("Database error")
        
        with patch('app.services.token_service.logger') as mock_logger:
            result = self.token_service.deduct_tokens(user_id=123, amount=50)
            assert result is None


# Pytest-style tests for integration scenarios
@pytest.fixture
def token_service_with_mocks():
    """Fixture for TokenService with mock dependencies."""
    mock_repo = MagicMock(spec=GameRepository)
    mock_db = MagicMock(spec=Session)
    service = TokenService(db=mock_db, repository=mock_repo)
    return service, mock_repo, mock_db


def test_token_service_full_flow(token_service_with_mocks):
    """Test a full flow of token operations."""
    service, mock_repo, mock_db = token_service_with_mocks

    # Setup mock user
    mock_user = MagicMock()
    mock_user.cyber_token_balance = 100
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    # Check initial balance
    balance = service.get_token_balance(user_id=123)
    assert balance == 100

    # Add tokens
    new_balance = service.add_tokens(user_id=123, amount=50)
    assert new_balance == 150
    assert mock_user.cyber_token_balance == 150

    # Deduct tokens
    new_balance = service.deduct_tokens(user_id=123, amount=25)
    assert new_balance == 125
    assert mock_user.cyber_token_balance == 125

    # Try to deduct more than available
    result = service.deduct_tokens(user_id=123, amount=999)
    assert result is None

    # Try to add negative tokens
    new_balance = service.add_tokens(user_id=123, amount=-50)
    assert new_balance == 75  # 125 - 50


def test_token_service_error_recovery(token_service_with_mocks):
    """Test error recovery in token operations."""
    service, mock_repo, mock_db = token_service_with_mocks

    # Setup mock user
    mock_user = MagicMock()
    mock_user.cyber_token_balance = 100
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    # Simulate commit error
    mock_db.commit.side_effect = Exception("Database error")

    # Try to add tokens - should fail and return fallback value
    with patch.object(service, 'get_token_balance', return_value=100):
        result = service.add_tokens(user_id=123, amount=50)
        assert result == 100  # Original balance

    # Try to deduct tokens - should fail and return None
    result = service.deduct_tokens(user_id=123, amount=50)
    assert result is None
