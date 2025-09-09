"""
User Segmentation API Router
Provides endpoints for user segmentation based on RFM analysis and behavioral patterns.
Implements user classification and targeting for personalized experiences.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.database import get_db
from app.dependencies import get_current_user, get_current_admin_user as get_current_admin
from app import models
from datetime import datetime, timedelta
import json

router = APIRouter(prefix="/api/segments", tags=["Segments"])

# Request/Response Models
class UserSegmentResponse(BaseModel):
    user_id: int
    rfm_group: str
    ltv_score: float
    risk_profile: str
    last_updated: datetime

class SegmentStatsResponse(BaseModel):
    segment_name: str
    user_count: int
    avg_ltv: float
    activity_level: str

class UpdateSegmentRequest(BaseModel):
    user_id: int
    rfm_group: str = Field(..., description="RFM segment group")
    ltv_score: float = Field(0.0, description="Lifetime value score")
    risk_profile: str = Field("MEDIUM", description="Risk profile level")

# 1. Get User Segment Information
@router.get("/user/{user_id}", response_model=UserSegmentResponse)
def get_user_segment(
    user_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get segmentation information for a specific user
    Returns RFM group, LTV score, and risk profile
    """
    # Check permissions - users can only view their own segment unless admin
    if current_user.id != user_id and not getattr(current_user, 'is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    segment = db.query(models.UserSegment).filter(
        models.UserSegment.user_id == user_id
    ).first()
    
    if not segment:
        # Create default segment if none exists
        segment = models.UserSegment(
            user_id=user_id,
            rfm_group="NEW_USER",
            ltv_score=0.0,
            risk_profile="MEDIUM",
            last_updated=datetime.now()
        )
        db.add(segment)
        db.commit()
        db.refresh(segment)
    
    return UserSegmentResponse(
        user_id=segment.user_id,
        rfm_group=segment.rfm_group,
        ltv_score=segment.ltv_score,
        risk_profile=segment.risk_profile,
        last_updated=segment.last_updated
    )

# 2. List All Segments
@router.get("/list", response_model=List[SegmentStatsResponse])
def list_all_segments(
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get statistics for all user segments
    Admin only endpoint for business intelligence
    """
    # Group users by segment and calculate statistics
    segments_data = db.query(
        models.UserSegment.rfm_group,
        db.func.count(models.UserSegment.user_id).label('user_count'),
        db.func.avg(models.UserSegment.ltv_score).label('avg_ltv')
    ).group_by(models.UserSegment.rfm_group).all()
    
    segment_stats = []
    for rfm_group, user_count, avg_ltv in segments_data:
        # Determine activity level based on user count
        if user_count > 100:
            activity_level = "HIGH"
        elif user_count > 20:
            activity_level = "MEDIUM"
        else:
            activity_level = "LOW"
        
        segment_stats.append(SegmentStatsResponse(
            segment_name=rfm_group,
            user_count=user_count,
            avg_ltv=round(avg_ltv or 0.0, 2),
            activity_level=activity_level
        ))
    
    return segment_stats

# 3. Update User Segment
@router.put("/update", response_model=UserSegmentResponse)
def update_user_segment(
    request: UpdateSegmentRequest,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update user segment information
    Admin only endpoint for manual segment adjustments
    """
    segment = db.query(models.UserSegment).filter(
        models.UserSegment.user_id == request.user_id
    ).first()
    
    if not segment:
        # Create new segment if none exists
        segment = models.UserSegment(
            user_id=request.user_id,
            rfm_group=request.rfm_group,
            ltv_score=request.ltv_score,
            risk_profile=request.risk_profile,
            last_updated=datetime.now()
        )
        db.add(segment)
    else:
        # Update existing segment
        segment.rfm_group = request.rfm_group
        segment.ltv_score = request.ltv_score
        segment.risk_profile = request.risk_profile
        segment.last_updated = datetime.now()
    
    db.commit()
    db.refresh(segment)
    
    return UserSegmentResponse(
        user_id=segment.user_id,
        rfm_group=segment.rfm_group,
        ltv_score=segment.ltv_score,
        risk_profile=segment.risk_profile,
        last_updated=segment.last_updated
    )

# 4. Calculate RFM Segments
@router.post("/calculate-rfm")
def calculate_rfm_segments(
    days: int = Query(90, description="Number of days to analyze for RFM calculation"),
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Recalculate RFM segments for all users
    Admin only endpoint for batch segment updates
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Get all users with activity in the specified period
    users_with_activity = db.query(
        models.UserAction.user_id,
        db.func.max(models.UserAction.created_at).label('last_activity'),
        db.func.count(models.UserAction.id).label('frequency'),
        db.func.sum(models.User.total_spent).label('monetary')
    ).join(
        models.User, models.UserAction.user_id == models.User.id
    ).filter(
        models.UserAction.created_at >= cutoff_date
    ).group_by(models.UserAction.user_id).all()
    
    updated_count = 0
    
    for user_id, last_activity, frequency, monetary in users_with_activity:
        # Calculate RFM scores
        recency_days = (datetime.now() - last_activity).days
        
        # Simple RFM scoring (can be enhanced with more sophisticated algorithms)
        if recency_days <= 7 and frequency >= 20 and (monetary or 0) >= 100:
            rfm_group = "WHALE"
            ltv_score = 100.0
            risk_profile = "LOW"
        elif recency_days <= 14 and frequency >= 10 and (monetary or 0) >= 50:
            rfm_group = "HIGH_VALUE"
            ltv_score = 75.0
            risk_profile = "LOW"
        elif recency_days <= 30 and frequency >= 5:
            rfm_group = "ENGAGED"
            ltv_score = 50.0
            risk_profile = "MEDIUM"
        elif recency_days <= 60:
            rfm_group = "AT_RISK"
            ltv_score = 25.0
            risk_profile = "HIGH"
        else:
            rfm_group = "DORMANT"
            ltv_score = 10.0
            risk_profile = "HIGH"
        
        # Update or create segment
        segment = db.query(models.UserSegment).filter(
            models.UserSegment.user_id == user_id
        ).first()
        
        if not segment:
            segment = models.UserSegment(
                user_id=user_id,
                rfm_group=rfm_group,
                ltv_score=ltv_score,
                risk_profile=risk_profile,
                last_updated=datetime.now()
            )
            db.add(segment)
        else:
            segment.rfm_group = rfm_group
            segment.ltv_score = ltv_score
            segment.risk_profile = risk_profile
            segment.last_updated = datetime.now()
        
        updated_count += 1
    
    db.commit()
    
    return {
        "message": f"RFM segments calculated successfully",
        "updated_users": updated_count,
        "calculation_period_days": days
    }

# 5. Get Segment Distribution
@router.get("/distribution")
def get_segment_distribution(
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get distribution of users across different segments
    Returns percentage breakdown and counts
    """
    total_users = db.query(models.UserSegment).count()
    
    if total_users == 0:
        return {
            "total_users": 0,
            "distribution": [],
            "message": "No user segments found"
        }
    
    distribution = db.query(
        models.UserSegment.rfm_group,
        db.func.count(models.UserSegment.user_id).label('count')
    ).group_by(models.UserSegment.rfm_group).all()
    
    distribution_data = []
    for rfm_group, count in distribution:
        percentage = round((count / total_users) * 100, 2)
        distribution_data.append({
            "segment": rfm_group,
            "count": count,
            "percentage": f"{percentage}%"
        })
    
    return {
        "total_users": total_users,
        "distribution": distribution_data
    }
