# 파일 위치: c:\Users\bdbd\Downloads\auto202506-a-main\auto202506-a-main\cc-webapp\backend\app\schemas\user.py
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    site_id: str
    nickname: str
    phone_number: str

class UserCreate(UserBase):
    password: str
    invite_code: str

# Add UserRegister schema for registration endpoints
class UserRegister(BaseModel):
    site_id: str
    nickname: str
    phone_number: str
    password: str
    invite_code: str

class UserLogin(BaseModel):
    site_id: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

# Add UserResponse for API responses
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    site_id: str
    nickname: str
    phone_number: str
    cyber_token_balance: int
    created_at: datetime
    is_active: bool
    is_admin: bool
    # rank를 Optional로 변경
    rank: Optional[str] = "STANDARD"

class PublicUserResponse(BaseModel):
    """타인 보기용 제한 정보 스키마"""
    id: int
    site_id: str
    nickname: str
    phone_number: str = "hidden"
    cyber_token_balance: int = 0
    created_at: Optional[datetime] = None
    is_active: bool = True
    is_admin: bool = False
    rank: Optional[str] = "STANDARD"

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    invite_code: str
    cyber_token_balance: int
    created_at: datetime
    # rank를 Optional로 변경
    rank: Optional[str] = "STANDARD"

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    rank: Optional[str] = None

class UserUpdateRequest(BaseModel):
    """사용자 프로필 업데이트 요청 모델"""
    nickname: Optional[str] = None
    phone_number: Optional[str] = None

class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    site_id: str
    nickname: str
    phone_number: str
    cyber_token_balance: int
    is_active: bool
    is_admin: bool
    # invite_code와 created_at, rank를 Optional로 변경
    invite_code: Optional[str] = None
    created_at: Optional[datetime] = None
    rank: Optional[str] = "STANDARD"
    total_spent: Optional[float] = 0.0
    vip_tier: Optional[str] = "STANDARD"
    battlepass_level: Optional[int] = 1

class UserProgressResponse(BaseModel):
    """사용자 진행상황 응답 모델"""
    user_id: int
    level: int
    experience: int
    next_level_exp: int
    progress_percentage: float

class UserStatisticsResponse(BaseModel):
    """사용자 통계 응답 모델"""
    user_id: int
    total_games_played: int
    total_spent: float
    total_earned: int
    win_rate: float
    favorite_game: Optional[str] = None

class UserSegmentResponse(BaseModel):
    """사용자 세그먼트 응답 모델"""
    user_id: int
    segment: str
    last_updated: datetime
