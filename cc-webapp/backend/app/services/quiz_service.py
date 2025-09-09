"""
🧠 Casino-Club F2P - Quiz Service (확장)
======================================
퀴즈 게임 비즈니스 로직 서비스
"""

import logging
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from .. import models
from ..schemas.quiz_schemas import QuizAttemptCreate

logger = logging.getLogger(__name__)


class QuizService:
    def __init__(self, db: Session, redis=None):
        self.db = db
        self.redis = redis

    def get_quiz(self, quiz_id: int) -> models.Quiz:
        """
        Retrieves a single quiz with its questions and answers.
        """
        quiz = self.db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
        if not quiz:
            raise ValueError("Quiz not found")
        return quiz

    async def start_quiz_attempt(
        self, 
        user_id: int, 
        quiz_id: int, 
        attempt_data: QuizAttemptCreate
    ) -> models.UserQuizAttempt:
        """퀴즈 시도 시작"""
        try:
            # 퀴즈 존재 확인
            quiz = self.db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
            if not quiz:
                raise ValueError("Quiz not found")
            
            # 최대 시도 횟수 확인
            existing_attempts = self.db.query(models.UserQuizAttempt).filter(
                models.UserQuizAttempt.user_id == user_id,
                models.UserQuizAttempt.quiz_id == quiz_id,
                models.UserQuizAttempt.status == "completed"
            ).count()
            
            max_attempts = getattr(quiz, 'max_attempts', 3)
            if existing_attempts >= max_attempts:
                raise ValueError("Maximum attempts exceeded")
            
            # 문제 수 조회
            question_count = self.db.query(models.QuizQuestion).filter(
                models.QuizQuestion.quiz_id == quiz_id
            ).count()
            
            # 시도 생성 (기존 모델 구조 사용)
            attempt = models.UserQuizAttempt(
                user_id=user_id,
                quiz_id=quiz_id,
                submitted_at=None,  # 시작 시점에는 None
                answers_json={}
            )
            
            # 새 필드들이 있다면 설정
            if hasattr(attempt, 'session_id') and attempt_data.session_id:
                attempt.session_id = attempt_data.session_id
            if hasattr(attempt, 'total_questions'):
                attempt.total_questions = question_count
            if hasattr(attempt, 'status'):
                attempt.status = "in_progress"
            
            self.db.add(attempt)
            self.db.commit()
            self.db.refresh(attempt)
            
            return attempt
            
        except Exception as e:
            logger.error(f"Failed to start quiz attempt: {str(e)}")
            self.db.rollback()
            raise

    async def submit_answer(
        self,
        attempt_id: int,
        user_id: int,
        answer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """답변 제출"""
        try:
            # 시도 확인
            attempt = self.db.query(models.UserQuizAttempt).filter(
                models.UserQuizAttempt.id == attempt_id,
                models.UserQuizAttempt.user_id == user_id
            ).first()
            
            if not attempt:
                raise ValueError("Quiz attempt not found")
            
            question_id = answer_data.get("question_id")
            answer_id = answer_data.get("answer_id")
            
            # 문제 조회
            question = self.db.query(models.QuizQuestion).filter(
                models.QuizQuestion.id == question_id
            ).first()
            
            if not question:
                raise ValueError("Question not found")
            
            # 정답 확인
            is_correct = False
            points_earned = 0
            
            if answer_id:
                quiz_answer = self.db.query(models.QuizAnswer).filter(
                    models.QuizAnswer.id == answer_id,
                    models.QuizAnswer.question_id == question_id
                ).first()
                
                if quiz_answer:
                    points_earned = getattr(quiz_answer, 'score', 0)
                    is_correct = getattr(quiz_answer, 'is_correct', False)
            
            # 답변을 JSON에 저장
            current_answers = attempt.answers_json or {}
            current_answers[str(question_id)] = answer_id
            attempt.answers_json = current_answers
            
            # 점수 업데이트
            if hasattr(attempt, 'total_score'):
                attempt.total_score = getattr(attempt, 'total_score', 0) + points_earned
            
            self.db.commit()
            
            return {
                "is_correct": is_correct,
                "points_earned": points_earned,
                "total_score": getattr(attempt, 'total_score', points_earned)
            }
            
        except Exception as e:
            logger.error(f"Failed to submit answer: {str(e)}")
            self.db.rollback()
            raise

    async def complete_quiz_attempt(
        self,
        attempt_id: int,
        user_id: int
    ) -> models.UserQuizAttempt:
        """퀴즈 시도 완료"""
        try:
            # 시도 조회
            attempt = self.db.query(models.UserQuizAttempt).filter(
                models.UserQuizAttempt.id == attempt_id,
                models.UserQuizAttempt.user_id == user_id
            ).first()
            
            if not attempt:
                raise ValueError("Quiz attempt not found")
            
            # 완료 처리
            attempt.submitted_at = datetime.utcnow()
            
            # 상태 업데이트
            if hasattr(attempt, 'status'):
                attempt.status = "completed"
            
            # 기존 로직 유지 - 점수 계산 및 리스크 프로필
            if not attempt.final_score:
                total_score = self._calculate_total_score(attempt)
                attempt.final_score = total_score
                attempt.risk_profile_result = self._determine_risk_profile(total_score)
            
            self.db.commit()
            
            return attempt
            
        except Exception as e:
            logger.error(f"Failed to complete quiz attempt: {str(e)}")
            self.db.rollback()
            raise

    def _calculate_total_score(self, attempt: models.UserQuizAttempt) -> int:
        """총 점수 계산"""
        total_score = 0
        answers = attempt.answers_json or {}
        
        for question_id_str, answer_id in answers.items():
            question_id = int(question_id_str)
            answer = self.db.query(models.QuizAnswer).filter(
                models.QuizAnswer.id == answer_id,
                models.QuizAnswer.question_id == question_id
            ).first()
            if answer and hasattr(answer, 'score'):
                total_score += answer.score
        
        return total_score

    def _determine_risk_profile(self, total_score: int) -> str:
        """리스크 프로필 결정"""
        if total_score > 10:
            return "High-Risk"
        elif total_score > 5:
            return "Calculated-Risk"
        else:
            return "Conservative"

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """사용자 퀴즈 통계"""
        try:
            # 전체 시도 수
            total_attempts = self.db.query(models.UserQuizAttempt).filter(
                models.UserQuizAttempt.user_id == user_id
            ).count()
            
            # 완료된 시도 수 (submitted_at이 있는 것들)
            completed_attempts = self.db.query(models.UserQuizAttempt).filter(
                models.UserQuizAttempt.user_id == user_id,
                models.UserQuizAttempt.submitted_at.isnot(None)
            ).count()
            
            # 평균 점수
            attempts_with_scores = self.db.query(models.UserQuizAttempt).filter(
                models.UserQuizAttempt.user_id == user_id,
                models.UserQuizAttempt.final_score.isnot(None)
            ).all()
            
            if attempts_with_scores:
                avg_score = sum(attempt.final_score for attempt in attempts_with_scores) / len(attempts_with_scores)
                best_score = max(attempt.final_score for attempt in attempts_with_scores)
            else:
                avg_score = 0.0
                best_score = 0
            
            return {
                "total_attempts": total_attempts,
                "completed_attempts": completed_attempts,
                "average_score": round(avg_score, 1),
                "best_score": best_score,
                "completion_rate": round((completed_attempts / total_attempts * 100), 1) if total_attempts > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {str(e)}")
            return {
                "total_attempts": 0,
                "completed_attempts": 0,
                "average_score": 0.0,
                "best_score": 0,
                "completion_rate": 0.0
            }

    def submit_answers(self, user_id: int, quiz_id: int, answers: Dict[int, int]) -> models.UserQuizAttempt:
        """
        Submits a user's answers for a quiz, calculates the score, and updates their profile.
        - answers: A dictionary of {question_id: answer_id}
        """
        total_score = 0
        for question_id, answer_id in answers.items():
            answer = self.db.query(models.QuizAnswer).filter_by(id=answer_id, question_id=question_id).first()
            if answer:
                total_score += answer.score

        # Determine risk profile based on score
        if total_score > 10:
            risk_profile = "High-Risk"
        elif total_score > 5:
            risk_profile = "Calculated-Risk"
        else:
            risk_profile = "Low-Risk"

        # Save the attempt
        attempt = models.UserQuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            final_score=total_score,
            risk_profile_result=risk_profile,
            answers_json=answers  # SQLAlchemy JSON/Text 컬럼 assume
        )
        self.db.add(attempt)

        # Update the user's segment profile
        user_segment = self.db.query(models.UserSegment).filter_by(user_id=user_id).first()
        if user_segment:
            user_segment.risk_profile = risk_profile
        else:
            user_segment = models.UserSegment(user_id=user_id, risk_profile=risk_profile, rfm_group="New")
            self.db.add(user_segment)
        self.db.flush()  # flush 후 attempt id 확보 및 segment 갱신 즉시 반영
        self.db.commit()
        self.db.refresh(attempt)

        return attempt
