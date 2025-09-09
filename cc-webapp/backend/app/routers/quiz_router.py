"""
Quiz Router
Handles psychometric quiz system for risk assessment and user profiling
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from ..database import get_db
from ..models import User, UserSegment, QuizResult
from ..schemas.quiz import (
    QuizQuestionResponse, 
    QuizSubmissionRequest, 
    QuizResultResponse,
    QuizAnalyticsResponse
)
from ..services.auth_service import get_current_user
from ..services.quiz_service import QuizService
from ..services.user_service import UserService
from sqlalchemy.orm import Session

router = APIRouter(tags=["Quiz"])
logger = logging.getLogger(__name__)

@router.get("/questions", response_model=List[QuizQuestionResponse])
async def get_quiz_questions(
    quiz_type: str = "risk_assessment",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get quiz questions for risk assessment"""
    try:
        questions = QuizService.get_quiz_questions(quiz_type)
        logger.info(f"Quiz questions requested by user {current_user.id}")
        return questions
    except Exception as e:
        logger.error(f"Error getting quiz questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get quiz questions"
        )

@router.post("/submit", response_model=QuizResultResponse)
async def submit_quiz(
    quiz_data: QuizSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit quiz answers and get risk profile"""
    try:
        # Calculate risk score
        risk_score = QuizService.calculate_risk_score(quiz_data.answers)
        risk_level = QuizService.determine_risk_level(risk_score)
        
        # Save quiz result
        quiz_result = QuizResult(
            user_id=current_user.id,
            quiz_type=quiz_data.quiz_type,
            answers=quiz_data.answers,
            risk_score=risk_score,
            risk_level=risk_level,
            completed_at=datetime.utcnow()
        )
        db.add(quiz_result)
        
        # Update user segment
        user_segment = UserService.get_or_create_segment(current_user.id, db)
        user_segment.risk_profile = risk_level
        user_segment.last_updated = datetime.utcnow()
        
        db.commit()
        
        # Generate recommendations
        recommendations = _get_risk_recommendations(risk_level)
        
        logger.info(f"Quiz completed by user {current_user.id}, risk level: {risk_level}")
        
        return QuizResultResponse(
            quiz_id=quiz_result.id,
            risk_score=risk_score,
            risk_level=risk_level,
            recommendations=recommendations,
            completed_at=quiz_result.completed_at
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error submitting quiz: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit quiz"
        )

@router.get("/results/{quiz_id}", response_model=QuizResultResponse)
async def get_quiz_result(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific quiz result"""
    try:
        quiz_result = db.query(QuizResult).filter(
            QuizResult.id == quiz_id,
            QuizResult.user_id == current_user.id
        ).first()
        
        if not quiz_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz result not found"
            )
        
        recommendations = _get_risk_recommendations(quiz_result.risk_level)
        
        return QuizResultResponse(
            quiz_id=quiz_result.id,
            risk_score=quiz_result.risk_score,
            risk_level=quiz_result.risk_level,
            recommendations=recommendations,
            completed_at=quiz_result.completed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting quiz result: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get quiz result"
        )

@router.get("/user/history", response_model=List[QuizResultResponse])
async def get_user_quiz_history(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's quiz history"""
    try:
        quiz_results = db.query(QuizResult).filter(
            QuizResult.user_id == current_user.id
        ).order_by(QuizResult.completed_at.desc()).limit(limit).all()
        
        results = []
        for result in quiz_results:
            recommendations = _get_risk_recommendations(result.risk_level)
            results.append(QuizResultResponse(
                quiz_id=result.id,
                risk_score=result.risk_score,
                risk_level=result.risk_level,
                recommendations=recommendations,
                completed_at=result.completed_at
            ))
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting quiz history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get quiz history"
        )

@router.get("/analytics", response_model=QuizAnalyticsResponse)
async def get_quiz_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get quiz analytics for admin users"""
    try:
        # Check admin permission
        if current_user.vip_tier != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        analytics = QuizService.get_quiz_analytics(db)
        
        return QuizAnalyticsResponse(
            total_quizzes=analytics["total_quizzes"],
            risk_distribution=analytics["risk_distribution"],
            completion_rate=analytics["completion_rate"],
            average_risk_score=analytics["average_risk_score"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting quiz analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get quiz analytics"
        )

def _get_risk_recommendations(risk_level: str) -> List[str]:
    """Get recommendations based on risk level"""
    recommendations = {
        "high-risk": [
            "Consider setting daily spending limits",
            "Take regular breaks from gaming",
            "Monitor your gaming time and habits",
            "Seek support if gambling becomes problematic"
        ],
        "moderate-risk": [
            "Set weekly spending budgets",
            "Track your gaming sessions",
            "Consider using cooling-off periods",
            "Review your gaming habits regularly"
        ],
        "low-risk": [
            "Continue playing responsibly",
            "Maintain awareness of your spending",
            "Enjoy gaming as entertainment",
            "Stay informed about responsible gaming"
        ]
    }
    
    return recommendations.get(risk_level, recommendations["low-risk"])

def _calculate_weekly_insights(user_id: int, db: Session) -> Dict[str, Any]:
    """Calculate weekly insights for user"""
    try:
        # Get recent quiz results
        recent_results = db.query(QuizResult).filter(
            QuizResult.user_id == user_id,
            QuizResult.completed_at >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        if not recent_results:
            return {
                "trend": "stable",
                "score_change": 0,
                "recommendation": "Take a quiz to track your gaming habits"
            }
        
        scores = [result.risk_score for result in recent_results]
        avg_score = sum(scores) / len(scores)
        
        # Determine trend
        if len(scores) > 1:
            score_change = scores[-1] - scores[0]
            if score_change > 5:
                trend = "increasing"
            elif score_change < -5:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
            score_change = 0
        
        return {
            "trend": trend,
            "score_change": score_change,
            "average_score": avg_score,
            "quiz_count": len(recent_results)
        }
        
    except Exception as e:
        logger.error(f"Error calculating weekly insights: {e}")
        return {
            "trend": "unknown",
            "score_change": 0,
            "recommendation": "Unable to calculate insights"
        }

def _validate_quiz_answers(answers: Dict[str, Any], quiz_type: str) -> bool:
    """Validate quiz answers format and content"""
    try:
        required_fields = QuizService.get_required_fields(quiz_type)
        
        for field in required_fields:
            if field not in answers:
                return False
                
        return True
        
    except Exception as e:
        logger.error(f"Error validating quiz answers: {e}")
        return False

def _generate_personalized_feedback(risk_score: int, risk_level: str, user_data: Dict) -> str:
    """Generate personalized feedback based on user profile"""
    try:
        base_feedback = {
            "high-risk": "Your responses indicate a higher risk profile. We recommend implementing stricter controls.",
            "moderate-risk": "Your responses show moderate risk indicators. Consider monitoring your gaming habits.",
            "low-risk": "Your responses indicate responsible gaming habits. Keep up the good work!"
        }
        
        feedback = base_feedback.get(risk_level, base_feedback["low-risk"])
        
        # Add personalized elements based on user data
        if user_data.get("gaming_frequency") == "daily":
            feedback += " Since you game daily, consider setting time limits."
            
        if user_data.get("spending_trend") == "increasing":
            feedback += " We notice increased spending patterns. Monitor your budget carefully."
        
        return feedback
        
    except Exception as e:
        logger.error(f"Error generating personalized feedback: {e}")
        return "Thank you for completing the quiz. Please review our responsible gaming guidelines."
