from fastapi import APIRouter, Depends, HTTPException

from pydantic import BaseModel
from typing import List, Dict

from ..services.quiz_service import QuizService
from ..database import get_db

router = APIRouter(
    prefix="/quiz",
    tags=["quiz"],
)

class AnswerRequest(BaseModel):
    answers: Dict[int, int] # {question_id: answer_id}

def get_quiz_service(db = Depends(get_db)):
    return QuizService(db)

@router.get("/{quiz_id}")
def get_quiz_details(quiz_id: int, quiz_service: QuizService = Depends(get_quiz_service)):
    """
    Get the details, questions, and answers for a specific quiz.
    """
    try:
        quiz = quiz_service.get_quiz(quiz_id)
        # A proper response model should be used here, but for now, we return a dict
        return {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "questions": [
                {
                    "id": q.id,
                    "text": q.text,
                    "answers": [{"id": a.id, "text": a.text} for a in q.answers]
                } for q in quiz.questions
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{quiz_id}/submit")
def submit_quiz_answers(
    quiz_id: int,
    request: AnswerRequest,
    quiz_service: QuizService = Depends(get_quiz_service),
    user_id: int = 1 # Placeholder for Depends(get_current_user_id)
):
    """
    Submit answers for a quiz and get the resulting risk profile.
    """
    try:
        attempt = quiz_service.submit_answers(
            user_id=user_id,
            quiz_id=quiz_id,
            answers=request.answers
        )
        return {
            "message": "Quiz submitted successfully!",
            "final_score": attempt.final_score,
            "risk_profile": attempt.risk_profile_result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
