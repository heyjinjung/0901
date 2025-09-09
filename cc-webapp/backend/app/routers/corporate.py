from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import token_service


class TokenEarnRequest(BaseModel):
    user_id: int
    amount: int

router = APIRouter(prefix="/v1/corporate", tags=["Corporate"])

@router.post("/tokens/earn")
async def earn_tokens(req: TokenEarnRequest):
    """Simulate earning cyber tokens on the corporate site"""
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    new_balance = token_service.add_tokens(req.user_id, req.amount)
    return {"balance": new_balance}


@router.get("/tokens/balance")
async def get_token_balance(user_id: int):
    """Retrieve a user's current cyber token balance"""
    return {"balance": token_service.get_balance(user_id)}


