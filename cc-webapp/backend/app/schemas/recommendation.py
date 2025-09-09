from pydantic import BaseModel
from typing import Optional

class FinalRecommendation(BaseModel):
    game_type: str
    confidence: float
    reason: Optional[str] = None