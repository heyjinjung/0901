"""
독립형 FastAPI 애플리케이션 - 단순화된 구조
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, Field

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 환경 설정
class Settings:
    """애플리케이션 설정"""
    # JWT 관련 설정
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "super-secret-key-for-development-only")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # 서버 관련 설정
    api_version: str = "0.1.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # 기타 설정
    default_admin_username: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    default_admin_password: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin")

settings = Settings()

# 데이터베이스 설정
def get_database_url():
    """Return database URL based on environment"""
    # Docker/Production environment - PostgreSQL
    postgres_server = os.getenv('POSTGRES_SERVER')
    postgres_user = os.getenv('POSTGRES_USER')
    postgres_password = os.getenv('POSTGRES_PASSWORD')
    postgres_db = os.getenv('POSTGRES_DB')
    
    if postgres_server and postgres_user and postgres_password and postgres_db:
        return f"postgresql://{postgres_user}:{postgres_password}@{postgres_server}:5432/{postgres_db}"
    
    # Fallback to legacy environment variables
    if os.getenv('DB_HOST'):
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'cc_webapp')
        db_user = os.getenv('DB_USER', 'cc_user')
        db_password = os.getenv('DB_PASSWORD', 'cc_password')
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    # 개발 환경 fallback - SQLite
    return os.getenv("DATABASE_URL", "sqlite:///./standalone.db")

# 데이터베이스 URL 설정
DATABASE_URL = get_database_url()

# PostgreSQL vs SQLite 연결 옵션
if DATABASE_URL.startswith("postgresql"):
    connect_args = {}
    echo = os.getenv('DEBUG', 'false').lower() == 'true'
else:
    connect_args = {"check_same_thread": False}
    echo = False

try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=echo)
    # 연결 테스트
    with engine.connect():
        pass
    print(f"✅ 데이터베이스 연결 성공: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
except Exception as e:
    print(f"⚠️ 주 데이터베이스 연결 실패: {e}")
    # Fallback to local SQLite
    fallback_url = "sqlite:///./standalone_fallback.db"
    engine = create_engine(fallback_url, connect_args={"check_same_thread": False})
    print(f"🔄 Fallback 데이터베이스 사용: {fallback_url}")

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 모델 (단일 파일에 모든 모델 정의)
class User(Base):
    """사용자 모델 - 필수 필드만 포함"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String(50), unique=True, index=True, nullable=False)  # 사이트 아이디
    nickname = Column(String(50), unique=True, nullable=False)  # 닉네임
    password_hash = Column(String(255), nullable=False)  # 비밀번호
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 필수 관계만 포함
    security_events = relationship("SecurityEvent", back_populates="user", cascade="all, delete-orphan")

class SecurityEvent(Base):
    """보안 이벤트 모델"""
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String(50), nullable=False)  # 로그인, 비밀번호 변경 등
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    user = relationship("User", back_populates="security_events")

class InviteCode(Base):
    """초대코드 모델"""
    __tablename__ = "invite_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic 모델 (스키마)
class UserBase(BaseModel):
    site_id: str
    nickname: str
    
class UserCreate(UserBase):
    password: str
    invite_code: str

class UserResponse(UserBase):
    id: int
    is_admin: bool
    
    class Config:
        orm_mode = True

class TokenData(BaseModel):
    user_id: int
    sub: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    nickname: str

# 인증 관련 유틸리티
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def oauth2_optional_token(request: Request) -> str | None:
    """Extract bearer token from Authorization header if present; do not raise if missing.

    This allows route dependencies to implement cookie fallbacks when headers are not provided.
    """
    auth = request.headers.get("Authorization")
    if not auth:
        return None
    parts = auth.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None

def create_access_token(data: dict, expires_delta: timedelta = None):
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_optional_token), db: Session = Depends(get_db), request: Request = None) -> User:
    """현재 인증된 사용자 가져오기

    Accepts bearer token via Authorization header or falls back to reading
    an httpOnly cookie (common in browser environments). Cookie names
    checked: 'access_token', 'cc_access_token', 'cc_auth_tokens'.
    """
    # If oauth2_scheme provided a token, prefer it. If not, try optional header first
    if not token and request is not None:
        # try common cookie names
        for name in ('access_token', 'cc_access_token', 'cc_auth_tokens'):
            val = request.cookies.get(name)
            if val:
                token = val
                # if cookie contains JSON with access_token field, extract it
                try:
                    import json
                    maybe = json.loads(token)
                    if isinstance(maybe, dict) and 'access_token' in maybe:
                        token = maybe['access_token']
                except Exception:
                    pass

    logger.debug(f"[AUTH] Token received (first 10 chars): { (token[:10] if token else 'None') }...")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 토큰 디코딩
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("user_id")
        
        if user_id is None:
            logger.error("[AUTH] user_id not found in token")
            raise credentials_exception
            
        logger.debug(f"[AUTH] User ID from token: {user_id}")
        
    except JWTError as e:
        logger.error(f"[AUTH] JWT Error: {str(e)}")
        raise credentials_exception
        
    # 데이터베이스에서 사용자 조회
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        logger.error(f"[AUTH] User not found with ID: {user_id}")
        raise credentials_exception
        
    logger.debug(f"[AUTH] User authenticated: {user.nickname}")
    return user

# FastAPI 앱 설정
app = FastAPI(title="Casino-Club F2P API - 독립 버전")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용으로 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 초기화
Base.metadata.create_all(bind=engine)

# 테스트를 위한 초기 데이터 생성 함수
def create_initial_data(db: Session):
    # 관리자 계정 확인/생성
    admin_user = db.query(User).filter(User.site_id == settings.default_admin_username).first()
    if not admin_user:
        admin_user = User(
            site_id=settings.default_admin_username,
            nickname="관리자",
            password_hash=pwd_context.hash(settings.default_admin_password),
            is_active=True,
            is_admin=True
        )
        db.add(admin_user)
        
    # 초대코드 확인/생성
    invite_code = db.query(InviteCode).filter(InviteCode.code == "WELCOME").first()
    if not invite_code:
        invite_code = InviteCode(code="WELCOME", is_used=False)
        db.add(invite_code)
    
    db.commit()

# 시작 이벤트에 초기 데이터 생성 연결
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        create_initial_data(db)
        logger.info("초기 데이터가 성공적으로 생성되었습니다.")
    except Exception as e:
        logger.error(f"초기 데이터 생성 중 오류 발생: {e}")
    finally:
        db.close()

# 엔드포인트 정의
@app.get("/")
def read_root():
    return {"message": "Casino-Club F2P API - 독립 버전이 실행 중입니다"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "시스템이 정상적으로 실행 중입니다"}

@app.post("/api/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """로그인 엔드포인트"""
    logger.debug(f"[AUTH] Login attempt for username: {form_data.username}")
    
    # 사용자 확인
    user = db.query(User).filter(User.site_id == form_data.username).first()
    
    # 사용자가 없거나 비밀번호가 일치하지 않는 경우
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        logger.error(f"[AUTH] Login failed for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자 이름 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 토큰 생성
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"user_id": user.id, "sub": user.site_id},
        expires_delta=access_token_expires,
    )
    
    logger.debug(f"[AUTH] Login successful for user: {user.nickname}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "nickname": user.nickname,
    }

@app.post("/api/auth/signup", response_model=Token)
def signup(user_create: UserCreate, db: Session = Depends(get_db)):
    """회원가입 엔드포인트"""
    logger.debug(f"[AUTH] Signup attempt for username: {user_create.site_id}")
    
    # 아이디 중복 확인
    existing_user = db.query(User).filter(User.site_id == user_create.site_id).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용중인 아이디입니다",
        )
    
    # 닉네임 중복 확인
    existing_nickname = db.query(User).filter(User.nickname == user_create.nickname).first()
    if existing_nickname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용중인 닉네임입니다",
        )
    
    # 초대코드 확인
    invite = db.query(InviteCode).filter(InviteCode.code == user_create.invite_code, InviteCode.is_used == False).first()
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 초대코드입니다",
        )
    
    # 비밀번호 해싱
    hashed_password = pwd_context.hash(user_create.password)
    
    # 사용자 생성
    new_user = User(
        site_id=user_create.site_id,
        nickname=user_create.nickname,
        password_hash=hashed_password,
        is_active=True,
    )
    
    # 초대코드 사용 처리
    invite.is_used = True
    
    # 데이터베이스 저장
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.debug(f"[AUTH] Signup successful for user: {new_user.nickname}")
    
    # 자동 로그인을 위한 토큰 생성
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"user_id": new_user.id, "sub": new_user.site_id},
        expires_delta=access_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": new_user.id,
        "nickname": new_user.nickname,
    }

@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """현재 로그인한 사용자 정보 조회"""
    return current_user

# 관리자 전용 API
@app.get("/api/admin/users", response_model=List[UserResponse])
def get_users(
    skip: int = 0, 
    limit: int = 10, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """모든 사용자 목록 조회 (관리자 전용)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다",
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/api/admin/invite-codes")
def get_invite_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """모든 초대코드 목록 조회 (관리자 전용)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다",
        )
    
    codes = db.query(InviteCode).all()
    return [
        {
            "id": code.id,
            "code": code.code,
            "is_used": code.is_used,
            "created_at": code.created_at
        } 
        for code in codes
    ]

@app.post("/api/admin/invite-codes")
def create_invite_code(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """새 초대코드 생성 (관리자 전용)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다",
        )
    
    # 코드 중복 확인
    existing_code = db.query(InviteCode).filter(InviteCode.code == code).first()
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 초대코드입니다",
        )
    
    # 새 초대코드 생성
    new_code = InviteCode(code=code, is_used=False)
    db.add(new_code)
    db.commit()
    db.refresh(new_code)
    
    return {
        "id": new_code.id,
        "code": new_code.code,
        "is_used": new_code.is_used,
        "created_at": new_code.created_at
    }
