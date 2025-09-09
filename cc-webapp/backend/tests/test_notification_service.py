# cc-webapp/backend/tests/test_notification_service.py
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta # Added timedelta for time comparison
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.services.notification_service import NotificationService
from app.models import Notification

class TestNotificationService(unittest.TestCase):

    def setUp(self):
        self.mock_db_session = MagicMock(spec=Session)
        self.notification_service = NotificationService(db=self.mock_db_session)

    def test_get_oldest_pending_notification_exists(self):
        # Arrange
        user_id = 1
        mock_notification = Notification(
            id=1,
            user_id=user_id,
            message="Hello",
            is_sent=False,
            created_at=datetime.now(timezone.utc) - timedelta(minutes=1)
        )

        # Configure the query chain to return the mock_notification
        mock_query = self.mock_db_session.query(Notification)
        mock_filter = mock_query.filter()
        mock_order_by = mock_filter.order_by()
        mock_order_by.first.return_value = mock_notification

        # Act
        result = self.notification_service.get_oldest_pending_notification(user_id=user_id)

        # Assert
        self.assertTrue(mock_notification.is_sent)
        self.assertIsNotNone(mock_notification.sent_at)
        self.assertIsInstance(mock_notification.sent_at, datetime)
        
        # Handle timezone-aware comparison
        sent_at = mock_notification.sent_at
        if sent_at.tzinfo is None:
            sent_at = sent_at.replace(tzinfo=timezone.utc)
        
        time_diff = (datetime.now(timezone.utc) - sent_at).total_seconds()
        self.assertLess(time_diff, 10)

        self.mock_db_session.commit.assert_called_once()
        self.mock_db_session.refresh.assert_called_once_with(mock_notification)
        self.assertEqual(result, mock_notification)

    def test_get_oldest_pending_notification_none_exists(self):
        # Arrange
        user_id = 1
        # Configure the query chain to return None
        mock_query = self.mock_db_session.query(Notification)
        mock_filter = mock_query.filter()
        mock_order_by = mock_filter.order_by()
        mock_order_by.first.return_value = None

        # Act
        result = self.notification_service.get_oldest_pending_notification(user_id=user_id)

        # Assert
        self.mock_db_session.commit.assert_not_called()
        self.mock_db_session.refresh.assert_not_called()
        self.assertIsNone(result)

    def test_get_oldest_pending_notification_commit_fails(self):
        # Arrange
        user_id = 1
        mock_notification = Notification(id=1, user_id=user_id, message="Hello", is_sent=False, created_at=datetime.now(timezone.utc))

        mock_query = self.mock_db_session.query(Notification)
        mock_filter = mock_query.filter()
        mock_order_by = mock_filter.order_by()
        mock_order_by.first.return_value = mock_notification

        self.mock_db_session.commit.side_effect = SQLAlchemyError("Commit failed")

        # Act & Assert
        with self.assertRaises(SQLAlchemyError): # Service should re-raise the original SQLAlchemyError
            self.notification_service.get_oldest_pending_notification(user_id=user_id)

        self.mock_db_session.rollback.assert_called_once()
        self.mock_db_session.refresh.assert_not_called()

    def test_create_notification_success(self):
        # Arrange
        user_id = 1
        message = "New notification"

        # Act
        returned_notification = self.notification_service.create_notification(user_id, message)

        # Assert
        self.mock_db_session.add.assert_called_once()
        added_object = self.mock_db_session.add.call_args[0][0]

        self.assertIsInstance(added_object, Notification)
        self.assertEqual(added_object.user_id, user_id)
        self.assertEqual(added_object.message, message)
        self.assertFalse(added_object.is_sent)
        self.assertIsNone(added_object.sent_at)
        self.assertIsInstance(added_object.created_at, datetime)
        
        # Handle timezone-aware comparison
        created_at = added_object.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        
        time_diff = (datetime.now(timezone.utc) - created_at).total_seconds()
        self.assertLess(time_diff, 10)

        self.mock_db_session.commit.assert_called_once()
        self.mock_db_session.refresh.assert_called_once_with(added_object)
        self.assertEqual(returned_notification, added_object)

    def test_create_notification_commit_fails(self):
        # Arrange
        user_id = 1
        message = "Another notification"

        self.mock_db_session.commit.side_effect = SQLAlchemyError("Commit failed")

        # Act & Assert
        with self.assertRaises(SQLAlchemyError): # Service should re-raise the original SQLAlchemyError
            self.notification_service.create_notification(user_id, message)

        self.mock_db_session.add.assert_called_once()
        self.mock_db_session.rollback.assert_called_once()
        self.mock_db_session.refresh.assert_not_called()

if __name__ == '__main__':
    unittest.main()
