from enum import Enum

class SupportedEmotion(str, Enum):
    EXCITEMENT = "EXCITEMENT"
    DISAPPOINTMENT = "DISAPPOINTMENT"
    ANTICIPATION = "ANTICIPATION"
    CELEBRATION = "CELEBRATION"
    ENCOURAGEMENT = "ENCOURAGEMENT"
    FRUSTRATED = "FRUSTRATED" # From the test
    JOY = "joy"
    SAD = "sad"
    ANGRY = "angry"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    CALM = "calm"
