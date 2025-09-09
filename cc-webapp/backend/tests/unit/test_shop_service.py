import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.services.shop_service import ShopService
from app.services.token_service import TokenService
from app.models import User, UserReward

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_token_service():
    return MagicMock(spec=TokenService)

@pytest.fixture
def shop_service(mock_db_session, mock_token_service):
    return ShopService(db=mock_db_session, token_service=mock_token_service)

@pytest.fixture
def mock_user():
    return User(id=1, cyber_token_balance=10000)

def test_purchase_item_success(shop_service, mock_db_session, mock_token_service, mock_user):
    """
    Test a successful item purchase.
    """
    # Arrange
    item_id = 101
    item_name = "Test Item"
    price = 5000
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    mock_token_service.get_token_balance.return_value = 10000 - price
    # Mock the count for the new item
    mock_db_session.query.return_value.filter.return_value.count.return_value = 1

    # Act
    result = shop_service.purchase_item(
        user_id=mock_user.id,
        item_id=item_id,
        item_name=item_name,
        price=price,
        description="A test item"
    )

    # Assert
    assert result["success"] is True
    assert result["new_balance"] == 5000
    assert result["new_item_count"] == 1
    mock_token_service.deduct_tokens.assert_called_once_with(mock_user.id, price)
    mock_db_session.add.assert_called_once()
    added_object = mock_db_session.add.call_args[0][0]
    assert isinstance(added_object, UserReward)
    assert added_object.reward_type == "SHOP_ITEM"
    mock_db_session.commit.assert_called_once()

def test_purchase_item_insufficient_funds(shop_service, mock_db_session, mock_token_service, mock_user):
    """
    Test a purchase attempt with insufficient funds.
    """
    # Arrange
    item_id = 101
    item_name = "Expensive Item"
    price = 20000 # More than the user's balance
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    # Act
    result = shop_service.purchase_item(
        user_id=mock_user.id,
        item_id=item_id,
        item_name=item_name,
        price=price,
        description="An expensive item"
    )

    # Assert
    assert result["success"] is False
    assert result["message"] == "토큰이 부족합니다."
    mock_token_service.deduct_tokens.assert_not_called()
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()
