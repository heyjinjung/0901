"""
Analytics API Router
Provides endpoints for data analysis, user behavior tracking, and business intelligence.
Supports real-time analytics and historical data analysis for Casino-Club F2P.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.database import get_db
from app.dependencies import get_current_user, get_current_admin_user as get_current_admin
from app import models
from datetime import datetime, timedelta
from sqlalchemy import func
import json
from app.olap.clickhouse_client import ClickHouseClient

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

# Request/Response Models
class AnalyticsQuery(BaseModel):
    text: str = Field(..., description="Analysis query text")
    date_from: Optional[datetime] = Field(None, description="Start date for analysis")
    date_to: Optional[datetime] = Field(None, description="End date for analysis")
    user_segment: Optional[str] = Field(None, description="User segment filter")

class AnalyticsResponse(BaseModel):
    query: str
    results: Dict[str, Any]
    timestamp: datetime
    total_records: int

# Basic Analytics Endpoints
@router.get("/dashboard/summary")
def get_dashboard_summary(
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get basic dashboard summary with key metrics
    """
    total_users = db.query(models.User).count()
    total_actions = db.query(models.UserAction).count()
    total_rewards = db.query(models.UserReward).count()
    
    return {
        "total_users": total_users,
        "total_actions": total_actions,
        "total_rewards": total_rewards,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/users/activity")
def get_user_activity(
    days: int = Query(7, description="Number of days to analyze"),
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get user activity analytics for the specified period
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Daily user activity
    daily_activity = []
    for i in range(days):
        day = start_date + timedelta(days=i)
        daily_actions = db.query(models.UserAction).filter(
            func.date(models.UserAction.created_at) == day.date()
        ).count()
        
        daily_activity.append({
            "date": day.date().isoformat(),
            "actions": daily_actions
        })
    
    return {
        "period": f"{days} days",
        "daily_activity": daily_activity
    }

@router.get("/games/stats")
def get_game_statistics(
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get game performance statistics
    """
    # Game popularity by action count
    game_stats = db.query(
        models.UserAction.action_type,
        func.count(models.UserAction.id).label('plays')
    ).group_by(models.UserAction.action_type).all()
    
    games_data = [
        {"game_type": action_type, "total_plays": plays}
        for action_type, plays in game_stats
    ]
    
    return {
        "games": games_data,
        "total_games": len(games_data)
    }

@router.get("/funnels/buy")
def get_buy_funnel(
    days: int = Query(7, ge=1, le=60),
    current_user: models.User = Depends(get_current_admin)
):
    """Return simple buy funnel slices from ClickHouse over the last N days."""
    ch = ClickHouseClient()
    try:
        data = ch.get_buy_funnel(days=days)
    except Exception as e:
        # Surface a friendly error; logs already contain CH detail
        raise HTTPException(status_code=502, detail=f"ClickHouse query failed: {e}")
    return {"days": days, "stages": data}
