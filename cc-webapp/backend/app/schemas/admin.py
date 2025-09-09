from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime

# User Activity schemas
class UserActivityBase(BaseModel):
    user_id: int
    activity_type: str
    description: Optional[str] = None

class UserActivityCreate(UserActivityBase):
    pass

class UserActivity(UserActivityBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

# Reward schemas
class RewardBase(BaseModel):
    user_id: int
    reward_type: str
    amount: float
    description: Optional[str] = None

class RewardCreate(RewardBase):
    pass

class Reward(RewardBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Admin dashboard schemas
class UserActivitySummary(BaseModel):
    total_activities: int
    activities_by_type: Dict[str, int]

class RewardSummary(BaseModel):
    total_rewards: int
    total_amount: float
    rewards_by_type: Dict[str, float]

class AdminDashboardData(BaseModel):
    user_activity: UserActivitySummary
    rewards: RewardSummary

class UserAdminResponse(BaseModel):
    id: int
    site_id: str
    nickname: str
    phone_number: str
    created_at: datetime
    cyber_token_balance: int
    rank: str
    model_config = ConfigDict(from_attributes=True)

class ActivityResponse(BaseModel):
    id: int
    activity_type: str
    timestamp: datetime
    details: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class UserDetailResponse(UserAdminResponse):
    activities: List[ActivityResponse]

class GiveRewardRequest(BaseModel):
    user_id: int
    amount: int
    reason: str

class RewardResponse(BaseModel):
    id: int
    user_id: int
    type: str
    amount: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
