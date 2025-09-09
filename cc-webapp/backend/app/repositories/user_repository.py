#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
👤 UserRepository: 사용자 데이터 액세스 레이어
사용자 관련 모든 DB 작업을 담당합니다.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
import logging

from .base_repository import BaseRepository
from .. import models

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository[models.User]):
    """사용자 데이터 액세스 리포지토리"""

    def __init__(self, db: Session):
        super().__init__(db, models.User)

    def get_by_email(self, email: str) -> Optional[models.User]:
        """이메일로 사용자 조회"""
        try:
            return self.db.query(models.User).filter(
                models.User.email == email
            ).first()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None

    def get_by_nickname(self, nickname: str) -> Optional[models.User]:
        """닉네임으로 사용자 조회"""
        try:
            return self.db.query(models.User).filter(
                models.User.nickname == nickname
            ).first()
        except Exception as e:
            logger.error(f"Error getting user by nickname {nickname}: {e}")
            return None

    def get_active_users(self, days: int = 7) -> List[models.User]:
        """최근 활성 사용자 조회"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            return self.db.query(models.User).filter(
                models.User.last_login >= cutoff_date
            ).all()
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []

    def get_users_by_vip_tier(self, vip_tier: str) -> List[models.User]:
        """VIP 등급별 사용자 조회"""
        try:
            return self.db.query(models.User).filter(
                models.User.vip_tier == vip_tier
            ).all()
        except Exception as e:
            logger.error(f"Error getting users by VIP tier {vip_tier}: {e}")
            return []

    def update_last_login(self, user_id: int) -> bool:
        """마지막 로그인 시간 업데이트"""
        try:
            user = self.get_by_id(user_id)
            if user:
                user.last_login = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {e}")
            self.db.rollback()
            return False

    def increment_login_count(self, user_id: int) -> bool:
        """로그인 횟수 증가"""
        try:
            user = self.get_by_id(user_id)
            if user:
                if hasattr(user, 'login_count'):
                    user.login_count += 1
                else:
                    user.login_count = 1
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error incrementing login count for user {user_id}: {e}")
            self.db.rollback()
            return False

    def get_user_statistics(self, user_id: int) -> dict:
        """사용자 통계 조회"""
        try:
            user = self.get_by_id(user_id)
            if not user:
                return {}

            # 기본 통계 정보
            stats = {
                'user_id': user_id,
                'created_at': user.created_at,
                'last_login': user.last_login,
                'vip_tier': user.vip_tier,
                'battlepass_level': user.battlepass_level,
                'total_spent': user.total_spent,
            }

            # 추가 통계 (UserAction 테이블에서)
            action_count = self.db.query(func.count(models.UserAction.id)).filter(
                models.UserAction.user_id == user_id
            ).scalar()
            stats['total_actions'] = action_count or 0

            # 보상 통계 (UserReward 테이블에서)
            reward_count = self.db.query(func.count(models.UserReward.id)).filter(
                models.UserReward.user_id == user_id
            ).scalar()
            stats['total_rewards'] = reward_count or 0

            return stats
        except Exception as e:
            logger.error(f"Error getting user statistics for user {user_id}: {e}")
            return {}

    def search_users(self, query: str, limit: int = 50) -> List[models.User]:
        """사용자 검색 (닉네임, 이메일)"""
        try:
            search_pattern = f"%{query}%"
            return self.db.query(models.User).filter(
                models.User.nickname.ilike(search_pattern) |
                models.User.email.ilike(search_pattern)
            ).limit(limit).all()
        except Exception as e:
            logger.error(f"Error searching users with query {query}: {e}")
            return []

    def get_users_by_creation_date(self, start_date: datetime, end_date: datetime) -> List[models.User]:
        """생성일 범위로 사용자 조회"""
        try:
            return self.db.query(models.User).filter(
                and_(
                    models.User.created_at >= start_date,
                    models.User.created_at <= end_date
                )
            ).all()
        except Exception as e:
            logger.error(f"Error getting users by creation date: {e}")
            return []

    def update_vip_tier(self, user_id: int, new_tier: str) -> bool:
        """VIP 등급 업데이트"""
        try:
            user = self.get_by_id(user_id)
            if user:
                user.vip_tier = new_tier
                user.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating VIP tier for user {user_id}: {e}")
            self.db.rollback()
            return False

    def update_battlepass_level(self, user_id: int, new_level: int) -> bool:
        """배틀패스 레벨 업데이트"""
        try:
            user = self.get_by_id(user_id)
            if user:
                user.battlepass_level = new_level
                user.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating battlepass level for user {user_id}: {e}")
            self.db.rollback()
            return False
