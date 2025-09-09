import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.services.quiz_service import QuizService
from app.models import Quiz, QuizQuestion, QuizAnswer, UserQuizAttempt, UserSegment

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def quiz_service(mock_db_session):
    return QuizService(db=mock_db_session)

def test_submit_answers(quiz_service, mock_db_session):
    """
    Test submitting quiz answers and calculating the risk profile.
    """
    # Arrange
    user_id = 1
    quiz_id = 1
    answers = {1: 101, 2: 202} # {question_id: answer_id}

    # Mock the answers that the service will query
    mock_answer1 = QuizAnswer(id=101, question_id=1, score=5)
    mock_answer2 = QuizAnswer(id=202, question_id=2, score=6)

    # When filter_by is called, return the correct answer
    def filter_by_side_effect(**kwargs):
        mock_filter = MagicMock()
        if kwargs.get("id") == 101:
            mock_filter.first.return_value = mock_answer1
        elif kwargs.get("id") == 202:
            mock_filter.first.return_value = mock_answer2
        else:
            mock_filter.first.return_value = None
        return mock_filter

    mock_db_session.query.return_value.filter_by.side_effect = filter_by_side_effect

    # Mock the user segment query
    mock_user_segment = UserSegment(user_id=user_id, rfm_group="Medium")
    mock_db_session.query.return_value.filter_by.return_value.first.side_effect = [
        mock_answer1, mock_answer2, mock_user_segment
    ]


    # Act
    result = quiz_service.submit_answers(user_id=user_id, quiz_id=quiz_id, answers=answers)

    # Assert
    assert result.final_score == 11 # 5 + 6
    assert result.risk_profile_result == "High-Risk"

    # Check that the user's segment was updated
    assert mock_user_segment.risk_profile == "High-Risk"

    # Check that the attempt was added and committed
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called_once()
