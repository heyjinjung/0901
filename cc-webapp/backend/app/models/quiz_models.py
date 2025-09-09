"""
🧠 Casino-Club F2P - Quiz 모델 (확장)
============================
퀴즈 게임 및 심리 프로필 측정 시스템
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from ..database import Base


class QuizResult(Base):
    """사용자 위험 평가 결과"""
    __tablename__ = "quiz_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_type = Column(String(50), default="risk_assessment")
    answers = Column(JSON)  # 사용자 답변 데이터
    risk_score = Column(Integer)  # 위험 점수
    risk_level = Column(String(50))  # 위험 수준 (high-risk, moderate-risk, low-risk)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    user = relationship("User")


class QuizCategory(Base):
    """퀴즈 카테고리"""
    __tablename__ = "quiz_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    icon = Column(String(100))  # 아이콘 이름
    category_type = Column(String(50), default="general")  # general, risk_assessment, personality
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    quizzes = relationship("Quiz", back_populates="category")


class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("quiz_categories.id"))
    title = Column(String, nullable=False, unique=True)
    description = Column(String)
    quiz_type = Column(String(50), default="general")  # general, risk_profile, knowledge
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    time_limit = Column(Integer, default=300)  # 제한시간(초)
    max_attempts = Column(Integer, default=3)  # 최대 시도 횟수
    reward_tokens = Column(Integer, default=100)  # 완료 시 보상 토큰
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    category = relationship("QuizCategory", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("UserQuizAttempt", back_populates="quiz")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    text = Column(String, nullable=False)
    question_type = Column(String(50), default="multiple_choice")  # multiple_choice, true_false, scale
    order = Column(Integer, default=0)
    points = Column(Integer, default=10)  # 문제당 점수
    explanation = Column(Text)  # 정답 해설
    
    # 관계
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("QuizAnswer", back_populates="question", cascade="all, delete-orphan")
    user_answers = relationship("UserQuizAnswer", back_populates="question")


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    text = Column(String, nullable=False)
    score = Column(Integer, default=0)  # 리스크 프로필/성격 점수
    is_correct = Column(Boolean, default=False)  # 정답 여부 (지식 퀴즈용)
    order = Column(Integer, default=0)
    
    # 관계
    question = relationship("QuizQuestion", back_populates="answers")


class UserQuizAttempt(Base):
    __tablename__ = "user_quiz_attempts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    session_id = Column(String(100))  # 세션 추적용
    start_time = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime)
    completion_time = Column(Integer)  # 소요시간(초)
    total_score = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    final_score = Column(Integer)
    risk_profile_result = Column(String)  # "High-Risk", "Calculated-Risk", "Conservative"
    personality_traits = Column(JSON)  # 성격 특성 분석 결과
    answers_json = Column(JSON)  # 실제 답변 데이터
    status = Column(String(20), default="in_progress")  # in_progress, completed, abandoned
    
    # 관계
    user = relationship("User")
    quiz = relationship("Quiz", back_populates="attempts")
    user_answers = relationship("UserQuizAnswer", back_populates="attempt")


class UserQuizAnswer(Base):
    """사용자 개별 답변 기록"""
    __tablename__ = "user_quiz_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("user_quiz_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    answer_id = Column(Integer, ForeignKey("quiz_answers.id"))
    answer_text = Column(String(500))  # 주관식 답변
    is_correct = Column(Boolean)
    points_earned = Column(Integer, default=0)
    time_taken = Column(Integer)  # 문제당 소요시간
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    attempt = relationship("UserQuizAttempt", back_populates="user_answers")
    question = relationship("QuizQuestion", back_populates="user_answers")
    answer = relationship("QuizAnswer")


class QuizLeaderboard(Base):
    """퀴즈 리더보드"""
    __tablename__ = "quiz_leaderboards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    category_id = Column(Integer, ForeignKey("quiz_categories.id"))
    period_type = Column(String(20), default="all_time")  # daily, weekly, monthly, all_time
    best_score = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    total_attempts = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    rank_position = Column(Integer)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    user = relationship("User")
    quiz = relationship("Quiz")
    category = relationship("QuizCategory")
