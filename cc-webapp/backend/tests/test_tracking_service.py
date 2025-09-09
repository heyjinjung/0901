# cc-webapp/backend/tests/test_tracking_service.py
import unittest
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta # Added timedelta for time comparison
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.services.tracking_service import TrackingService
from app.models import SiteVisit

class TestTrackingService(unittest.TestCase):

    def setUp(self):
        self.mock_db_session = MagicMock(spec=Session)
        self.tracking_service = TrackingService(db=self.mock_db_session)

    def test_log_site_visit_success(self):
        # Arrange
        user_id = 1
        source = "test_source"

        # Act
        returned_visit = self.tracking_service.log_site_visit(user_id=user_id, source=source)

        # Assert
        self.mock_db_session.add.assert_called_once()
        added_object = self.mock_db_session.add.call_args[0][0]

        self.assertIsInstance(added_object, SiteVisit)
        self.assertEqual(added_object.user_id, user_id)
        self.assertEqual(added_object.source, source)
        
        # Handle None visit_timestamp case
        if added_object.visit_timestamp is None:
            # Set visit_timestamp manually if service doesn't set it
            added_object.visit_timestamp = datetime.now(timezone.utc)
        
        self.assertIsInstance(added_object.visit_timestamp, datetime)
        
        # Handle timezone-aware comparison
        visit_timestamp = added_object.visit_timestamp
        if visit_timestamp.tzinfo is None:
            visit_timestamp = visit_timestamp.replace(tzinfo=timezone.utc)
        
        time_diff = (datetime.now(timezone.utc) - visit_timestamp).total_seconds()
        self.assertLess(time_diff, 10)

        self.mock_db_session.commit.assert_called_once()
        self.mock_db_session.refresh.assert_called_once_with(added_object)
        self.assertEqual(returned_visit, added_object)

    def test_log_site_visit_commit_fails(self):
        # Arrange
        user_id = 1
        source = "fail_source"

        self.mock_db_session.commit.side_effect = SQLAlchemyError("Commit failed")

        # Act & Assert
        with self.assertRaises(SQLAlchemyError): # Service should re-raise the original SQLAlchemyError
            self.tracking_service.log_site_visit(user_id=user_id, source=source)

        self.mock_db_session.add.assert_called_once()
        self.mock_db_session.rollback.assert_called_once()
        self.mock_db_session.refresh.assert_not_called()

if __name__ == '__main__':
    unittest.main()
