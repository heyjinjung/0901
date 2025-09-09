"""게임 통계 집계 서비스

MVP 범위: game_history 테이블 기반 단순 집계 (win_rate / ROI)

ROI 정의:
  total_bet = sum( -delta_coin ) for BET (delta_coin 음수 저장 가정) 절대값 합
  total_win = sum( delta_coin ) for WIN (양수)
  net = total_win - total_bet
  roi = (net / total_bet) if total_bet>0 else 0

win_rate 정의:
  wins = WIN action 수
  total_hands = BET action 수 (또는 (WIN+LOSE)?) -> 명세 불명확: 문서 항목 "게임 핸드 데이터 저장" 기준 BET 단위를 hand 로 본다.
  win_rate = wins / total_hands if total_hands>0 else 0

NOTE: delta_coin 부호 정책이 다를 경우 조정 필요. 현재 구현은 BET 시 음수 기록을 전제로 함.
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from ..models.history_models import GameHistory

class GameStatsService:
    def __init__(self, db: Session):
        self.db = db

    def basic_stats(self, *, user_id: Optional[int] = None, game_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """게임별 기본 통계 리스트 반환.

        필터:
          user_id: 특정 사용자 한정 (없으면 전체)
          game_type: 단일 게임 타입 한정
        반환: [{game_type, total_hands, wins, win_rate, total_bet, total_win, net, roi}]
        """
        q = self.db.query(
            GameHistory.game_type.label("game_type"),
            # total_hands: BET 액션 횟수
            func.sum(case((GameHistory.action_type == "BET", 1), else_=0)).label("total_hands"),
            # wins: WIN 액션 횟수
            func.sum(case((GameHistory.action_type == "WIN", 1), else_=0)).label("wins"),
            # total_bet: BET 행에서 delta_coin 절대값 합 (음수 가정) -> -delta_coin 합
            func.coalesce(func.sum(case((GameHistory.action_type == "BET", -GameHistory.delta_coin), else_=0)), 0).label("total_bet"),
            # total_win: WIN 행에서 delta_coin 합(양수 가정)
            func.coalesce(func.sum(case((GameHistory.action_type == "WIN", GameHistory.delta_coin), else_=0)), 0).label("total_win"),
        )
        if user_id is not None:
            q = q.filter(GameHistory.user_id == user_id)
        if game_type is not None:
            q = q.filter(GameHistory.game_type == game_type)
        q = q.group_by(GameHistory.game_type)
        rows = q.all()
        results: List[Dict[str, Any]] = []
        for r in rows:
            total_hands = int(r.total_hands or 0)
            wins = int(r.wins or 0)
            total_bet = int(r.total_bet or 0)
            total_win = int(r.total_win or 0)
            net = total_win - total_bet
            win_rate = (wins / total_hands) if total_hands > 0 else 0.0
            roi = (net / total_bet) if total_bet > 0 else 0.0
            results.append(
                {
                    "game_type": r.game_type,
                    "total_hands": total_hands,
                    "wins": wins,
                    "win_rate": round(win_rate, 4),
                    "total_bet": total_bet,
                    "total_win": total_win,
                    "net": net,
                    "roi": round(roi, 4),
                }
            )
        return results
