"""Redis 유틸: streak 등에서 사용하는 저수준 접근 헬퍼.

기존 상위 로직(update_streak_counter 등)은 이미 import 되어 있음.
여기서는 streak.py에서 직접 호출하는 get_redis() 심플 구현을 제공하여
ImportError를 제거하고, 연결 실패시 None 반환(가용성 우선) 전략 적용.
"""
from __future__ import annotations
import os
import logging
from functools import lru_cache
from typing import Optional

try:
    import redis  # type: ignore
except ImportError:  # pragma: no cover
    redis = None  # type: ignore

logger = logging.getLogger(__name__)

REDIS_URL_ENV_KEYS = [
    "REDIS_URL",
    "REDIS_DSN",
    "REDIS_CONNECTION_STRING",
]


def _discover_url() -> Optional[str]:
    for k in REDIS_URL_ENV_KEYS:
        v = os.getenv(k)
        if v:
            return v
    host = os.getenv("REDIS_HOST", "redis")
    port = os.getenv("REDIS_PORT", "6379")
    password = os.getenv("REDIS_PASSWORD")
    if password:
        return f"redis://:{password}@{host}:{port}/0"
    return f"redis://{host}:{port}/0"


@lru_cache(maxsize=1)
def get_redis():  # 반환 타입 Optional[redis.Redis]
    """Lazy Redis 클라이언트.

    실패 시 예외를 올리지 않고 None 반환하여 호출측에서 graceful degrade.
    """
    if redis is None:  # pragma: no cover
        logger.warning("redis-py 미설치 상태 - get_redis() -> None")
        return None
    url = _discover_url()
    try:
        client = redis.Redis.from_url(url, decode_responses=True)  # type: ignore
        # 가벼운 ping으로 연결 검증 (0.2s 타임아웃)
        try:
            client.ping()
        except Exception:
            logger.warning("Redis ping 실패 - None 반환", exc_info=True)
            return None
        return client
    except Exception:  # pragma: no cover
        logger.warning("Redis 클라이언트 생성 실패", exc_info=True)
        return None


# 기존 streak 유틸 함수 (update_streak_counter 등)이 다른 파일에 정의되어 있는 경우
# 이 파일은 단순히 get_redis 제공 목적. 중복 정의 피하기 위해 추가 구현 불필요.
"""
Redis 유틸리티 함수들
- 사용자 데이터 캐싱
- 세션 관리
- 스트릭 카운터
- 실시간 데이터 저장
"""

import json
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RedisManager:
    """Redis 연결 및 데이터 관리 클래스"""
    
    def __init__(self, redis_client: Any = None):
        """
        Redis 매니저 초기화
        
        Args:
            redis_client: Redis 클라이언트 인스턴스
        """
        self.redis_client = redis_client
        self._fallback_cache = {}  # Redis 연결 실패시 임시 메모리 캐시
    
    def is_connected(self) -> bool:
        """Redis 연결 상태 확인"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
        except Exception as e:
            logger.warning(f"Redis connection failed: {str(e)}")
        return False
    
    def cache_user_data(self, user_id: str, data: Dict[str, Any], 
                       expire_seconds: int = 3600) -> bool:
        """
        사용자 데이터 캐싱
        
        Args:
            user_id: 사용자 ID
            data: 캐시할 데이터
            expire_seconds: 만료 시간 (초)
        
        Returns:
            캐싱 성공 여부
        """
        try:
            key = f"user:{user_id}:data"
            
            if self.is_connected():
                serialized_data = json.dumps(data, default=str)
                result = self.redis_client.setex(key, expire_seconds, serialized_data)
                return bool(result)
            else:
                # Fallback to memory cache
                self._fallback_cache[key] = {
                    "data": data,
                    "expires_at": datetime.utcnow() + timedelta(seconds=expire_seconds)
                }
                return True
                
        except Exception as e:
            logger.error(f"Failed to cache user data: {str(e)}")
            return False
    
    def get_cached_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        캐시된 사용자 데이터 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            캐시된 데이터 또는 None
        """
        try:
            key = f"user:{user_id}:data"
            
            if self.is_connected():
                cached_data = self.redis_client.get(key)
                if cached_data:
                    return json.loads(cached_data.decode('utf-8'))
            else:
                # Check fallback cache
                cached_item = self._fallback_cache.get(key)
                if cached_item and cached_item["expires_at"] > datetime.utcnow():
                    return cached_item["data"]
                elif cached_item:
                    # Remove expired item
                    del self._fallback_cache[key]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached data: {str(e)}")
            return None
    
    def update_streak_counter(self, user_id: str, action_type: str, 
                             increment: bool = True) -> int:
        """
        사용자 스트릭 카운터 업데이트
        
        Args:
            user_id: 사용자 ID
            action_type: 액션 타입 (SLOT_SPIN, GACHA_PULL 등)
            increment: 증가(True) 또는 리셋(False)
        
        Returns:
            현재 스트릭 카운트
        """
        try:
            key = f"user:{user_id}:streak:{action_type}"
            
            if self.is_connected():
                if increment:
                    current_count = self.redis_client.incr(key)
                    # 24시간 만료 설정
                    self.redis_client.expire(key, 86400)
                else:
                    # 스트릭 리셋
                    self.redis_client.delete(key)
                    current_count = 0
                
                return current_count
            else:
                # Fallback to memory cache
                if increment:
                    current_count = self._fallback_cache.get(key, 0) + 1
                    self._fallback_cache[key] = current_count
                else:
                    self._fallback_cache[key] = 0
                    current_count = 0
                
                return current_count
                
        except Exception as e:
            logger.error(f"Failed to update streak counter: {str(e)}")
            return 0

    def get_streak_counter(self, user_id: str, action_type: str) -> int:
        """현재 스트릭 카운트 조회 (없으면 0)"""
        try:
            key = f"user:{user_id}:streak:{action_type}"
            if self.is_connected():
                val = self.redis_client.get(key)
                return int(val) if val is not None else 0
            else:
                return int(self._fallback_cache.get(key, 0))
        except Exception:
            return 0

    def get_streak_ttl(self, user_id: str, action_type: str) -> Optional[int]:
        """스트릭 남은 TTL(초). 연결 안되면 대략적 추정 불가로 None"""
        try:
            key = f"user:{user_id}:streak:{action_type}"
            if self.is_connected():
                ttl = self.redis_client.ttl(key)
                return int(ttl) if ttl and ttl > 0 else None
            return None
        except Exception:
            return None

    # -------------------------------
    # Attendance (출석) 기록/조회
    # -------------------------------
    def record_attendance_day(self, user_id: str, action_type: str, day_iso: str) -> bool:
        """
        특정 일자 출석 기록

        Args:
            user_id: 사용자 ID
            action_type: 액션 타입 (예: DAILY_LOGIN)
            day_iso: 'YYYY-MM-DD' 형식의 날짜 문자열

        Note:
            월 단위 키에 SADD로 보관. 키 만료는 120일로 설정.
        """
        try:
            month_key = day_iso[:7].replace('-', '')  # YYYYMM
            key = f"user:{user_id}:attendance:{action_type}:{month_key}"
            if self.is_connected():
                # SADD 로 날짜 문자열 저장
                self.redis_client.sadd(key, day_iso)
                # 120일 만료 (보수적으로 길게)
                self.redis_client.expire(key, 60 * 60 * 24 * 120)
                return True
            else:
                # Fallback set in memory
                s = self._fallback_cache.get(key)
                if not isinstance(s, set):
                    s = set()
                s.add(day_iso)
                self._fallback_cache[key] = s
                return True
        except Exception as e:
            logger.error(f"Failed to record attendance: {str(e)}")
            return False

    def get_attendance_month(self, user_id: str, action_type: str, year: int, month: int) -> List[str]:
        """
        해당 연/월의 출석 날짜 목록 반환 (YYYY-MM-DD 문자열 리스트)
        """
        try:
            month_key = f"{year:04d}{month:02d}"
            key = f"user:{user_id}:attendance:{action_type}:{month_key}"
            if self.is_connected():
                members = self.redis_client.smembers(key)
                # redis-py returns set[bytes|str]; decode if bytes
                result = []
                for m in members or []:
                    if isinstance(m, bytes):
                        result.append(m.decode('utf-8'))
                    else:
                        result.append(str(m))
                return sorted(result)
            else:
                s = self._fallback_cache.get(key, set())
                return sorted(list(s)) if isinstance(s, set) else []
        except Exception as e:
            logger.error(f"Failed to get attendance month: {str(e)}")
            return []

    # -------------------------------
    # Streak Protection 토글 저장
    # -------------------------------
    def get_streak_protection(self, user_id: str, action_type: str) -> bool:
        """스트릭 보호 토글 상태 조회 (True/False)"""
        try:
            key = f"user:{user_id}:streak_protection:{action_type}"
            if self.is_connected():
                val = self.redis_client.get(key)
                if val is None:
                    return False
                if isinstance(val, bytes):
                    val = val.decode('utf-8')
                return val == '1' or str(val).lower() == 'true'
            else:
                val = self._fallback_cache.get(key, '0')
                if isinstance(val, bool):
                    return val
                return str(val) == '1'
        except Exception as e:
            logger.error(f"Failed to get streak protection: {str(e)}")
            return False

    def set_streak_protection(self, user_id: str, action_type: str, enabled: bool) -> bool:
        """스트릭 보호 토글 상태 설정"""
        try:
            key = f"user:{user_id}:streak_protection:{action_type}"
            val = '1' if enabled else '0'
            if self.is_connected():
                self.redis_client.set(key, val)
                return True
            else:
                self._fallback_cache[key] = enabled
                return True
        except Exception as e:
            logger.error(f"Failed to set streak protection: {str(e)}")
            return False
    
    def manage_session_data(self, session_id: str, data: Optional[Dict[str, Any]] = None, 
                           delete: bool = False) -> Optional[Dict[str, Any]]:
        """
        세션 데이터 관리 (생성/조회/삭제)
        
        Args:
            session_id: 세션 ID
            data: 저장할 데이터 (None이면 조회)
            delete: 삭제 여부
        
        Returns:
            세션 데이터 또는 None
        """
        try:
            key = f"session:{session_id}"
            
            if delete:
                # 세션 삭제
                if self.is_connected():
                    self.redis_client.delete(key)
                else:
                    self._fallback_cache.pop(key, None)
                return None
            
            if data is not None:
                # 세션 데이터 저장
                if self.is_connected():
                    serialized_data = json.dumps(data, default=str)
                    self.redis_client.setex(key, 3600, serialized_data)  # 1시간 만료
                else:
                    self._fallback_cache[key] = {
                        "data": data,
                        "expires_at": datetime.utcnow() + timedelta(hours=1)
                    }
                return data
            else:
                # 세션 데이터 조회
                if self.is_connected():
                    cached_data = self.redis_client.get(key)
                    if cached_data:
                        return json.loads(cached_data.decode('utf-8'))
                else:
                    cached_item = self._fallback_cache.get(key)
                    if cached_item and cached_item["expires_at"] > datetime.utcnow():
                        return cached_item["data"]
                    elif cached_item:
                        del self._fallback_cache[key]
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to manage session data: {str(e)}")
            return None
    
    def store_temp_data(self, key: str, data: Any, expire_seconds: int = 300) -> bool:
        """
        임시 데이터 저장 (기본 5분 만료)
        
        Args:
            key: 저장 키
            data: 저장할 데이터
            expire_seconds: 만료 시간 (초)
        
        Returns:
            저장 성공 여부
        """
        try:
            if self.is_connected():
                serialized_data = json.dumps(data, default=str)
                result = self.redis_client.setex(key, expire_seconds, serialized_data)
                return bool(result)
            else:
                self._fallback_cache[key] = {
                    "data": data,
                    "expires_at": datetime.utcnow() + timedelta(seconds=expire_seconds)
                }
                return True
                
        except Exception as e:
            logger.error(f"Failed to store temp data: {str(e)}")
            return False
    
    def get_temp_data(self, key: str) -> Optional[Any]:
        """
        임시 데이터 조회
        
        Args:
            key: 조회 키
        
        Returns:
            저장된 데이터 또는 None
        """
        try:
            if self.is_connected():
                cached_data = self.redis_client.get(key)
                if cached_data:
                    return json.loads(cached_data.decode('utf-8'))
            else:
                cached_item = self._fallback_cache.get(key)
                if cached_item and cached_item["expires_at"] > datetime.utcnow():
                    return cached_item["data"]
                elif cached_item:
                    del self._fallback_cache[key]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get temp data: {str(e)}")
            return None
    
    def clean_expired_cache(self):
        """만료된 메모리 캐시 정리"""
        try:
            current_time = datetime.utcnow()
            expired_keys = [
                key for key, value in self._fallback_cache.items()
                if isinstance(value, dict) and 
                value.get("expires_at", current_time) <= current_time
            ]
            
            for key in expired_keys:
                del self._fallback_cache[key]
            
            logger.info(f"Cleaned {len(expired_keys)} expired cache entries")
            
        except Exception as e:
            logger.error(f"Failed to clean expired cache: {str(e)}")

# 전역 Redis 매니저 인스턴스
redis_manager = None

def init_redis_manager(redis_client: Any = None):
    """Redis 매니저 초기화"""
    global redis_manager
    redis_manager = RedisManager(redis_client)

def get_redis_manager() -> RedisManager:
    """Redis 매니저 인스턴스 반환"""
    global redis_manager
    if redis_manager is None:
        redis_manager = RedisManager()
    return redis_manager

# 편의 함수들
def cache_user_data(user_id: str, data: Dict[str, Any], expire_seconds: int = 3600) -> bool:
    """사용자 데이터 캐싱 (편의 함수)"""
    return get_redis_manager().cache_user_data(user_id, data, expire_seconds)

def get_cached_data(user_id: str) -> Optional[Dict[str, Any]]:
    """캐시된 사용자 데이터 조회 (편의 함수)"""
    return get_redis_manager().get_cached_data(user_id)

def update_streak_counter(user_id: str, action_type: str, increment: bool = True) -> int:
    """스트릭 카운터 업데이트 (편의 함수)"""
    return get_redis_manager().update_streak_counter(user_id, action_type, increment)

def get_streak_counter(user_id: str, action_type: str) -> int:
    """스트릭 카운터 조회 (편의 함수)"""
    return get_redis_manager().get_streak_counter(user_id, action_type)

def get_streak_ttl(user_id: str, action_type: str) -> Optional[int]:
    """스트릭 TTL 조회 (편의 함수)"""
    return get_redis_manager().get_streak_ttl(user_id, action_type)

def manage_session_data(session_id: str, data: Optional[Dict[str, Any]] = None, 
                       delete: bool = False) -> Optional[Dict[str, Any]]:
    """세션 데이터 관리 (편의 함수)"""
    return get_redis_manager().manage_session_data(session_id, data, delete)

# Attendance / Protection 편의 함수
def record_attendance_day(user_id: str, action_type: str, day_iso: str) -> bool:
    return get_redis_manager().record_attendance_day(user_id, action_type, day_iso)

def get_attendance_month(user_id: str, action_type: str, year: int, month: int) -> List[str]:
    return get_redis_manager().get_attendance_month(user_id, action_type, year, month)

def get_streak_protection(user_id: str, action_type: str) -> bool:
    return get_redis_manager().get_streak_protection(user_id, action_type)

def set_streak_protection(user_id: str, action_type: str, enabled: bool) -> bool:
    return get_redis_manager().set_streak_protection(user_id, action_type, enabled)