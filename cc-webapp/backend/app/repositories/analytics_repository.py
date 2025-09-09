"""
Analytics Repository - 분석 및 통계 관련 데이터 접근
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from .base_repository import BaseRepository
from app import models
import logging

logger = logging.getLogger(__name__)


class AnalyticsRepository(BaseRepository[models.UserAction]):
    """분석 및 통계 관련 Repository"""
    
    def __init__(self, db):
        super().__init__(db, models.UserAction)
    
    def get_daily_active_users(self, days: int = 7) -> List[dict]:
        """일일 활성 사용자 수 조회"""
        try:
            results = []
            for i in range(days):
                target_date = datetime.utcnow().date() - timedelta(days=i)
                
                # 해당 날짜의 활성 사용자 조회 (간소화된 버전)
                actions = self.db.query(models.UserAction)\
                    .filter(models.UserAction.created_at >= target_date)\
                    .filter(models.UserAction.created_at < target_date + timedelta(days=1))\
                    .all()
                
                unique_users = len(set(action.user_id for action in actions))
                
                results.append({
                    'date': target_date.isoformat(),
                    'active_users': unique_users
                })
            
            return results
        except Exception as e:
            logger.error(f"일일 활성 사용자 조회 실패: {e}")
            return []
    
    def get_game_statistics(self, days: int = 30) -> Dict[str, Any]:
        """게임 통계 조회"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # 게임 관련 액션들 조회
            actions = self.db.query(models.UserAction)\
                .filter(models.UserAction.created_at >= cutoff_date)\
                .filter(models.UserAction.action_type.in_(['SLOT_SPIN', 'ROULETTE_SPIN', 'RPS_PLAY', 'GACHA_SPIN']))\
                .all()
            
            # 게임별 플레이 횟수 계산
            game_plays = {}
            for action in actions:
                game_type = action.action_type
                game_plays[game_type] = game_plays.get(game_type, 0) + 1
            
            # 승률 계산
            win_rates = {}
            for game_type in ['SLOT_SPIN', 'ROULETTE_SPIN', 'RPS_PLAY']:
                game_actions = [a for a in actions if a.action_type == game_type]
                total_plays = len(game_actions)
                wins = len([a for a in game_actions if 'win' in (a.result or '')])
                
                win_rates[game_type] = {
                    'total_plays': total_plays,
                    'wins': wins,
                    'win_rate': round(wins / total_plays * 100, 2) if total_plays > 0 else 0
                }
            
            return {
                'game_plays': [{'game': game, 'count': count} for game, count in game_plays.items()],
                'win_rates': win_rates,
                'period_days': days
            }
        except Exception as e:
            logger.error(f"게임 통계 조회 실패: {e}")
            return {}
    
    def get_user_behavior_patterns(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """사용자 행동 패턴 분석"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            actions = self.db.query(models.UserAction)\
                .filter(models.UserAction.user_id == user_id)\
                .filter(models.UserAction.created_at >= cutoff_date)\
                .order_by(models.UserAction.created_at)\
                .all()
            
            if not actions:
                return {}
            
            # 시간대별 활동 패턴
            hourly_activity = {}
            for action in actions:
                hour = action.created_at.hour
                hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
            
            # 선호 게임 분석
            game_preferences = {}
            for action in actions:
                if action.action_type in ['SLOT_SPIN', 'ROULETTE_SPIN', 'RPS_PLAY', 'GACHA_SPIN']:
                    game_preferences[action.action_type] = game_preferences.get(action.action_type, 0) + 1
            
            # 세션 길이 분석
            sessions = self._calculate_sessions(actions)
            avg_session_length = sum(sessions) / len(sessions) if sessions else 0
            
            return {
                'total_actions': len(actions),
                'hourly_activity': hourly_activity,
                'game_preferences': game_preferences,
                'sessions': {
                    'count': len(sessions),
                    'average_length_minutes': round(avg_session_length, 2),
                    'total_time_minutes': sum(sessions)
                },
                'most_active_hour': max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else 0,
                'favorite_game': max(game_preferences.items(), key=lambda x: x[1])[0] if game_preferences else None
            }
        except Exception as e:
            logger.error(f"사용자 행동 패턴 분석 실패: {e}")
            return {}
    
    def _calculate_sessions(self, actions: List[models.UserAction]) -> List[float]:
        """세션 길이 계산 (분 단위)"""
        if len(actions) < 2:
            return []
        
        sessions = []
        session_start = actions[0].created_at
        last_action = actions[0].created_at
        
        for action in actions[1:]:
            time_gap = (action.created_at - last_action).total_seconds() / 60  # 분 단위
            
            if time_gap > 30:  # 30분 이상 간격이면 새 세션
                session_length = (last_action - session_start).total_seconds() / 60
                if session_length > 0:
                    sessions.append(session_length)
                session_start = action.created_at
            
            last_action = action.created_at
        
        # 마지막 세션 추가
        final_session = (last_action - session_start).total_seconds() / 60
        if final_session > 0:
            sessions.append(final_session)
        
        return sessions
    
    def get_retention_metrics(self, days: int = 30) -> Dict[str, Any]:
        """리텐션 지표 계산"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # 해당 기간의 모든 액션 조회
            actions = self.db.query(models.UserAction)\
                .filter(models.UserAction.created_at >= cutoff_date)\
                .all()
            
            # 사용자별 활동 일수 계산
            user_activity = {}
            for action in actions:
                user_id = action.user_id
                date_key = action.created_at.date()
                
                if user_id not in user_activity:
                    user_activity[user_id] = set()
                user_activity[user_id].add(date_key)
            
            new_users = len(user_activity)
            active_users = new_users
            returning_users = len([user_id for user_id, dates in user_activity.items() if len(dates) >= 2])
            
            return {
                'new_users': new_users,
                'active_users': active_users,
                'returning_users': returning_users,
                'retention_rate': round(returning_users / new_users * 100, 2) if new_users > 0 else 0,
                'period_days': days
            }
        except Exception as e:
            logger.error(f"리텐션 지표 계산 실패: {e}")
            return {}
    
    def get_revenue_analytics(self, days: int = 30) -> Dict[str, Any]:
        """수익 분석 (프리미엄 젬 기반)"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # 구매 관련 액션들 조회
            purchase_actions = self.db.query(models.UserAction)\
                .filter(models.UserAction.created_at >= cutoff_date)\
                .filter(models.UserAction.action_type.in_(['PURCHASE_GOLD', 'BUY_PACKAGE']))\
                .all()
            
            total_revenue = 0
            daily_revenue = {}
            
            for action in purchase_actions:
                amount = action.metadata.get('amount', 0) if action.metadata else 0
                total_revenue += amount
                
                date_key = action.created_at.date().isoformat()
                daily_revenue[date_key] = daily_revenue.get(date_key, 0) + amount
            
            return {
                'total_revenue': total_revenue,
                'daily_revenue': daily_revenue,
                'average_daily_revenue': total_revenue / days if days > 0 else 0,
                'period_days': days
            }
        except Exception as e:
            logger.error(f"수익 분석 실패: {e}")
            return {}
