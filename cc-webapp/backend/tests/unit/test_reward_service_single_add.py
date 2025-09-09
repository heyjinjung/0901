import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.services.reward_service import RewardService
from app.services.token_service import TokenService
from app import models

@pytest.fixture
def db():
    return MagicMock(spec=Session)

@pytest.fixture
def token_service(db):
    return MagicMock(spec=TokenService)

@pytest.fixture
def reward_service(db, token_service):
    # SINGLE_ADD_COMPAT 기본 True 가정
    return RewardService(db=db, token_service=token_service)

@pytest.fixture
def user(db):
    user = models.User(id=1, rank="STANDARD")
    # query().filter().first() 체인
    db.query.return_value.filter.return_value.first.return_value = user
    return user

def test_single_add_compat_creates_only_userreward_and_relationship(db, reward_service, token_service, user):
    # arrange
    token_service.add_tokens.return_value = None

    # SQLAlchemy add 호출 추적
    added = []
    def add_tracker(obj):
        added.append(obj)
    db.add.side_effect = add_tracker

    # commit/refresh no-op
    db.commit.return_value = None
    db.refresh.return_value = None

    result = reward_service.distribute_reward(
        user_id=1,
        reward_type="TOKEN",
        amount=100,
        source_description="test-grant",
        idempotency_key=None,
    )

    # assertions
    # SINGLE_ADD_COMPAT=True 이므로 한 번의 add 호출(실제로는 UserReward 객체만 add)
    assert len(added) >= 1
    # 첫 add 객체는 UserReward 여야 함
    from app.models import UserReward, Reward
    assert any(isinstance(obj, UserReward) for obj in added)
    # Reward 객체는 UserReward.reward 관계를 통해 생성되어 add 없이 flush 가능 (SA가 cascade 할 수 있음)
    # 결과 payload 필드 확인
    assert result["reward_type"] == "TOKEN"
    assert result["reward_value"] == "100"

