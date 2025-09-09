"""
🎰 Casino-Club F2P - API 인증 라우터 (Auth API Router)
========================================================
Frontend와 Database를 연결하는 실제 API 엔드포인트

✅ 이 파일 하나만으로 프론트엔드/데이터베이스/API 모든 연동 가능!
✅ auth_service.py와 함께 완전한 인증 시스템 구성
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from ...database import get_db
from ...auth.auth_service import AuthService
from ...models.auth_models import User

# ===== API Router 설정 =====
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# ===== Pydantic Schemas =====
class UserRegisterRequest(BaseModel):
    """회원가입 요청"""
    invite_code: str = Field(..., min_length=4, max_length=10, description="초대코드")
    nickname: str = Field(..., min_length=2, max_length=50, description="닉네임")
    site_id: str = Field(..., min_length=4, max_length=50, description="사이트 아이디")
    phone_number: str = Field(..., min_length=10, max_length=20, description="전화번호")
    password: str = Field(..., min_length=6, description="비밀번호")

class UserLoginRequest(BaseModel):
    """로그인 요청"""
    site_id: str = Field(..., description="사이트 아이디")
    password: str = Field(..., description="비밀번호")
    device_info: Optional[str] = Field(None, description="디바이스 정보")

class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

class UserProfileResponse(BaseModel):
    """사용자 프로필 응답"""
    id: int
    site_id: str
    nickname: str
    phone_number: str
    cyber_token_balance: int
    is_active: bool
    is_admin: bool
    avatar_url: Optional[str]
    bio: Optional[str]
    created_at: str
    last_login: Optional[str]

# ===== API 엔드포인트 =====

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: UserRegisterRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    🎯 회원가입 API
    - 초대코드로 즉시 가입
    - 자동 로그인 처리
    - JWT 토큰 발급
    """
    try:
        # 디바이스 정보 생성
        device_info = f"{http_request.client.host}_{http_request.headers.get('user-agent', '')[:100]}"
        
        # AuthService를 통한 회원가입
        result = AuthService.register_user(
            db=db,
            invite_code=request.invite_code,
            nickname=request.nickname,
            site_id=request.site_id,
            phone_number=request.phone_number,
            password=request.password,
            device_info=device_info
        )
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            expires_in=3600
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="회원가입 처리 중 오류가 발생했습니다."
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    request: UserLoginRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    🎯 로그인 API
    - 사이트 아이디 + 비밀번호 로그인
    - JWT 토큰 발급
    - 세션 관리
    """
    try:
        # 디바이스 정보 생성
        device_info = request.device_info or f"{http_request.client.host}_{http_request.headers.get('user-agent', '')[:100]}"
        
        # AuthService를 통한 로그인
        result = AuthService.login_user(
            db=db,
            site_id=request.site_id,
            password=request.password,
            device_info=device_info
        )
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            expires_in=3600
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 오류가 발생했습니다."
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    🎯 토큰 갱신 API
    - 리프레시 토큰으로 새 액세스 토큰 발급
    """
    try:
        result = AuthService.refresh_access_token(db=db, refresh_token=refresh_token)
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=refresh_token,  # 기존 리프레시 토큰 유지
            expires_in=3600
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.get("/me", response_model=UserProfileResponse)
async def get_current_user(
    current_user: User = Depends(AuthService.get_current_user_dependency)
):
    """
    🎯 현재 사용자 정보 API
    - JWT 토큰으로 사용자 정보 조회
    - 프론트엔드에서 사용자 상태 확인용
    """
    return UserProfileResponse(
        id=current_user.id,
        site_id=current_user.site_id,
        nickname=current_user.nickname,
        phone_number=current_user.phone_number,
        cyber_token_balance=current_user.cyber_token_balance,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        created_at=current_user.created_at.isoformat() if current_user.created_at else "",
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )

@router.post("/logout")
async def logout_user(
    current_user: User = Depends(AuthService.get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    🎯 로그아웃 API
    - 현재 세션 종료
    - 토큰 블랙리스트 처리
    """
    try:
        AuthService.logout_user(db=db, user_id=current_user.id)
        return {"message": "성공적으로 로그아웃되었습니다."}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그아웃 처리 중 오류가 발생했습니다."
        )

@router.post("/logout-all")
async def logout_all_sessions(
    current_user: User = Depends(AuthService.get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    🎯 모든 세션 로그아웃 API
    - 모든 디바이스에서 로그아웃
    - 모든 토큰 무효화
    """
    try:
        AuthService.logout_all_sessions(db=db, user_id=current_user.id)
        return {"message": "모든 세션에서 성공적으로 로그아웃되었습니다."}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="전체 로그아웃 처리 중 오류가 발생했습니다."
        )

@router.get("/check-invite/{code}")
async def check_invite_code(
    code: str,
    db: Session = Depends(get_db)
):
    """
    🎯 초대코드 확인 API
    - 초대코드 유효성 검증
    - 회원가입 전 사전 확인용
    """
    try:
        is_valid = AuthService.validate_invite_code(db=db, invite_code=code)
        return {
            "code": code,
            "is_valid": is_valid,
            "message": "사용 가능한 초대코드입니다." if is_valid else "유효하지 않은 초대코드입니다."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="초대코드 확인 중 오류가 발생했습니다."
        )

# ===== 관리자 전용 엔드포인트 =====

@router.post("/admin/create-invite")
async def create_invite_code(
    count: int = 1,
    current_user: User = Depends(AuthService.get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    🎯 초대코드 생성 API (관리자 전용)
    - 새로운 초대코드 대량 생성
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 접근 가능합니다."
        )
    
    try:
        codes = AuthService.create_invite_codes(db=db, count=count)
        return {
            "message": f"{count}개의 초대코드가 생성되었습니다.",
            "codes": codes
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="초대코드 생성 중 오류가 발생했습니다."
        )

# ===== 헬스체크 엔드포인트 =====

@router.get("/health")
async def health_check():
    """
    🎯 인증 시스템 헬스체크
    - 시스템 상태 확인
    """
    return {
        "status": "healthy",
        "service": "auth",
        "message": "인증 시스템이 정상 작동 중입니다."
    }
