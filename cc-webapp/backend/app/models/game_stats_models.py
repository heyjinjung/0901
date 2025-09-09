from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, Numeric, DateTime, ForeignKey
from ..database import Base

class UserGameStats(Base):
    __tablename__ = 'user_game_stats'
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    total_bets = Column(BigInteger, nullable=False, default=0)
    total_wins = Column(BigInteger, nullable=False, default=0)
    total_losses = Column(BigInteger, nullable=False, default=0)
    highest_multiplier = Column(Numeric(10, 4), nullable=True)
    total_profit = Column(Numeric(18, 2), nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # NOTE: relationship back to User optional; avoid circular heavy import
    # from ..models.auth_models import User
    # user = relationship('User', backref=backref('game_stats', uselist=False))

    def as_dict(self):
        return {
            'user_id': self.user_id,
            'total_bets': int(self.total_bets or 0),
            'total_wins': int(self.total_wins or 0),
            'total_losses': int(self.total_losses or 0),
            'highest_multiplier': float(self.highest_multiplier) if self.highest_multiplier is not None else None,
            'total_profit': float(self.total_profit or 0),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
