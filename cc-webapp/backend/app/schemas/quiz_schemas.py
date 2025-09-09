"""
🧠 Casino-Club F2P - Quiz Schemas
===============================
퀴즈 시스템 Pydantic 스키마 정의
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class QuizType(str, Enum):
    GENERAL = "general"
    RISK_PROFILE = "risk_profile"
    KNOWLEDGE = "knowledge"
    PERSONALITY = "personality"


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SCALE = "scale"
    INPUT = "input"


class QuizCategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    category_type: str = "general"
    is_active: bool = True
    model_config = ConfigDict(from_attributes=True)


class QuizAnswerResponse(BaseModel):
    id: int
    text: str
    order: int = 0
    model_config = ConfigDict(from_attributes=True)


class QuizQuestionResponse(BaseModel):
    id: int
    text: str
    question_type: QuestionType = QuestionType.MULTIPLE_CHOICE
    order: int = 0
    points: int = 10
    explanation: Optional[str] = None
    answers: List[QuizAnswerResponse] = []
    model_config = ConfigDict(from_attributes=True)


class QuizResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    quiz_type: QuizType = QuizType.GENERAL
    difficulty: str = "medium"
    time_limit: int = 300
    max_attempts: int = 3
    reward_tokens: int = 100
    is_active: bool = True
    category: Optional[QuizCategoryResponse] = None
    questions: List[QuizQuestionResponse] = []
    model_config = ConfigDict(from_attributes=True)


class QuizAttemptCreate(BaseModel):
    session_id: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class QuizAnswerSubmit(BaseModel):
    question_id: int
    answer_id: Optional[int] = None
    answer_text: Optional[str] = None
    time_taken: Optional[int] = None


class QuizAttemptResponse(BaseModel):
    id: int
    user_id: int
    quiz_id: int
    session_id: Optional[str] = None
    start_time: datetime
    submitted_at: Optional[datetime] = None
    completion_time: Optional[int] = None
    total_score: int = 0
    correct_answers: int = 0
    total_questions: int = 0
    risk_profile_result: Optional[str] = None
    personality_traits: Optional[Dict[str, Any]] = None
    status: str = "in_progress"
    feedback: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)


class QuizLeaderboardResponse(BaseModel):
    id: int
    user_id: int
    best_score: int = 0
    average_score: float = 0.0
    total_attempts: int = 0
    completion_rate: float = 0.0
    rank_position: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class QuizStatsResponse(BaseModel):
    total_attempts: int = 0
    completed_attempts: int = 0
    average_score: float = 0.0
    best_score: int = 0
    total_time_spent: int = 0
    favorite_categories: List[Dict[str, Any]] = []
    recent_performance: List[Dict[str, Any]] = []
    risk_profile_history: List[Dict[str, Any]] = []
    achievements: List[Dict[str, Any]] = []
    model_config = ConfigDict(from_attributes=True)
