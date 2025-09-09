# 파일 위치: c:\Users\bdbd\Downloads\auto202506-a-main\auto202506-a-main\cc-webapp\backend\app\schemas\notification.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    user_id: int
    title: Optional[str] = None
    message: str
    
class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    is_read: bool
    is_sent: bool
    sent_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)