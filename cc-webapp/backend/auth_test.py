from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt, JWTError
import datetime
import uvicorn
import secrets

# JWT configuration
SECRET_KEY = "secret_key_for_testing"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Setup security scheme
security = HTTPBearer(auto_error=False)

class User(BaseModel):
    site_id: str
    nickname: str
    password: str
    invite_code: str = "5858"
    phone_number: str = "010-1234-5678"

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    nickname: str

class TokenData(BaseModel):
    user_id: int

# Create FastAPI app
app = FastAPI(title="Auth Test API")

# Fake users database
fake_users_db = {
    "test_user": {
        "id": 1,
        "site_id": "test_user",
        "nickname": "테스트유저",
        "password": "password123",
        "invite_code": "5858",
        "phone_number": "010-1234-5678"
    }
}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # For this test, we'll just return a dummy user
    return {"id": token_data.user_id, "nickname": "테스트유저"}

@app.post("/auth/register", response_model=Token)
async def register(user: User, request: Request):
    """Register a new user"""
    # In a real application, we would save the user to the database
    # For this test, we'll just create a token
    
    # Check if user exists
    if user.site_id in fake_users_db:
        fake_user = fake_users_db[user.site_id]
        # Create access token
        access_token = create_access_token({"sub": fake_user["id"]})
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=fake_user["id"],
            nickname=fake_user["nickname"]
        )
    
    # Create new user
    new_user_id = len(fake_users_db) + 1
    fake_users_db[user.site_id] = {
        "id": new_user_id,
        "site_id": user.site_id,
        "nickname": user.nickname,
        "password": user.password,
        "invite_code": user.invite_code,
        "phone_number": user.phone_number
    }
    
    # Create access token
    access_token = create_access_token({"sub": new_user_id})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user_id,
        nickname=user.nickname
    )

@app.post("/auth/login")
async def login(site_id: str, password: str, request: Request):
    """Login a user"""
    user = fake_users_db.get(site_id)
    if not user or user["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token({"sub": user["id"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user["id"],
        "nickname": user["nickname"]
    }

@app.get("/auth/profile")
async def profile(current_user = Depends(get_current_user)):
    """Get the current user's profile"""
    return current_user

if __name__ == "__main__":
    print("Starting FastAPI auth test server...")
    print("Test with: curl -X POST http://localhost:8001/auth/register -H \"Content-Type: application/json\" -d \"{\"site_id\": \"test_user123\", \"nickname\": \"테스트유저123\", \"password\": \"password123\", \"invite_code\": \"5858\"}\"")
    uvicorn.run(app, host="0.0.0.0", port=8001)
