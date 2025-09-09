from fastapi import APIRouter, Depends, HTTPException

from pydantic import BaseModel, ConfigDict
from datetime import datetime

from .. import models
from ..database import get_db
from ..services.tracking_service import TrackingService

router = APIRouter(
    prefix="/api/tracking",  # Route under /api consistently
    tags=["Tracking"]         # Standardized tag casing
)

# Pydantic model for request body (moved from notification.py)
class SiteVisitCreate(BaseModel):
    user_id: int # Assuming client still sends this. Could also be derived from auth.
    source: str

# Pydantic model for response (moved from notification.py)
class SiteVisitResponse(BaseModel):
    id: int
    user_id: int
    source: str
    visit_timestamp: datetime

    class Config:

        # Pydantic V2 uses ``from_attributes`` for ORM integration.
        from_attributes = True

# Dependency provider for TrackingService
def get_tracking_service(db = Depends(get_db)):
    return TrackingService(db=db)

@router.post("/site-visit", status_code=201, response_model=SiteVisitResponse)
async def log_site_visit_endpoint( # Renamed to avoid conflict if main app has log_site_visit
    visit_data: SiteVisitCreate,
    service: TrackingService = Depends(get_tracking_service)
):
    """
    Logs a visit to an external corporate site or other tracked action.
    """
    try:
        # Consider if user_id should be taken from authenticated user instead of request body
        # For example: current_user: models.User = Depends(get_current_user)
        # then use current_user.id
        db_site_visit = service.log_site_visit(
            user_id=visit_data.user_id,
            source=visit_data.source
        )
        return SiteVisitResponse.model_validate(db_site_visit) # Pydantic V2
    except Exception as e:
        # Log the exception e.g. logging.error(f"Error logging site visit: {e}")
        # This could be a DB error from the service or other unexpected error.
        # The service might raise specific exceptions that can be handled more granularly here.
        raise HTTPException(status_code=500, detail="Failed to log site visit.")

# To include this router in your main application (e.g., app/main.py):
# from app.routers import tracking as tracking_router # Choose an alias
# app.include_router(tracking_router.router) # Default prefix "/tracking" will be used
# Or, if you want to nest it under /api:
# app.include_router(tracking_router.router, prefix="/api/tracking") # Manually setting full prefix
# The instruction mentions /api prefix for the main app, so if routers are included with their own
# prefix, it would become /api/tracking/site-visit. Let's assume main.py adds /api.
