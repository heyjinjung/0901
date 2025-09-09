"""
Invite Code System Router
Handles invite code generation, validation, and user registration with invite codes.
Implements simple registration flow for MVP.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app import models
from app.schemas.invite_code import (
    InviteCodeResponse, ValidateInviteCodeRequest, ValidateInviteCodeResponse
)
from datetime import datetime, timedelta
import secrets
import string

router = APIRouter(prefix="/api/invite", tags=["Invite Codes"])

def generate_invite_code(length: int = 8) -> str:
    """Generate a random invite code"""
    characters = string.ascii_uppercase + string.digits
    # Exclude confusing characters
    characters = characters.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
    return ''.join(secrets.choice(characters) for _ in range(length))

@router.post("/generate", response_model=InviteCodeResponse)
def create_invite_code(
    expires_in_days: int = 30,
    max_uses: int = 1,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new invite code
    Only admin users can generate invite codes
    """
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can generate invite codes"
        )
    
    # Generate unique code
    while True:
        code = generate_invite_code()
        existing = db.query(models.InviteCode).filter(
            models.InviteCode.code == code
        ).first()
        if not existing:
            break
    
    # Create invite code record
    invite_code = models.InviteCode(
        code=code,
        created_by=current_user.id,
        expires_at=datetime.now() + timedelta(days=expires_in_days),
        max_uses=max_uses,
        used_count=0,
        is_active=True
    )
    
    db.add(invite_code)
    db.commit()
    db.refresh(invite_code)
    
    return InviteCodeResponse(
        code=invite_code.code,
        expires_at=invite_code.expires_at,
        max_uses=invite_code.max_uses,
        used_count=invite_code.used_count,
        is_active=invite_code.is_active,
        created_at=invite_code.created_at
    )

@router.post("/validate", response_model=ValidateInviteCodeResponse)
def validate_invite_code(
    request: ValidateInviteCodeRequest,
    db: Session = Depends(get_db)
):
    """
    Validate an invite code
    Returns validation status and code details
    """
    invite_code = db.query(models.InviteCode).filter(
        models.InviteCode.code == request.code.upper()
    ).first()
    
    if not invite_code:
        return ValidateInviteCodeResponse(
            is_valid=False,
            error_message="Invalid invite code"
        )
    
    # Check if code is still active
    if not invite_code.is_active:
        return ValidateInviteCodeResponse(
            is_valid=False,
            error_message="Invite code has been deactivated"
        )
    
    # Check if code has expired
    if invite_code.expires_at and invite_code.expires_at < datetime.now():
        return ValidateInviteCodeResponse(
            is_valid=False,
            error_message="Invite code has expired"
        )
    
    # Check if code has reached max uses
    if invite_code.max_uses is not None and invite_code.used_count >= invite_code.max_uses:
        return ValidateInviteCodeResponse(
            is_valid=False,
            error_message="Invite code has reached maximum usage limit"
        )
    
    # Compute remaining uses (None for unlimited)
    remaining = None
    if invite_code.max_uses is not None:
        remaining = max(invite_code.max_uses - invite_code.used_count, 0)

    return ValidateInviteCodeResponse(
        is_valid=True,
        code=invite_code.code,
        expires_at=invite_code.expires_at,
        remaining_uses=remaining
    )

@router.get("/codes", response_model=list[InviteCodeResponse])
def list_invite_codes(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all invite codes created by the current user
    Admin users can see all codes
    """
    if getattr(current_user, 'is_admin', False):
        # Admin can see all codes
        codes = db.query(models.InviteCode).order_by(
            models.InviteCode.created_at.desc()
        ).all()
    else:
        # Regular users can only see codes they created
        codes = db.query(models.InviteCode).filter(
            models.InviteCode.created_by == current_user.id
        ).order_by(
            models.InviteCode.created_at.desc()
        ).all()
    
    return [
        InviteCodeResponse(
            code=code.code,
            expires_at=code.expires_at,
            max_uses=code.max_uses,
            used_count=code.used_count,
            is_active=code.is_active,
            created_at=code.created_at
        )
        for code in codes
    ]

@router.patch("/codes/{code}/deactivate")
def deactivate_invite_code(
    code: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate an invite code
    Only the creator or admin can deactivate
    """
    invite_code = db.query(models.InviteCode).filter(
        models.InviteCode.code == code.upper()
    ).first()
    
    if not invite_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite code not found"
        )
    
    # Check permissions
    if (not getattr(current_user, 'is_admin', False) and 
        invite_code.created_by != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only deactivate your own invite codes"
        )
    
    invite_code.is_active = False
    db.commit()
    
    return {"message": "Invite code deactivated successfully"}

@router.get("/stats")
def get_invite_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get invite code statistics
    Shows usage metrics for the current user's codes
    """
    if getattr(current_user, 'is_admin', False):
        # Admin gets global stats
        total_codes = db.query(models.InviteCode).count()
        active_codes = db.query(models.InviteCode).filter(
            models.InviteCode.is_active == True
        ).count()
        total_uses = db.query(models.InviteCode).with_entities(
            db.func.sum(models.InviteCode.used_count)
        ).scalar() or 0
    else:
        # Regular user gets their own stats
        total_codes = db.query(models.InviteCode).filter(
            models.InviteCode.created_by == current_user.id
        ).count()
        active_codes = db.query(models.InviteCode).filter(
            models.InviteCode.created_by == current_user.id,
            models.InviteCode.is_active == True
        ).count()
        total_uses = db.query(models.InviteCode).filter(
            models.InviteCode.created_by == current_user.id
        ).with_entities(
            db.func.sum(models.InviteCode.used_count)
        ).scalar() or 0
    
    return {
        "total_codes": total_codes,
        "active_codes": active_codes,
        "expired_codes": total_codes - active_codes,
        "total_uses": total_uses
    }
