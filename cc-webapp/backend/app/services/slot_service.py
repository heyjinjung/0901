from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
import random
import datetime

from .token_service import TokenService
from ..repositories.game_repository import GameRepository
from .. import models

@dataclass
class SlotSpinResult:
    result: str
    tokens_change: int
    balance: int
    daily_spin_count: int
    animation: Optional[str]

class SlotService:
    """슬롯 머신 로직을 담당하는 서비스 계층."""

    def __init__(self, repository: GameRepository | None = None, token_service: TokenService | None = None, db: Optional[Session] = None) -> None:
        self.repo = repository or GameRepository()
        self.token_service = token_service or TokenService(db, self.repo)

    def spin(self, user_id: int, bet_amount: int, db: Optional[Session] = None, *_, **__) -> SlotSpinResult:
        """슬롯 스핀 실행 (db optional; 테스트 호환)."""
        db = db or getattr(self.token_service, 'db', None)
        if db is None:
            raise ValueError("Database session not provided")
        if not getattr(self.token_service, 'db', None):
            self.token_service.db = db

        # 1. 베팅액 검증
        if not (5000 <= bet_amount <= 10000):
            raise ValueError("베팅액은 5,000에서 10,000 사이여야 합니다.")

        # 2. 일일 스핀 횟수 제한 검증
        daily_spin_count = 0
        try:
            if hasattr(self.repo, 'count_daily_actions'):
                raw_count = self.repo.count_daily_actions(db, user_id, "SLOT_SPIN") or 0
                try:
                    daily_spin_count = int(raw_count)
                except Exception:
                    daily_spin_count = 0
        except Exception:
            daily_spin_count = 0
        if daily_spin_count >= 30:
            raise ValueError("일일 슬롯 스핀 횟수(30회)를 초과했습니다.")

        # 3. 토큰 차감
        deducted_tokens = self.token_service.deduct_tokens(user_id, bet_amount)
        if deducted_tokens is None:
            raise ValueError("토큰이 부족합니다.")

        # 4. 승리/패배 및 보상 계산 (수익률 85% 기반)
        # RTP 15% -> 15% 확률로 승리하고, 승리 시 베팅액의 100/15 * 0.15 = 1배, 즉 베팅액만큼 돌려받음.
        # 더 나은 사용자 경험을 위해, 승리 시 베팅액의 2배를 돌려주고 승리 확률을 7.5%로 조정. RTP는 동일.
        win_chance = 0.075  # 7.5%
        spin = random.random()
        
        result: str
        reward: int
        animation: str

        if spin < win_chance:
            # 승리
            result = "win"
            reward = bet_amount * 2  # 2배 지급
            animation = "win"
        else:
            # 패배
            result = "lose"
            reward = 0
            animation = "lose"
            # 50% 확률로 근접 실패 애니메이션
            if random.random() < 0.5:
                animation = "near_miss"

        # 5. 보상 지급 (승리 시)
        if reward > 0:
            self.token_service.add_tokens(user_id, reward)

        # 6. 액션 기록
        self.repo.record_action(db, user_id, "SLOT_SPIN", -bet_amount)
        
        # 7. 게임 결과 기록
        game = models.Game(
            user_id=user_id,
            game_type="slot",
            bet_amount=bet_amount,
            result=result,
            payout=reward
        )
        db.add(game)
        db.commit()

        # 8. 최종 결과 반환
        final_balance = self.token_service.get_token_balance(user_id)
        tokens_change = reward - bet_amount
        
        return SlotSpinResult(
            result=result,
            tokens_change=tokens_change,
            balance=final_balance,
            daily_spin_count=daily_spin_count + 1,
            animation=animation
        )
