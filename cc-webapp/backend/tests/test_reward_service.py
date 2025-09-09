import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError # For testing commit failure

from app.services.reward_service import RewardService
from app.models import UserReward

class TestRewardService(unittest.TestCase):

    def setUp(self):
        self.mock_db_session = MagicMock(spec=Session)
        self.reward_service = RewardService(db=self.mock_db_session)

    def test_grant_content_unlock_success(self):
        user_id = 1
        content_id = 101
        stage_name = "Full"
        source_description = "Test unlock"

        # Act
        returned_reward = self.reward_service.grant_content_unlock(
            user_id=user_id,
            content_id=content_id,
            stage_name=stage_name,
            source_description=source_description
        )

        # Assert
        self.mock_db_session.add.assert_called_once()
        added_object = self.mock_db_session.add.call_args[0][0]

        self.assertIsInstance(added_object, UserReward)
        self.assertEqual(added_object.user_id, user_id)
        # UserReward model does not have a direct content_id field.
        # It's embedded in reward_value.
        self.assertEqual(added_object.reward_type, "CONTENT_UNLOCK")
        self.assertEqual(added_object.reward_value, f"{content_id}_{stage_name}")
        self.assertEqual(added_object.source_description, source_description)
        self.assertIsInstance(added_object.awarded_at, datetime)
        self.assertLess((datetime.utcnow().replace(tzinfo=timezone.utc) - added_object.awarded_at.replace(tzinfo=timezone.utc)).total_seconds(), 5) # Check it's recent

        self.mock_db_session.commit.assert_called_once()
        self.mock_db_session.refresh.assert_called_once_with(added_object)
        self.assertEqual(returned_reward, added_object)

    def test_grant_content_unlock_with_custom_awarded_at(self):
        user_id = 2
        content_id = 102
        stage_name = "Partial"
        source_description = "Test custom time"
        custom_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Act
        returned_reward = self.reward_service.grant_content_unlock(
            user_id=user_id,
            content_id=content_id,
            stage_name=stage_name,
            source_description=source_description,
            awarded_at=custom_time
        )

        # Assert
        self.mock_db_session.add.assert_called_once()
        added_object = self.mock_db_session.add.call_args[0][0]

        self.assertIsInstance(added_object, UserReward)
        self.assertEqual(added_object.user_id, user_id)
        self.assertEqual(added_object.reward_type, "CONTENT_UNLOCK")
        self.assertEqual(added_object.reward_value, f"{content_id}_{stage_name}")
        self.assertEqual(added_object.source_description, source_description)
        self.assertEqual(added_object.awarded_at, custom_time)

        self.mock_db_session.commit.assert_called_once()
        self.mock_db_session.refresh.assert_called_once_with(added_object)
        self.assertEqual(returned_reward, added_object)

    def test_grant_content_unlock_db_commit_fails(self):
        user_id = 3
        content_id = 103
        stage_name = "Teaser"
        source_description = "Test commit failure"

        # Configure the mock to raise an IntegrityError on commit
        self.mock_db_session.commit.side_effect = IntegrityError("Simulated DB error", params=None, orig=None)

        # Act & Assert
        with self.assertRaises(IntegrityError): # Assuming service re-raises or doesn't catch IntegrityError
            self.reward_service.grant_content_unlock(
                user_id=user_id,
                content_id=content_id,
                stage_name=stage_name,
                source_description=source_description
            )

        self.mock_db_session.add.assert_called_once() # Still should try to add
        self.mock_db_session.commit.assert_called_once() # Commit was attempted
        self.mock_db_session.rollback.assert_called_once() # Rollback should be called by service if commit fails
        self.mock_db_session.refresh.assert_not_called() # Refresh should not be called if commit fails

if __name__ == '__main__':
    unittest.main()
