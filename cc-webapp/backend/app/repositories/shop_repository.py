"""
Shop Repository - 상점 관련 데이터 접근
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from .base_repository import BaseRepository
from app import models
import logging

logger = logging.getLogger(__name__)


class ShopRepository(BaseRepository[models.UserAction]):
    """상점 및 구매 관련 Repository
    
    Note: ShopTransaction 모델이 정의되어 있지 않으므로 
    UserAction을 사용하여 구매 관련 액션을 처리합니다.
    """
    
    def __init__(self, db):
        super().__init__(db, models.UserAction)
    
    def get_user_purchases(self, user_id: int, limit: int = 50) -> List[models.UserAction]:
        """사용자의 구매 내역 조회"""
        try:
            return self.db.query(models.UserAction)\
                .filter(models.UserAction.user_id == user_id)\
                .filter(models.UserAction.action_type.in_(['PURCHASE_GOLD', 'BUY_PACKAGE']))\
                .order_by(models.UserAction.created_at.desc())\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"사용자 구매 내역 조회 실패: {e}")
            return []
    
    def get_recent_purchases(self, hours: int = 24) -> List[models.UserAction]:
        """최근 구매 내역 조회"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            return self.db.query(models.UserAction)\
                .filter(models.UserAction.action_type.in_(['PURCHASE_GOLD', 'BUY_PACKAGE']))\
                .filter(models.UserAction.created_at >= cutoff_time)\
                .order_by(models.UserAction.created_at.desc())\
                .all()
        except Exception as e:
            logger.error(f"최근 구매 내역 조회 실패: {e}")
            return []
    
    def get_popular_items(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """인기 상품 조회"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # 구매 액션에서 상품별 구매 횟수 집계
            purchases = self.db.query(models.UserAction)\
                .filter(models.UserAction.action_type.in_(['PURCHASE_GOLD', 'BUY_PACKAGE']))\
                .filter(models.UserAction.created_at >= cutoff_date)\
                .all()
            
            # 상품별 구매 횟수 계산
            item_counts = {}
            for purchase in purchases:
                item_name = purchase.metadata.get('item_name', 'Unknown')
                item_counts[item_name] = item_counts.get(item_name, 0) + 1
            
            # 인기순으로 정렬
            popular_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
            
            return [
                {'item_name': item[0], 'purchase_count': item[1]}
                for item in popular_items[:limit]
            ]
        except Exception as e:
            logger.error(f"인기 상품 조회 실패: {e}")
            return []
    
    def get_user_spending_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """사용자 소비 통계"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            purchases = self.db.query(models.UserAction)\
                .filter(models.UserAction.user_id == user_id)\
                .filter(models.UserAction.action_type.in_(['PURCHASE_GOLD', 'BUY_PACKAGE']))\
                .filter(models.UserAction.created_at >= cutoff_date)\
                .all()
            
            total_spent = 0
            purchase_count = len(purchases)
            
            for purchase in purchases:
                amount = purchase.metadata.get('amount', 0)
                total_spent += amount
            
            return {
                'total_spent': total_spent,
                'purchase_count': purchase_count,
                'average_purchase': total_spent / purchase_count if purchase_count > 0 else 0,
                'period_days': days
            }
        except Exception as e:
            logger.error(f"사용자 소비 통계 조회 실패: {e}")
            return {}
    
    def record_purchase(self, user_id: int, item_name: str, amount: float,
                       gold_received: int = 0, metadata: Optional[Dict] = None) -> models.UserAction:
        """구매 기록"""
        try:
            purchase_metadata = {
                'item_name': item_name,
                'amount': amount,
                'gold_received': gold_received,
                **(metadata or {})
            }
            
            purchase_action = models.UserAction(
                user_id=user_id,
                action_type='PURCHASE_GOLD' if gold_received > 0 else 'BUY_PACKAGE',
                result='success',
                points_earned=0,
                metadata=purchase_metadata
            )
            
            self.db.add(purchase_action)
            self.db.commit()
            self.db.refresh(purchase_action)
            
            return purchase_action
        except Exception as e:
            logger.error(f"구매 기록 실패: {e}")
            self.db.rollback()
            raise
    
    def get_revenue_by_period(self, days: int = 30) -> Dict[str, Any]:
        """기간별 수익 분석"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            purchases = self.db.query(models.UserAction)\
                .filter(models.UserAction.action_type.in_(['PURCHASE_GOLD', 'BUY_PACKAGE']))\
                .filter(models.UserAction.created_at >= cutoff_date)\
                .all()
            
            daily_revenue = {}
            total_revenue = 0
            
            for purchase in purchases:
                date_key = purchase.created_at.date().isoformat()
                amount = purchase.metadata.get('amount', 0)
                
                daily_revenue[date_key] = daily_revenue.get(date_key, 0) + amount
                total_revenue += amount
            
            return {
                'total_revenue': total_revenue,
                'daily_revenue': daily_revenue,
                'average_daily_revenue': total_revenue / days if days > 0 else 0,
                'period_days': days
            }
        except Exception as e:
            logger.error(f"수익 분석 실패: {e}")
            return {}
    
    def get_top_spenders(self, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """최고 소비자 조회"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            purchases = self.db.query(models.UserAction)\
                .filter(models.UserAction.action_type.in_(['PURCHASE_GOLD', 'BUY_PACKAGE']))\
                .filter(models.UserAction.created_at >= cutoff_date)\
                .all()
            
            user_spending = {}
            for purchase in purchases:
                user_id = purchase.user_id
                amount = purchase.metadata.get('amount', 0)
                
                if user_id not in user_spending:
                    user_spending[user_id] = {'total_spent': 0, 'purchase_count': 0}
                
                user_spending[user_id]['total_spent'] += amount
                user_spending[user_id]['purchase_count'] += 1
            
            # 소비금액 기준 정렬
            top_spenders = sorted(
                [(user_id, data) for user_id, data in user_spending.items()],
                key=lambda x: x[1]['total_spent'],
                reverse=True
            )[:limit]
            
            return [
                {
                    'user_id': user_id,
                    'total_spent': data['total_spent'],
                    'purchase_count': data['purchase_count']
                }
                for user_id, data in top_spenders
            ]
        except Exception as e:
            logger.error(f"최고 소비자 조회 실패: {e}")
            return []
