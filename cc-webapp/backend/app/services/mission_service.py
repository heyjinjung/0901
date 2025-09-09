from sqlalchemy.orm import Session
from typing import List

from .. import models
from .reward_service import RewardService

class MissionService:
    def __init__(self, db: Session):
        self.db = db

    def list_user_missions(self, user_id: int) -> List[dict]:
        """
        Lists all active missions and the user's progress for each.
        """
        active_missions = self.db.query(models.Mission).filter(models.Mission.is_active == True).all()
        user_progress = self.db.query(models.UserMissionProgress).filter(models.UserMissionProgress.user_id == user_id).all()

        progress_map = {p.mission_id: p for p in user_progress}

        missions_with_progress = []
        for mission in active_missions:
            progress = progress_map.get(mission.id)
            missions_with_progress.append({
                "mission_id": mission.id,
                "title": mission.title,
                "description": mission.description,
                "target_count": mission.target_count,
                "reward_amount": mission.reward_amount,
                "current_count": progress.current_count if progress else 0,
                "is_completed": progress.is_completed if progress else False,
                "is_claimed": progress.is_claimed if progress else False,
            })
        return missions_with_progress

    def update_mission_progress(self, user_id: int, action_type: str):
        """
        Updates mission progress for a user based on an action they took.
        """
        # Find all active missions related to this action
        relevant_missions = self.db.query(models.Mission).filter(
            models.Mission.is_active == True,
            models.Mission.target_action == action_type
        ).all()

        for mission in relevant_missions:
            progress = self.db.query(models.UserMissionProgress).filter_by(user_id=user_id, mission_id=mission.id).first()
            if not progress:
                progress = models.UserMissionProgress(user_id=user_id, mission_id=mission.id)
                self.db.add(progress)

            if not progress.is_completed:
                progress.current_count += 1
                if progress.current_count >= mission.target_count:
                    progress.is_completed = True
                    progress.completed_at = datetime.utcnow()

        self.db.commit()

    def claim_reward(self, user_id: int, mission_id: int) -> models.UserReward:
        """
        Allows a user to claim the reward for a completed, unclaimed mission.
        """
        progress = self.db.query(models.UserMissionProgress).filter_by(user_id=user_id, mission_id=mission_id).first()

        if not progress or not progress.is_completed:
            raise ValueError("Mission not completed.")

        if progress.is_claimed:
            raise ValueError("Reward already claimed.")

        mission = self.db.query(models.Mission).filter_by(id=mission_id).one()

        reward_service = RewardService(self.db)
        user_reward = reward_service.distribute_reward(
            user_id=user_id,
            reward_type=mission.reward_type,
            amount=mission.reward_amount,
            source_description=f"Mission Complete: {mission.title}"
        )

        progress.is_claimed = True
        progress.claimed_at = datetime.utcnow()
        self.db.commit()

        return user_reward
