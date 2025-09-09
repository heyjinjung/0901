from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# Create a router for the test endpoints
router = APIRouter(tags=["Test"])

# Model for user creation
class TestUser(BaseModel):
    site_id: str
    nickname: str
    password: str
    invite_code: str = "5858"
    phone_number: str = "010-1234-5678"

@router.post("/test-auth")
async def test_auth(user: TestUser):
    """Test authentication functionality"""
    try:
        return {
            "status": "success",
            "message": "Authentication test completed",
            "user": {
                "site_id": user.site_id,
                "nickname": user.nickname
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
