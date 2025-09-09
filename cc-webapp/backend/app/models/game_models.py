"""게임 관련 데이터베이스 모델"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from ..database import Base


class Game(Base):
    """게임 모델

    테스트 코드 및 서비스 레이어(roulette/slot 등)가 다음 형태의 생성자를 사용:
        Game(user_id=..., game_type=..., bet_amount=..., payout=..., result=...)
    과거 스키마는 name(unique, not null)을 강제했으나 실제 사용 시 name 미지정으로
    에러가 발생했으므로 name 을 nullable 로 완화하고 기본적으로 game_type 기반
    메타 데이터만 저장하도록 조정.
    """
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=True, unique=True)  # 선택적; NULL 허용
    description = Column(Text)
    game_type = Column(String(50), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # 집계/호환 필드
    bet_amount = Column(Integer, default=0)
    payout = Column(Integer, default=0)
    result = Column(String(100))  # 최근 결과(예: prize id, win/lose 등)


class UserAction(Base):
    """사용자 액션 모델"""
    __tablename__ = "user_actions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String(50), nullable=False)
    action_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    user = relationship("User", back_populates="actions")


class UserReward(Base):
    """사용자 보상 모델"""
    __tablename__ = "user_rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # 기존 reward_id 기반 레거시 관계 (선택적) - 일부 경로는 직접 reward 객체 참조
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=True)
    claimed_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)
    # 확장 필드 (streak / economy 멱등 처리용)
    reward_type = Column(String(50), nullable=True, index=True)  # 예: STREAK_DAILY, GACHA_PULL 등
    gold_amount = Column(Integer, nullable=True)
    xp_amount = Column(Integer, nullable=True)
    reward_metadata = Column(JSON, nullable=True)
    idempotency_key = Column(String(120), nullable=True, unique=True, index=True)
    
    # 관계
    user = relationship("User", back_populates="rewards")
    reward = relationship("Reward", back_populates="user_rewards")


class GameSession(Base):
    """게임 세션 모델 (리팩터: 내부 int PK + 외부 UUID)"""
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    external_session_id = Column(String(36), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    game_type = Column(String(50), nullable=False, index=True)
    initial_bet = Column(Integer, nullable=False, default=0)
    total_win = Column(Integer, nullable=False, default=0)
    total_bet = Column(Integer, nullable=False, default=0)
    total_rounds = Column(Integer, nullable=False, default=0)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), default="active", nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    result_data = Column(JSON)
    
    user = relationship("User", back_populates="game_sessions")


class GameStats(Base):
    __tablename__ = "game_stats"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    game_type = Column(String, nullable=False)
    total_games = Column(Integer, default=0)
    total_wins = Column(Integer, default=0)
    total_losses = Column(Integer, default=0)
    total_bet = Column(Integer, default=0)
    total_won = Column(Integer, default=0)
    best_score = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    last_played = Column(DateTime)
    
    user = relationship("User", back_populates="game_stats")


class DailyGameLimit(Base):
    __tablename__ = "daily_game_limits"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    game_type = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    play_count = Column(Integer, default=0)
    max_plays = Column(Integer, nullable=False)
    
    user = relationship("User", back_populates="daily_limits")


class UserActivity(Base):
    """사용자 활동 모델"""
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)
    activity_date = Column(DateTime, default=datetime.utcnow)
    activity_data = Column(Text)
    points_earned = Column(Integer, default=0)
    
    # 관계
    user = relationship("User", back_populates="activities")


class Reward(Base):
    """보상 모델"""
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    reward_type = Column(String(50), nullable=False)
    value = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    user_rewards = relationship("UserReward", back_populates="reward")


class GachaResult(Base):
    """가챠 결과 모델"""
    __tablename__ = "gacha_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    gacha_type = Column(String(50), nullable=False)
    result_data = Column(Text)
    rarity = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    user = relationship("User", back_populates="gacha_results")


class UserProgress(Base):
    """사용자 진행도 모델"""
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    progress_type = Column(String(50), nullable=False)
    current_value = Column(Integer, default=0)
    max_value = Column(Integer, default=100)
    is_completed = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    user = relationship("User", back_populates="progress")
