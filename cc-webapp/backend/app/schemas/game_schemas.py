"""
게임 관련 스키마 정의

PrizeRoulette 게임 및 프로필 API에서 사용하는 요청/응답 스키마 정의
"""
from typing import Dict, List, Optional, Any
from pydantic import ConfigDict
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

# 프라이즈 룰렛 스키마 정의
class Prize(BaseModel):
   class CrashBetResponse(BaseModel):
    """크래시 게임 베팅 응답 모델"""
    success: bool
    game_id: str
    bet_amount: int
    potential_win: int
    max_multiplier: Optional[float] = None
    message: str
    balance: int
    status: Optional[str] = Field(default=None, description="베팅 직후 상태 placed|auto_cashed|active 등")
    simulated_max_win: Optional[int] = Field(default=None, description="UI 표시용 – 현재 multiplier 기반 가상의 최대 승리금 (auto_cashout 미지정 시 안내)")
    win_amount: Optional[int] = Field(default=None, description="실제 획득 금액")


class CrashCashoutRequest(BaseModel):
    """크래시 게임 수동 캐시아웃 요청 모델"""
    game_id: str
    multiplier: float


class CrashCashoutResponse(BaseModel):
    """크래시 게임 수동 캐시아웃 응답 모델"""
    success: bool
    game_id: str
    cashout_multiplier: float
    win_amount: int
    balance: int
    message: str


class Prize(BaseModel):
    """상품 모델"""
    id: str
    name: str
    value: int
    color: str
    probability: float
    icon: Optional[str] = None


class RouletteInfoResponse(BaseModel):
    """룰렛 정보 응답 모델"""
    success: bool = True
    spins_left: int
    max_spins: int = 3
    cooldown_expires: Optional[str] = None
    prizes: List[Prize]
    recent_spins: Optional[List[Dict[str, Any]]] = None
    message: Optional[str] = None


class RouletteSpinRequest(BaseModel):
    """룰렛 스핀 요청 모델 (필요시)"""
    pass


class RouletteSpinResponse(BaseModel):
    """룰렛 스핀 응답 모델"""
    success: bool
    prize: Optional[Prize] = None
    message: str
    spins_left: int
    cooldown_expires: Optional[str] = None
    is_near_miss: Optional[bool] = False
    animation_type: Optional[str] = "normal"


# 게임 통계 스키마
class GameStats(BaseModel):
    """사용자 게임 통계 모델"""
    user_id: int
    total_spins: int = 0
    total_coins_won: int = 0
    total_gems_won: int = 0
    special_items_won: int = 0
    jackpots_won: int = 0
    bonus_spins_won: int = 0
    best_streak: int = 0
    current_streak: int = 0
    last_spin_date: Optional[datetime] = None


class GameSession(BaseModel):
    """게임 세션 모델"""
    session_id: str
    user_id: int
    game_type: str
    start_time: datetime
    duration: Optional[int] = None  # 초 단위
    current_bet: Optional[int] = 0
    current_round: Optional[int] = 0
    status: str = "active"
    
    
class GameSessionStart(BaseModel):
    """게임 세션 시작 요청 모델"""
    game_type: str
    bet_amount: Optional[int] = 0
    metadata: Optional[Dict[str, Any]] = None
    
    
class GameSessionEnd(BaseModel):
    """게임 세션 종료 요청 모델"""
    session_id: str
    duration: int  # 초 단위
    rounds_played: int = 1
    total_bet: int = 0
    total_win: int = 0
    game_result: Optional[Dict[str, Any]] = None


# 프로필 API 스키마
class UserGameActivity(BaseModel):
    """사용자 게임 활동 요약"""
    game_type: str
    total_rounds: int = 0
    total_wins: int = 0
    total_losses: int = 0
    win_rate: float = 0.0
    favorite: bool = False
    last_played: Optional[datetime] = None


class Achievement(BaseModel):
    """사용자 업적"""
    id: int
    name: str
    description: str
    badge_icon: str
    badge_color: str
    achieved_at: Optional[datetime] = None
    progress: Optional[float] = None  # 0.0 ~ 1.0


class ProfileGameStats(BaseModel):
    """프로필 게임 통계 응답"""
    user_id: int
    total_games_played: int = 0
    total_time_played: Optional[int] = None  # 분 단위
    favorite_game: Optional[str] = None
    recent_activities: List[UserGameActivity] = []
    achievements: List[Achievement] = []
    current_session: Optional[GameSession] = None


# 게임 목록 스키마
class GameListResponse(BaseModel):
    """게임 목록 응답 모델"""
    id: str
    name: str
    description: str
    type: str
    image_url: str
    is_active: bool = True
    daily_limit: Optional[int] = None
    playCount: Optional[int] = 0
    bestScore: Optional[int] = 0
    canPlay: bool = True
    cooldown_remaining: Optional[int] = None
    requires_vip_tier: Optional[int] = None


class GameDetailResponse(BaseModel):
    """게임 상세 정보 응답 모델"""
    id: str
    name: str
    description: str
    type: str
    image_url: str
    rules: str
    bet_options: Optional[List[int]] = None
    min_bet: Optional[int] = None
    max_bet: Optional[int] = None
    game_config: Optional[Dict[str, Any]] = None
    is_active: bool = True
    daily_limit: Optional[int] = None
    cooldown_seconds: Optional[int] = None
    requires_vip_tier: Optional[int] = None


# 리더보드 스키마
class LeaderboardEntry(BaseModel):
    """리더보드 항목"""
    rank: int
    user_id: int
    nickname: str
    score: int
    avatar_url: Optional[str] = None


class GameLeaderboard(BaseModel):
    """게임 리더보드 응답"""
    game_type: str
    period: str
    entries: List[LeaderboardEntry] = []
    user_rank: Optional[int] = None
    updated_at: datetime


# 슬롯 머신 게임 스키마
class SlotSpinRequest(BaseModel):
    """슬롯 머신 스핀 요청 모델"""
    bet_amount: int
    lines: int = 1


class SlotSpinResponse(BaseModel):
    """슬롯 머신 스핀 응답 모델"""
    success: bool
    reels: List[List[str]]
    win_amount: int = 0
    win_lines: List[Dict[str, Any]] = []
    multiplier: float = 1.0
    is_jackpot: bool = False
    free_spins_awarded: int = 0
    message: str
    balance: int
    special_animation: Optional[str] = None
    # 표준화된 피드백 블록 (UI 토스트/애니메이션 트리거)
    feedback: Optional[Dict[str, Any]] = None
    net_change: Optional[int] = Field(default=None, description="순 변화량 (win_amount - bet_amount)")


# 가위바위보 게임 스키마
class RPSPlayRequest(BaseModel):
    """가위바위보 게임 요청 모델"""
    choice: str  # 'rock', 'paper', 'scissors'
    bet_amount: int


class RPSPlayResponse(BaseModel):
    """가위바위보 게임 응답 모델"""
    success: bool
    player_choice: str
    computer_choice: str
    result: str  # 'win', 'lose', 'draw'
    win_amount: int = 0
    message: str
    balance: int
    streak: Optional[int] = None


# 가챠 게임 스키마
class GachaPullRequest(BaseModel):
    """가챠 뽑기 요청 모델"""
    gacha_id: Optional[str] = None
    pull_count: int = 1
    use_premium_currency: bool = False
    # OpenAPI 예시
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "pull_count": 10,
            "use_premium_currency": False
        }
    })


class GachaPullResponse(BaseModel):
    """가챠 뽑기 응답 모델"""
    success: bool
    items: List[Dict[str, Any]]
    rare_item_count: int = 0
    ultra_rare_item_count: int = 0
    pull_count: int
    balance: int
    special_animation: Optional[str] = None
    # Added for UX feedback and OpenAPI example clarity
    animation_type: Optional[str] = Field(default=None, description="애니메이션 타입: normal|epic|legendary|near_miss|pity")
    psychological_message: Optional[str] = Field(default=None, description="즉시 피드백용 메시지")
    message: str
    feedback: Optional[Dict[str, Any]] = None
    currency_balance: Dict[str, int]
    net_change: Optional[int] = Field(default=None, description="토큰 순 변화량 (뽑기 비용 합산 반영)")
    # OpenAPI 예시
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "items": [
                {"name": "Neon Chip", "rarity": "common"},
                {"name": "Cyber Ring", "rarity": "rare"},
                {"name": "Blade of Flux", "rarity": "epic"}
            ],
            "rare_item_count": 1,
            "ultra_rare_item_count": 1,
            "pull_count": 10,
            "balance": 12345,
            "special_animation": None,
            "animation_type": "near_miss",
            "psychological_message": "거의 다 왔어요! 한 번만 더 도전해보세요!",
            "message": "Gacha pull completed",
            "currency_balance": {"tokens": 11895, "gems": 0}
        }
    })


# 크래시 게임 스키마
class CrashBetRequest(BaseModel):
    """크래시 게임 베팅 요청 모델"""
    bet_amount: int
    auto_cashout_multiplier: Optional[float] = None


class CrashBetResponse(BaseModel):
    """크래시 게임 베팅 응답 모델"""
    success: bool
    game_id: str
    bet_amount: int
    potential_win: int
    max_multiplier: Optional[float] = None
    message: str
    balance: int
    status: Optional[str] = Field(default=None, description="베팅 직후 상태 placed|auto_cashed|active 등")
    simulated_max_win: Optional[int] = Field(default=None, description="UI 표시용 – 현재 multiplier 기반 가상의 최대 승리금 (auto_cashout 미지정 시 안내)")
