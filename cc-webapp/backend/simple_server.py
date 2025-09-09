from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import hashlib
import time

app = FastAPI(title="Casino-Club F2P Backend", version="1.0.0")

# 간단한 메모리 기반 사용자 데이터베이스 (테스트용)
users_db = {
    "admin": {
        "id": 1,
        "site_id": "admin",
        "nickname": "관리자",
        "phone_number": "010-0000-0000",
        "password_hash": "admin123_hashed",
        "cyber_token_balance": 999999,
        "rank": "ADMIN",
        "created_at": "2025-07-28T00:00:00Z"
    }
}

# Pydantic 모델들
class SignupRequest(BaseModel):
    site_id: str
    nickname: str
    phone_number: str
    password: str
    invite_code: Optional[str] = "DEFAULT_INVITE"

class LoginRequest(BaseModel):
    site_id: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    user: dict

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 오리진 허용 (개발용)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Casino-Club F2P Backend is running!", "status": "ok"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "casino-club-backend"}

@app.get("/api/admin/stats")
async def get_admin_stats():
    return {
        "totalUsers": 150,
        "activeUsers": 89,
        "totalRewards": 45000,
        "todayActivities": 234
    }

@app.get("/api/admin/activities")
async def get_admin_activities():
    return {
        "items": [
            {"id": 1, "activity_type": "LOGIN", "details": "사용자 로그인", "timestamp": "2025-07-28T20:30:00Z"},
            {"id": 2, "activity_type": "GAME_PLAY", "details": "슬롯머신 게임", "timestamp": "2025-07-28T20:25:00Z"},
            {"id": 3, "activity_type": "REWARD_RECEIVED", "details": "토큰 100개 획득", "timestamp": "2025-07-28T20:20:00Z"},
            {"id": 4, "activity_type": "SIGNUP", "details": "신규 사용자 가입", "timestamp": "2025-07-28T20:15:00Z"},
            {"id": 5, "activity_type": "PURCHASE", "details": "프리미엄 아이템 구매", "timestamp": "2025-07-28T20:10:00Z"}
        ],
        "total": 5,
        "page": 1,
        "limit": 10
    }

@app.get("/api/admin/users")
async def get_admin_users():
    return {
        "items": [
            {
                "id": 1,
                "nickname": "관리자",
                "site_id": "admin",
                "phone_number": "010-0000-0000",
                "cyber_token_balance": 999999,
                "rank": "ADMIN",
                "created_at": "2025-07-28T00:00:00Z"
            },
            {
                "id": 2,
                "nickname": "테스트유저1",
                "site_id": "test001",
                "phone_number": "010-1234-5678",
                "cyber_token_balance": 5000,
                "rank": "PREMIUM",
                "created_at": "2025-07-28T10:00:00Z"
            },
            {
                "id": 3,
                "nickname": "일반유저1",
                "site_id": "user001",
                "phone_number": "010-9876-5432",
                "cyber_token_balance": 1500,
                "rank": "STANDARD",
                "created_at": "2025-07-28T15:00:00Z"
            }
        ],
        "total": 3,
        "page": 1,
        "limit": 10
    }

# 회원가입 API
@app.post("/api/auth/signup")
async def signup(request: SignupRequest):
    # 중복 체크
    if request.site_id in users_db:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자 ID입니다")
    
    # 새 사용자 ID 생성
    new_user_id = len(users_db) + 1
    
    # 사용자 데이터 생성
    user_data = {
        "id": new_user_id,
        "site_id": request.site_id,
        "nickname": request.nickname,
        "phone_number": request.phone_number,
        "password_hash": f"{request.password}_hashed",  # 실제로는 bcrypt 사용
        "cyber_token_balance": 1000,  # 신규 가입 보너스
        "rank": "STANDARD",
        "created_at": time.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    
    # 메모리 DB에 저장
    users_db[request.site_id] = user_data
    
    # 토큰 생성 (실제로는 JWT 사용)
    token = f"token_{request.site_id}_{int(time.time())}"
    
    # 응답용 사용자 데이터 (비밀번호 제외)
    response_user = {k: v for k, v in user_data.items() if k != "password_hash"}
    
    return {
        "access_token": token,
        "user": response_user,
        "message": "회원가입이 완료되었습니다"
    }

# 로그인 API
@app.post("/api/auth/login")
async def login(request: LoginRequest):
    # 사용자 확인
    if request.site_id not in users_db:
        raise HTTPException(status_code=401, detail="존재하지 않는 사용자입니다")
    
    user = users_db[request.site_id]
    
    # 비밀번호 확인 (간단한 체크, 실제로는 bcrypt 사용)
    expected_hash = f"{request.password}_hashed"
    if user["password_hash"] != expected_hash:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다")
    
    # 토큰 생성
    token = f"token_{request.site_id}_{int(time.time())}"
    
    # 응답용 사용자 데이터 (비밀번호 제외)
    response_user = {k: v for k, v in user.items() if k != "password_hash"}
    
    return {
        "access_token": token,
        "user": response_user,
        "message": "로그인이 완료되었습니다"
    }

# 현재 사용자 정보 API
@app.get("/api/auth/me")
async def get_current_user():
    # 간단한 더미 응답 (실제로는 토큰 검증 필요)
    return {
        "id": 1,
        "site_id": "admin",
        "nickname": "관리자",
        "phone_number": "010-0000-0000",
        "cyber_token_balance": 999999,
        "rank": "ADMIN",
        "created_at": "2025-07-28T00:00:00Z"
    }

# 초대 코드 확인 API
@app.post("/api/auth/verify-invite")
async def verify_invite_code(request: dict):
    invite_code = request.get("invite_code", "DEFAULT_INVITE")
    
    # 간단한 초대 코드 검증
    valid_codes = ["DEFAULT_INVITE", "VIP2025", "PREMIUM2025"]
    
    if invite_code in valid_codes:
        return {
            "valid": True,
            "message": "유효한 초대 코드입니다",
            "bonus_tokens": 500 if invite_code != "DEFAULT_INVITE" else 0
        }
    else:
        return {
            "valid": False,
            "message": "유효하지 않은 초대 코드입니다",
            "bonus_tokens": 0
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
