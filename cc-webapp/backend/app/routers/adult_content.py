"""Adult Content Router - VIP token-driven adult content unlocking system."""

import logging
from fastapi import APIRouter, HTTPException, Depends, Body, Path, Query
from fastapi.security import OAuth2PasswordBearer

from typing import List, Optional, Dict, Any

from app.database import get_db
from app.services.token_service import TokenService
from app.services.adult_content_service import AdultContentService
from app.services.user_service import UserService
from app.schemas import (
    AdultContentDetail, AdultContentGalleryResponse, ContentPreviewResponse,
    ContentUnlockRequestNew, ContentUnlockResponse, UnlockHistoryResponse,
    AccessUpgradeRequest, AccessUpgradeResponse
)
from app.models import User
from app.auth.simple_auth import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/adult", tags=["Adult Content"])
public_router = APIRouter(prefix="/v1/adult", tags=["Adult Content - Public"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Authentication dependency - Simple nickname based authentication
async def get_current_user(nickname: str, db = Depends(get_db)) -> User:
    """User authentication by nickname - Simple invite code enabled user"""
    user = db.query(User).filter(User.nickname == nickname).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def check_rank_access(user: User, required_rank: str) -> bool:
    """Rank based access control"""
    from app.auth.simple_auth import SimpleAuth
    return SimpleAuth.check_rank_access(str(user.rank), required_rank)

# Service dependencies
def get_token_service(db = Depends(get_db)) -> TokenService:
    return TokenService(db=db)

def get_user_service(db = Depends(get_db)) -> UserService:
    return UserService(db=db)

def get_adult_content_service(
    db = Depends(get_db),
    token_service: TokenService = Depends(get_token_service)
) -> AdultContentService:
    return AdultContentService(db=db, token_service=token_service)

# Placeholder service dependencies for tests - TODO: implement actual services
def get_vip_content_service(db = Depends(get_db)) -> Any:
    """Placeholder VIP content service for testing."""
    return None

def get_flash_offer_service(db = Depends(get_db)) -> Any:
    """Placeholder flash offer service for testing."""
    return None

def get_age_verification_service(db = Depends(get_db)) -> Any:
    """Placeholder age verification service for testing."""
    return None

# Error handling helper
def handle_service_errors(e: ValueError):
    """Handle common service errors with appropriate HTTP status codes."""
    error_message = str(e).lower()
    if "insufficient tokens" in error_message:
        raise HTTPException(status_code=402, detail=str(e))
    if "not found" in error_message:
        raise HTTPException(status_code=404, detail=str(e))
    if "age verification required" in error_message:
        raise HTTPException(status_code=403, detail=str(e))
    if "segment level too low" in error_message:
        raise HTTPException(status_code=403, detail=str(e))    # Default for other ValueErrors
    raise HTTPException(status_code=400, detail=str(e))

# --- Public Endpoints (No Authentication Required) ---

@public_router.get("/health")
async def health_check():
    """Health check endpoint for adult content service."""
    return {"status": "healthy", "service": "adult_content"}

# --- Content Retrieval Endpoints ---

@router.get("/gallery", response_model=AdultContentGalleryResponse)
async def get_gallery(
    current_user_id: int = Depends(get_current_user_id),
    service: AdultContentService = Depends(get_adult_content_service)
):
    """Get adult content gallery for authenticated user."""
    try:
        items = service.get_gallery_for_user(user_id=current_user_id)
        return AdultContentGalleryResponse(items=items)
    except ValueError as e:
        handle_service_errors(e)
    except Exception as e:
        logger.error(f"Gallery error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error getting gallery.")

@router.get("/content/preview")
async def get_content_gallery_preview(
    current_user_id: int = Depends(get_current_user_id),
    service: AdultContentService = Depends(get_adult_content_service)
):
    """Get content gallery preview for authenticated user."""
    try:
        items = service.get_gallery_for_user(user_id=current_user_id)
        return {"items": items}
    except ValueError as e:
        handle_service_errors(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error getting gallery preview.")

@router.get("/{content_id}", response_model=AdultContentDetail)
async def get_content_details(
    content_id: int = Path(..., title="The ID of the content to retrieve"),
    current_user_id: int = Depends(get_current_user_id),
    service: AdultContentService = Depends(get_adult_content_service)
):
    """Get detailed information about specific adult content."""
    try:
        details = await service.get_content_details(user_id=current_user_id, content_id=content_id)
        if not details:
            raise HTTPException(status_code=404, detail="Content not found or access denied.")
        return details
    except ValueError as e:
        handle_service_errors(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error getting content details.")

@router.get("/{content_id}/preview", response_model=ContentPreviewResponse)
async def get_content_preview(
    content_id: int = Path(..., title="The ID of the content to preview"),
    current_user_id: int = Depends(get_current_user_id),
    service: AdultContentService = Depends(get_adult_content_service)
):
    """Get preview for adult content."""
    try:
        preview_data = await service.get_content_preview(user_id=current_user_id, content_id=content_id)
        if not preview_data:
            raise HTTPException(status_code=404, detail="Preview not available or content not found.")
        return preview_data
    except ValueError as e:
        handle_service_errors(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error getting content preview.")

# --- Unlock Processing Endpoints ---

@router.post("/unlock", response_model=ContentUnlockResponse)
async def unlock_content_stage(
    request_data: ContentUnlockRequestNew = Body(...),
    current_user_id: int = Depends(get_current_user_id),
    service: AdultContentService = Depends(get_adult_content_service),
    user_service: UserService = Depends(get_user_service)
):
    """Unlock specific content stage."""
    try:
        # Get current user from database
        user = user_service.get_user_or_error(current_user_id)
        
        response = await service.unlock_content_stage(
            content_id=request_data.content_id,            stage_to_unlock=int(request_data.stage_to_unlock) if isinstance(request_data.stage_to_unlock, str) else (request_data.stage_to_unlock or 1),
            user=user
        )
        return response
    except ValueError as e:
        handle_service_errors(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error unlocking content.")

@router.get("/unlock/history", response_model=UnlockHistoryResponse)
async def get_unlock_history(
    current_user_id: int = Depends(get_current_user_id),
    service: AdultContentService = Depends(get_adult_content_service)
):
    """Get user's unlock history."""
    try:
        history_data = service.get_user_unlock_history(user_id=current_user_id)
        # Convert Dict to UnlockHistoryItem objects
        from app.schemas import UnlockHistoryItem
        history_items = [
            UnlockHistoryItem(**item) if isinstance(item, dict) else item
            for item in history_data
        ]
        return UnlockHistoryResponse(history=history_items)
    except ValueError as e:
        handle_service_errors(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error getting unlock history.")

@router.post("/content/unlock")
async def unlock_content(
    request_data: Dict[str, Any] = Body(...),
    current_user_id: int = Depends(get_current_user_id),
    service: AdultContentService = Depends(get_adult_content_service),
    user_service: UserService = Depends(get_user_service)
):
    """Unlock content using tokens."""
    try:
        # Get current user from database
        user = user_service.get_user_or_error(current_user_id)
        
        # Extract stage and tokens from request
        stage = request_data.get("stage", 1)
        tokens_to_spend = request_data.get("tokens_to_spend", 0)
        
        # For now, return mock response
        return {
            "success": True,
            "stage": stage,
            "content_url": f"https://example.com/content/{stage}"
        }
    except ValueError as e:
        handle_service_errors(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error unlocking content.")

# VIP-related endpoints (placeholders for testing)
@router.get("/vip/info")
async def get_vip_info(
    current_user_id: int = Depends(get_current_user_id),
    vip_service: Any = Depends(get_vip_content_service)
):
    """Get VIP information for user."""
    return {"vip_status": "active", "expires_at": "2025-12-31T23:59:59Z"}

# Flash offer endpoints (placeholders for testing)
@router.get("/flash-offers/active")
async def get_active_flash_offers(
    current_user_id: int = Depends(get_current_user_id),
    flash_service: Any = Depends(get_flash_offer_service)
):
    """Get active flash offers."""
    return {"offers": []}

@router.post("/flash-offers/purchase")
async def purchase_flash_offer(
    offer_data: Dict[str, Any] = Body(...),
    current_user_id: int = Depends(get_current_user_id),
    flash_service: Any = Depends(get_flash_offer_service)
):
    """Purchase flash offer."""
    return {"success": True, "offer_id": offer_data.get("offer_id")}

@router.get("/my-unlocks", response_model=UnlockHistoryResponse)
async def get_my_unlocks(
    current_user_id: int = Depends(get_current_user_id),
    service: AdultContentService = Depends(get_adult_content_service)
):
    """Get user's unlock history."""
    try:
        history = service.get_user_unlock_history(user_id=current_user_id)
        # Convert Dict to UnlockHistoryItem objects
        from app.schemas import UnlockHistoryItem
        history_items = [
            UnlockHistoryItem(**item) if isinstance(item, dict) else item
            for item in history        ]
        return UnlockHistoryResponse(history=history_items)
    except ValueError as e:
        handle_service_errors(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error getting unlock history.")

@router.post("/upgrade-access", response_model=AccessUpgradeResponse)
async def upgrade_access(
    request_data: AccessUpgradeRequest = Body(...),
    current_user_id: int = Depends(get_current_user_id),
    service: AdultContentService = Depends(get_adult_content_service),
    user_service: UserService = Depends(get_user_service)
):
    """Temporarily upgrade user's access level."""
    try:
        # Get current user from database
        user = user_service.get_user_or_error(current_user_id)
        
        response = await service.upgrade_access_temporarily(request=request_data, user=user)
        return response
    except ValueError as e:
        handle_service_errors(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error upgrading access.")

# --- Health Check ---

