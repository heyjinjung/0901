"""
🎰 Casino-Club F2P - Repository Layer
====================================
데이터 액세스 레이어 모듈

📅 작성일: 2025-08-03
🎯 목적: Repository 패턴 구현 - 완전히 구현됨
"""

from .base_repository import BaseRepository
from .user_repository import UserRepository
from .auth_repository import AuthRepository
from .game_repository import GameRepository
from .mission_repository import MissionRepository
from .shop_repository import ShopRepository
from .analytics_repository import AnalyticsRepository

__all__ = [
    "BaseRepository",
    "UserRepository", 
    "AuthRepository",
    "GameRepository",
    "MissionRepository",
    "ShopRepository",
    "AnalyticsRepository"
]

# Repository Factory 클래스
class RepositoryFactory:
    """Repository Factory 클래스"""
    
    def __init__(self, db):
        self.db = db
        self._user_repo = None
        self._auth_repo = None
        self._game_repo = None
        self._mission_repo = None
        self._shop_repo = None
        self._analytics_repo = None
    
    @property
    def user(self) -> UserRepository:
        if self._user_repo is None:
            self._user_repo = UserRepository(self.db)
        return self._user_repo
    
    @property
    def auth(self) -> AuthRepository:
        if self._auth_repo is None:
            self._auth_repo = AuthRepository(self.db)
        return self._auth_repo
    
    @property
    def game(self) -> GameRepository:
        if self._game_repo is None:
            self._game_repo = GameRepository(self.db)
        return self._game_repo
    
    @property
    def mission(self) -> MissionRepository:
        if self._mission_repo is None:
            self._mission_repo = MissionRepository(self.db)
        return self._mission_repo
    
    @property
    def shop(self) -> ShopRepository:
        if self._shop_repo is None:
            self._shop_repo = ShopRepository(self.db)
        return self._shop_repo
    
    @property
    def analytics(self) -> AnalyticsRepository:
        if self._analytics_repo is None:
            self._analytics_repo = AnalyticsRepository(self.db)
        return self._analytics_repo

# 의존성 주입을 위한 팩토리 함수
def get_repository_factory(db):
    """Repository Factory 인스턴스 생성"""
    return RepositoryFactory(db)