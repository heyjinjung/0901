from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, func
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import uuid

from app.db.base import Base

class UserGameLimit(Base):
    __tablename__ = "user_game_limits"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    game_type = Column(String, index=True)  # "slot", "crash", "rps", "gacha"
    daily_max = Column(Integer, default=0)
    daily_used = Column(Integer, default=0)
    last_reset = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    @property
    def remaining(self):
        """Calculate remaining plays today"""
        return max(0, self.daily_max - self.daily_used)
        
    @property
    def needs_reset(self):
        """Check if we need to reset the counter (new day)"""
        now = datetime.utcnow()
        # Reset if the last reset was before today's date
        return self.last_reset.date() < now.date()
    
    def use_play(self):
        """Use one play and return remaining count"""
        if self.needs_reset:
            self.reset_count()
            
        if self.remaining > 0:
            self.daily_used += 1
            return self.remaining
        return 0
    
    def reset_count(self):
        """Reset daily count (called at midnight or first play of day)"""
        self.daily_used = 0
        self.last_reset = datetime.utcnow()
        return self.daily_max
