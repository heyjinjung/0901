import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ..models.auth_models import User
from ..models.game_models import UserAction, Game
from ..models.user_models import UserSegment

logger = logging.getLogger(__name__)

# Define RFM thresholds
RECENCY_THRESHOLDS = {'high': 7, 'mid': 30}
FREQUENCY_THRESHOLDS = {'high': 50, 'mid': 10} # Adjusted for more actions
MONETARY_THRESHOLDS = {'high': 500000, 'mid': 100000} # Adjusted for coin values

class RFMService:
    """Service for calculating and managing RFM metrics."""

    def __init__(self, db: Session):
        self.db = db

    def _get_rfm_score(self, value, thresholds, higher_is_better=True):
        if higher_is_better:
            if value >= thresholds['high']: return 5
            if value >= thresholds['mid']: return 3
            return 1
        else: # lower is better (like recency)
            if value <= thresholds['high']: return 5
            if value <= thresholds['mid']: return 3
            return 1

    def update_all_user_segments(self):
        """
        Calculates RFM scores for all users and updates their segments in the database.
        """
        print(f"[{datetime.utcnow()}] Starting RFM computation for all users...")
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        users = self.db.query(User).all()
        if not users:
            print("No users found to process.")
            return

        updated_count = 0
        created_count = 0

        for user in users:
            user_id = user.id

            # Calculate Recency and Frequency from user_actions
            action_stats = self.db.query(
                func.max(UserAction.created_at).label("last_action_date"),
                func.count(UserAction.id).label("frequency")
            ).filter(
                UserAction.user_id == user_id,
                UserAction.created_at >= thirty_days_ago
            ).first()

            last_action_date = action_stats.last_action_date
            frequency = action_stats.frequency or 0
            recency_days = (datetime.utcnow() - last_action_date).days if last_action_date else 999

            # Calculate Monetary value from the games table
            monetary_stats = self.db.query(
                func.sum(Game.bet_amount).label("monetary_value")
            ).filter(
                Game.user_id == user_id,
                Game.created_at >= thirty_days_ago
            ).first()
            monetary_value = monetary_stats.monetary_value or 0.0

            r_score = self._get_rfm_score(recency_days, RECENCY_THRESHOLDS, higher_is_better=False)
            f_score = self._get_rfm_score(frequency, FREQUENCY_THRESHOLDS)
            m_score = self._get_rfm_score(monetary_value, MONETARY_THRESHOLDS)

            # Simplified RFM group assignment
            if r_score >= 4 and f_score >= 4 and m_score >= 4:
                rfm_group = "Whale"
            elif (r_score + f_score + m_score) / 3 >= 3:
                rfm_group = "High-Value"
            elif (r_score + f_score + m_score) / 3 >= 2:
                rfm_group = "Medium-Value"
            elif r_score < 2:
                rfm_group = "At-Risk"
            else:
                rfm_group = "Low-Value"

            # Update or Create UserSegment
            user_segment = self.db.query(UserSegment).filter(UserSegment.user_id == user_id).first()
            current_time = datetime.utcnow()
            if user_segment:
                user_segment.rfm_group = rfm_group
                user_segment.last_updated = current_time
                updated_count += 1
            else:
                user_segment = UserSegment(
                    user_id=user_id,
                    rfm_group=rfm_group,
                    last_updated=current_time,
                )
                self.db.add(user_segment)
                created_count += 1

        try:
            self.db.commit()
            print(f"[{datetime.utcnow()}] User segments updated: {updated_count} updated, {created_count} created.")
        except Exception as e:
            self.db.rollback()
            print(f"[{datetime.utcnow()}] Error updating user segments: {e}")
            raise e
