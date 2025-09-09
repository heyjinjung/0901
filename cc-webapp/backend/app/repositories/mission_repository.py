"""
Mission Repository - 미션 및 퀘스트 관련 데이터 접근
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta

from .base_repository import BaseRepository
from app import models
import logging

logger = logging.getLogger(__name__)


class MissionRepository(BaseRepository[models.UserAction]):
    """미션 및 퀘스트 관련 Repository"""
    
    def __init__(self, db: Session):
        super().__init__(db, models.UserAction)
    
    def get_user_missions(self, user_id: int) -> List[models.UserAction]:
        """사용자의 미션 진행 상황 조회"""
        try:
            return self.db.query(models.UserAction)\
                .filter(models.UserAction.user_id == user_id)\
                .filter(models.UserAction.action_type.in_(['MISSION_START', 'MISSION_COMPLETE']))\
                .order_by(desc(models.UserAction.created_at))\
                .all()
        except Exception as e:
            logger.error(f"사용자 미션 조회 실패 (user_id: {user_id}): {e}")
            return []
    
    def get_daily_missions(self, user_id: int) -> List[dict]:
        """일일 미션 진행 상황"""
        try:
            today = datetime.utcnow().date()
            actions = self.db.query(models.UserAction)\
                .filter(models.UserAction.user_id == user_id)\
                .filter(func.date(models.UserAction.created_at) == today)\
                .all()
            
            # 일일 미션 통계 계산
            slot_actions = [a for a in actions if str(a.action_type) == 'SLOT_SPIN']
            game_actions = [a for a in actions if str(a.action_type) in ['SLOT_SPIN', 'ROULETTE_SPIN', 'RPS_PLAY']]
            win_actions = [a for a in actions if a.result and 'win' in str(a.result).lower()]
            login_actions = [a for a in actions if str(a.action_type) == 'USER_LOGIN']
            
            missions = {
                'daily_spins': len(slot_actions),
                'daily_games': len(game_actions),
                'daily_wins': len(win_actions),
                'daily_login': len(login_actions) > 0
            }
            
            return [
                {'mission_type': 'daily_spins', 'progress': missions['daily_spins'], 'target': 10, 'completed': missions['daily_spins'] >= 10},
                {'mission_type': 'daily_games', 'progress': missions['daily_games'], 'target': 5, 'completed': missions['daily_games'] >= 5},
                {'mission_type': 'daily_wins', 'progress': missions['daily_wins'], 'target': 3, 'completed': missions['daily_wins'] >= 3},
                {'mission_type': 'daily_login', 'progress': 1 if missions['daily_login'] else 0, 'target': 1, 'completed': missions['daily_login']}
            ]
        except Exception as e:
            logger.error(f"일일 미션 조회 실패: {e}")
            return []
    
    def get_weekly_missions(self, user_id: int) -> List[dict]:
        """주간 미션 진행 상황"""
        try:
            week_start = datetime.utcnow() - timedelta(days=7)
            actions = self.db.query(models.UserAction)\
                .filter(models.UserAction.user_id == user_id)\
                .filter(models.UserAction.created_at >= week_start)\
                .all()
            
            missions = {
                'weekly_spins': len([a for a in actions if str(a.action_type) == 'SLOT_SPIN']),
                'weekly_games': len([a for a in actions if str(a.action_type) in ['SLOT_SPIN', 'ROULETTE_SPIN', 'RPS_PLAY']]),
                'weekly_wins': len([a for a in actions if a.result and 'win' in str(a.result).lower()]),
                'weekly_streaks': self._calculate_win_streaks(actions)
            }
            
            return [
                {'mission_type': 'weekly_spins', 'progress': missions['weekly_spins'], 'target': 50, 'completed': missions['weekly_spins'] >= 50},
                {'mission_type': 'weekly_games', 'progress': missions['weekly_games'], 'target': 30, 'completed': missions['weekly_games'] >= 30},
                {'mission_type': 'weekly_wins', 'progress': missions['weekly_wins'], 'target': 15, 'completed': missions['weekly_wins'] >= 15},
                {'mission_type': 'weekly_streaks', 'progress': missions['weekly_streaks'], 'target': 5, 'completed': missions['weekly_streaks'] >= 5}
            ]
        except Exception as e:
            logger.error(f"주간 미션 조회 실패: {e}")
            return []
    
    def _calculate_win_streaks(self, actions: List[models.UserAction]) -> int:
        """연승 계산"""
        win_actions = [a for a in actions if a.result and 'win' in str(a.result).lower()]
        if not win_actions:
            return 0
        
        # 연속된 승리 중 최대 연승 계산
        max_streak = 0
        current_streak = 0
        
        # Sort by created_at timestamp - handle None values safely
        try:
            sorted_actions = sorted(win_actions, key=lambda x: getattr(x, 'created_at', datetime.utcnow()))
        except Exception:
            # Fallback to unsorted if sorting fails
            sorted_actions = win_actions
        
        for action in sorted_actions:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        
        return max_streak
    
    def complete_mission(self, user_id: int, mission_type: str, reward_data: dict) -> Optional[models.UserAction]:
        """미션 완료 처리"""
        try:
            mission_action = models.UserAction(
                user_id=user_id,
                action_type='MISSION_COMPLETE',
                result=f"Completed {mission_type}",
                metadata={'mission_type': mission_type, 'reward': reward_data}
            )
            
            self.db.add(mission_action)
            self.db.commit()
            self.db.refresh(mission_action)
            
            logger.info(f"미션 완료: user_id={user_id}, mission_type={mission_type}")
            return mission_action
            
        except Exception as e:
            logger.error(f"미션 완료 처리 실패: {e}")
            self.db.rollback()
            return None
    
    def get_mission_completion_stats(self, days: int = 30) -> dict:
        """미션 완료 통계"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            completions = self.db.query(models.UserAction)\
                .filter(models.UserAction.action_type == 'MISSION_COMPLETE')\
                .filter(models.UserAction.created_at >= cutoff_date)\
                .all()
            
            stats = {}
            for completion in completions:
                mission_type = completion.metadata.get('mission_type', 'unknown')
                stats[mission_type] = stats.get(mission_type, 0) + 1
            
            return stats
        except Exception as e:
            logger.error(f"미션 완료 통계 조회 실패: {e}")
            return {}
