from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from ..database import Base

class GameHistory(Base):
    __tablename__ = "game_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    game_type = Column(String(50), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id"), nullable=True, index=True)
    action_type = Column(String(30), nullable=False, index=True)  # BET, WIN, LOSE, BONUS, JACKPOT
    delta_coin = Column(Integer, default=0, nullable=False)
    delta_gem = Column(Integer, default=0, nullable=False)
    result_meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", backref="game_history")
    session = relationship("GameSession", backref="actions")
