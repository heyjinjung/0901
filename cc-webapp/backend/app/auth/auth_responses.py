"""
Casino-Club F2P - Standardized Auth Response Models
=============================================================================
Standardized response models for authentication endpoints
Ensures consistent response formats across all auth APIs
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class TokenResponse(BaseModel):
    """Standard response for token operations"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user_info: Optional[Dict[str, Any]] = None


class AuthErrorResponse(BaseModel):
    """Standard error response for auth operations"""
    error: str
    error_description: str
    status_code: int = 401


class LoginResponse(BaseModel):
    """Response for login operations"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    nickname: str
    vip_tier: str
    cyber_tokens: int


class UserProfileResponse(BaseModel):
    """Response for user profile operations"""
    user_id: int
    site_id: str
    nickname: str
    email: Optional[str] = None
    vip_tier: str
    battlepass_level: int
    cyber_tokens: int
    created_at: str
    last_login: Optional[str] = None
    

class SessionInfoResponse(BaseModel):
    """Response for session information"""
    session_id: str
    device_info: str
    ip_address: str
    created_at: str
    expires_at: str
    is_current: bool


class SessionsListResponse(BaseModel):
    """Response for listing user sessions"""
    active_sessions: List[SessionInfoResponse]
    total_count: int
