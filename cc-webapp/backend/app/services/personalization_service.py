"""Personalization service for user recommendations and caching."""

import json
import logging
from typing import Dict, List

from sqlalchemy.orm import Session

from app.repositories.game_repository import GameRepository

logger = logging.getLogger(__name__)


class PersonalizationService:
    """Service for managing personalized user recommendations."""

    def __init__(self, db: Session, repository: GameRepository):
        """
        Initialize personalization service with database session and game repository.

        Args:
            db (Session): SQLAlchemy database session
            repository (GameRepository): Game data repository
        """
        self.db = db
        self.repository = repository

    async def cache_recommendations(self, user_id: int, recs: List[Dict]) -> None:
        """
        Cache recommendations for a user.

        Args:
            user_id (int): User's unique identifier
            recs (List[Dict]): List of recommendation dictionaries
        """
        try:
            # Store recommendations in user's game repository
            self.repository.set_gacha_history(user_id, [json.dumps(rec) for rec in recs])
        except Exception as exc:
            logger.error(f"Failed to cache recommendations for user {user_id}: {exc}")

    async def get_recommendations(self, user_id: int) -> List[Dict]:
        """
        Retrieve cached recommendations for a user.

        Args:
            user_id (int): User's unique identifier

        Returns:
            List[Dict]: Cached recommendations or empty list if not found
        """
        try:
            cached_history = self.repository.get_gacha_history(user_id)
            if cached_history:
                return [json.loads(rec) for rec in cached_history]
            return []
        except Exception as exc:
            logger.error(f"Failed to retrieve recommendations for user {user_id}: {exc}")
            return []

    async def generate_recommendations(self, user_id: int) -> List[Dict]:
        """
        Generate personalized recommendations for a user.

        Args:
            user_id (int): User's unique identifier

        Returns:
            List[Dict]: Generated recommendations
        """
        try:
            # Implement recommendation generation logic
            # This is a placeholder implementation
            recommendations = [
                {
                    "type": "game",
                    "id": "roulette",
                    "score": 0.8,
                    "reason": "High engagement history"
                },
                {
                    "type": "content",
                    "id": "adult_content",
                    "score": 0.6,
                    "reason": "Potential interest based on past interactions"
                }
            ]

            await self.cache_recommendations(user_id, recommendations)
            return recommendations
        except Exception as exc:
            logger.error(f"Recommendation generation failed for user {user_id}: {exc}")
            return []
