"""
Integrated utility module
- Game probability calculation
- Reward processing
- Emotion feedback
- Segmentation
- Redis helper
- Webhooks and external APIs
"""

__version__ = "1.0.0"

# 모든 유틸리티 함수들을 중앙 집중식으로 import
from .probability import *
from .emotion_utils import *
from .segment_utils import *
from .redis import *
from .sentiment_analyzer import *

__all__ = [
    # Probability Utils
    'calculate_gacha_probability',
    'calculate_streak_bonus',
    'weighted_random_choice',
    'variable_ratio_reward',
    'calculate_drop_rates',
    'simulate_gacha_pull',
    
    # Emotion Utils
    'get_feedback_message',
    'generate_dopamine_trigger',
    'calculate_addiction_score',
    'get_responsible_gaming_message',
    'create_achievement_feedback',
    
    # Segment Utils
    'calculate_rfm_score',
    'update_user_segment',
    'get_personalized_offers',
    'compute_rfm_and_update_segments',
    
    # Redis Utils
    'init_redis_manager',
    'get_redis_manager',
    'cache_user_data',
    'get_cached_data',
    'update_streak_counter',
    'manage_session_data',
    
    # Sentiment Utils
    'preprocess_text',
    'detect_language',
    'analyze_emotion_basic',
    'get_emotion_analysis',
]
