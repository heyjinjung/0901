"""
Casino-Club F2P - Enhanced Token Management System
=============================================================================
Comprehensive token management system for JWT access and refresh tokens
Features:
- Access token generation, validation, and blacklisting
- Refresh token management with secure rotation
- Token revocation and expiration handling
- Session-aware token tracking
- Redis-based token blacklist with memory fallback
"""

import os
from jose import jwt as PyJWT
import uuid
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import JWTError

logger = logging.getLogger("token_manager")

# ===== Environment Settings =====
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "casino-club-secret-key-2024")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))


class TokenManager:
    """Enhanced token management system for Casino-Club F2P"""
    
    @staticmethod
    def create_access_token(
        user_id: int, 
        session_id: str = None,
        additional_claims: Dict[str, Any] = None
    ) -> str:
        """
        Create a new JWT access token with proper claims and expiration.
        
        Args:
            user_id: User identifier
            session_id: Optional session ID to bind token to session
            additional_claims: Any additional claims to include in token
            
        Returns:
            Encoded JWT access token string
        """
        expires_delta = timedelta(minutes=JWT_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta
        
        # Basic claims
        claims = {
            "sub": str(user_id),
            "exp": expire.timestamp(),
            "iat": datetime.utcnow().timestamp(),
            "jti": str(uuid.uuid4()),  # Unique token identifier
            "type": "access"
        }
        
        # Add session ID if provided
        if session_id:
            claims["sid"] = session_id
        
        # Add any additional claims
        if additional_claims:
            claims.update(additional_claims)
        
        # Create token with claims
        token = PyJWT.encode(claims, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        
        logger.debug(f"Created access token for user {user_id}, expires: {expire}")
        return token
    
    @staticmethod
    def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT access token.
        
        Args:
            token: JWT token string to verify
            
        Returns:
            Decoded payload if token is valid, None otherwise
        """
        try:
            # First verify the token is not blacklisted
            if TokenManager.is_token_blacklisted(token):
                logger.warning("Token is blacklisted")
                return None
            
            # Decode and verify token
            payload = PyJWT.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Verify token type
            if payload.get("type") != "access":
                logger.warning("Token is not an access token")
                return None
                
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {str(e)}")
            return None
    
    @staticmethod
    def create_refresh_token(
        user_id: int, 
        ip_address: str,
        user_agent: str,
        db: Session
    ) -> str:
        """
        Create a new refresh token and store its hash in the database.
        
        Args:
            user_id: User identifier
            ip_address: Client IP address
            user_agent: Client user agent string
            db: Database session
            
        Returns:
            Generated refresh token string
        """
        try:
            from ..models.auth_models import RefreshToken

            # Generate a secure random token
            refresh_token = secrets.token_hex(32)

            # Determine storage strategy by model columns
            has_token_hash = hasattr(RefreshToken, 'token_hash')
            has_is_active = hasattr(RefreshToken, 'is_active')
            has_device_fingerprint = hasattr(RefreshToken, 'device_fingerprint')
            has_ip = hasattr(RefreshToken, 'ip_address')
            has_ua = hasattr(RefreshToken, 'user_agent')

            # Common fields
            expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            kwargs = {
                'user_id': user_id,
                'expires_at': expires_at,
                'created_at': datetime.utcnow(),
            }

            if has_token_hash:
                token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
                kwargs['token_hash'] = token_hash
            else:
                kwargs['token'] = refresh_token

            if has_is_active:
                kwargs['is_active'] = True
            else:
                # legacy schema uses is_revoked flag
                if hasattr(RefreshToken, 'is_revoked'):
                    kwargs['is_revoked'] = False

            if has_device_fingerprint:
                kwargs['device_fingerprint'] = hashlib.sha256(f"{user_agent}:{ip_address}".encode()).hexdigest()
            if has_ip:
                kwargs['ip_address'] = ip_address
            if has_ua:
                kwargs['user_agent'] = user_agent

            refresh_token_record = RefreshToken(**kwargs)
            db.add(refresh_token_record)
            db.commit()

            logger.info(f"Refresh token created for user {user_id}, expires: {expires_at}")
            return refresh_token

        except Exception as e:
            logger.error(f"Failed to create refresh token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="토큰 생성 중 오류가 발생했습니다"
            )
    
    @staticmethod
    def verify_refresh_token(
        refresh_token: str, 
        ip_address: str, 
        user_agent: str, 
        db: Session
    ) -> Tuple[bool, Optional[int], str]:
        """
        Verify a refresh token and return user ID if valid.
        
        Args:
            refresh_token: Refresh token to verify
            ip_address: Client IP address
            user_agent: Client user agent string
            db: Database session
            
        Returns:
            Tuple of (is_valid, user_id, error_message)
        """
        try:
            from ..models.auth_models import RefreshToken

            has_token_hash = hasattr(RefreshToken, 'token_hash')
            has_is_active = hasattr(RefreshToken, 'is_active')
            has_is_revoked = hasattr(RefreshToken, 'is_revoked')
            has_device_fingerprint = hasattr(RefreshToken, 'device_fingerprint')

            q = db.query(RefreshToken)
            if has_token_hash:
                token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
                q = q.filter(RefreshToken.token_hash == token_hash)
            else:
                q = q.filter(RefreshToken.token == refresh_token)

            # Active/not revoked
            if has_is_active:
                q = q.filter(RefreshToken.is_active == True)
            elif has_is_revoked:
                q = q.filter(RefreshToken.is_revoked == False)

            # Not expired
            q = q.filter(RefreshToken.expires_at > datetime.utcnow())

            refresh_record = q.first()

            if not refresh_record:
                # Distinguish between: token exists but revoked vs does not exist
                # For legacy schema we can attempt a lighter lookup ignoring revoked filter to see if it was revoked.
                try:
                    from ..models.auth_models import RefreshToken as RT2
                    probe_q = db.query(RT2)
                    if has_token_hash:
                        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
                        probe_q = probe_q.filter(RT2.token_hash == token_hash)
                    else:
                        probe_q = probe_q.filter(RT2.token == refresh_token)
                    probe = probe_q.first()
                    if probe is not None:
                        # It matched but failed active/not revoked filter → treat as reuse of revoked token
                        logger.warning(f"Reuse of revoked refresh token from {ip_address}")
                        return False, None, "REVOKED"
                except Exception:
                    pass
                logger.warning(f"Invalid refresh token attempt from {ip_address}")
                return False, None, "유효하지 않은 리프레시 토큰입니다"

            # Optional device fingerprint check
            if has_device_fingerprint:
                device_fingerprint = hashlib.sha256(f"{user_agent}:{ip_address}".encode()).hexdigest()
                if getattr(refresh_record, 'device_fingerprint', None) and refresh_record.device_fingerprint != device_fingerprint:
                    logger.warning(f"Device fingerprint mismatch for user {refresh_record.user_id}")

            return True, refresh_record.user_id, ""

        except Exception as e:
            logger.error(f"Refresh token verification failed: {str(e)}")
            return False, None, "토큰 검증 중 오류가 발생했습니다"
    
    @staticmethod
    def rotate_refresh_token(
        current_token: str,
        user_id: int,
        ip_address: str,
        user_agent: str,
        db: Session
    ) -> Optional[str]:
        """
        Rotate a refresh token - invalidate current token and create a new one.
        
        Args:
            current_token: Current refresh token to invalidate
            user_id: User identifier
            ip_address: Client IP address
            user_agent: Client user agent string
            db: Database session
            
        Returns:
            New refresh token string
        """
        try:
            from ..models.auth_models import RefreshToken

            has_token_hash = hasattr(RefreshToken, 'token_hash')
            has_is_active = hasattr(RefreshToken, 'is_active')
            has_is_revoked = hasattr(RefreshToken, 'is_revoked')

            q = db.query(RefreshToken)
            if has_token_hash:
                current_token_hash = hashlib.sha256(current_token.encode()).hexdigest()
                q = q.filter(RefreshToken.token_hash == current_token_hash)
            else:
                q = q.filter(RefreshToken.token == current_token)

            current_record = q.first()
            if current_record:
                if has_is_active:
                    current_record.is_active = False
                elif has_is_revoked:
                    current_record.is_revoked = True
                # optional audit fields
                if hasattr(current_record, 'revoked_at'):
                    current_record.revoked_at = datetime.utcnow()
                if hasattr(current_record, 'revoke_reason'):
                    current_record.revoke_reason = 'token_rotation'
                db.commit()

            # Create new refresh token
            new_token = TokenManager.create_refresh_token(
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                db=db
            )

            logger.info(f"Rotated refresh token for user {user_id}")
            return new_token

        except Exception as e:
            logger.error(f"Token rotation failed: {str(e)}")
            return None

    @staticmethod
    def revoke_refresh_token(refresh_token: str, db: Session) -> bool:
        """Revoke a single refresh token if present."""
        try:
            from ..models.auth_models import RefreshToken
            has_token_hash = hasattr(RefreshToken, 'token_hash')
            has_is_active = hasattr(RefreshToken, 'is_active')
            has_is_revoked = hasattr(RefreshToken, 'is_revoked')

            q = db.query(RefreshToken)
            if has_token_hash:
                token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
                q = q.filter(RefreshToken.token_hash == token_hash)
            else:
                q = q.filter(RefreshToken.token == refresh_token)

            rec = q.first()
            if not rec:
                return False
            if has_is_active:
                rec.is_active = False
            elif has_is_revoked:
                rec.is_revoked = True
            if hasattr(rec, 'revoked_at'):
                rec.revoked_at = datetime.utcnow()
            if hasattr(rec, 'revoke_reason'):
                rec.revoke_reason = 'logout'
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to revoke refresh token: {e}")
            return False

    @staticmethod
    def revoke_all_refresh_tokens(user_id: int, db: Session) -> int:
        """Revoke all refresh tokens for a given user."""
        try:
            from ..models.auth_models import RefreshToken
            has_is_active = hasattr(RefreshToken, 'is_active')
            has_is_revoked = hasattr(RefreshToken, 'is_revoked')

            q = db.query(RefreshToken).filter(RefreshToken.user_id == user_id)
            tokens = q.all()
            count = 0
            for rec in tokens:
                changed = False
                if has_is_active and getattr(rec, 'is_active', None) is not False:
                    rec.is_active = False
                    changed = True
                elif has_is_revoked and getattr(rec, 'is_revoked', None) is not True:
                    rec.is_revoked = True
                    changed = True
                if changed:
                    if hasattr(rec, 'revoked_at'):
                        rec.revoked_at = datetime.utcnow()
                    if hasattr(rec, 'revoke_reason'):
                        rec.revoke_reason = 'logout_all'
                    count += 1
            if count:
                db.commit()
            return count
        except Exception as e:
            logger.error(f"Failed to revoke all refresh tokens: {e}")
            return 0
    
    @staticmethod
    def blacklist_token(token: str, reason: str = "logout") -> bool:
        """
        Add a token to the blacklist to invalidate it.
        
        Args:
            token: JWT token to blacklist
            reason: Reason for blacklisting
            
        Returns:
            True if blacklisting succeeded, False otherwise
        """
        try:
            # Extract JWT ID from token
            try:
                payload = PyJWT.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                jti = payload.get("jti")
                exp = payload.get("exp")
                
                if not jti:
                    logger.warning("Token has no JTI, cannot blacklist")
                    return False
                    
            except JWTError as e:
                logger.warning(f"Cannot decode token for blacklisting: {e}")
                return False
            
            # Try Redis first, fall back to memory
            try:
                import redis
                redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
                
                # Store until token expiration
                expire_time = datetime.fromtimestamp(exp) - datetime.utcnow()
                if expire_time.total_seconds() > 0:
                    redis_client.setex(
                        f"blacklist_token:{jti}",
                        int(expire_time.total_seconds()),
                        reason
                    )
                    logger.info(f"Token {jti} blacklisted in Redis for {reason}")
                    return True
                else:
                    logger.info(f"Token {jti} already expired, no need to blacklist")
                    return True
                    
            except Exception as redis_error:
                logger.warning(f"Redis not available, using memory fallback: {redis_error}")
                # Memory fallback
                if not hasattr(TokenManager, '_memory_blacklist'):
                    TokenManager._memory_blacklist = {}
                    
                TokenManager._memory_blacklist[jti] = {
                    'reason': reason,
                    'expires_at': exp
                }
                logger.info(f"Token {jti} blacklisted in memory for {reason}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
            return False
    
    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        """
        Check if a token is in the blacklist.
        
        Args:
            token: JWT token to check
            
        Returns:
            True if token is blacklisted, False otherwise
        """
        try:
            # Extract JWT ID
            try:
                payload = PyJWT.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                jti = payload.get("jti")
                
                if not jti:
                    return False
                    
            except JWTError:
                return True  # Invalid tokens are considered blacklisted
            
            # Check Redis first, fall back to memory
            try:
                import redis
                redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
                
                blacklisted = redis_client.exists(f"blacklist_token:{jti}")
                if blacklisted:
                    logger.info(f"Token {jti} found in Redis blacklist")
                    return True
                    
            except Exception as redis_error:
                logger.warning(f"Redis not available, checking memory fallback: {redis_error}")
                # Check memory fallback
                if hasattr(TokenManager, '_memory_blacklist'):
                    if jti in TokenManager._memory_blacklist:
                        # Check if token has expired
                        exp = TokenManager._memory_blacklist[jti]['expires_at']
                        if datetime.utcnow().timestamp() < exp:
                            logger.info(f"Token {jti} found in memory blacklist")
                            return True
                        else:
                            # Clean up expired token
                            del TokenManager._memory_blacklist[jti]
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {e}")
            return False  # Error case, allow token (prioritize availability)
    
    @staticmethod
    def get_token_payload(token: str) -> Optional[Dict[str, Any]]:
        """
        Safely extract payload from a token without validation.
        
        Args:
            token: JWT token
            
        Returns:
            Decoded payload or None
        """
        try:
            # Decode without verification (just to read payload)
            payload = PyJWT.decode(token, options={"verify_signature": False})
            return payload
        except Exception as e:
            logger.error(f"Failed to decode token payload: {e}")
            return None
