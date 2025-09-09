"""리프레시 토큰 요청 스키마"""
from pydantic import BaseModel

class RefreshTokenRequest(BaseModel):
    """리프레시 토큰 요청"""
    refresh_token: str

class LogoutRequest(BaseModel):
    """로그아웃 요청"""
    refresh_token: str
