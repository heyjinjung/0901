from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/test", tags=["test"])  # 한글 "테스트"를 "test"로 변경

class TestUserCreate(BaseModel):
    site_id: str
    password: str
    nickname: str

@router.post("/simple-register")
async def simple_register(user: TestUserCreate):
    """Simple test registration"""
    try:
        return {"message": "Test successful", "user": user.site_id}
    except Exception as e:
        return {"error": str(e)}
