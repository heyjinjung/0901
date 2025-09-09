from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app import models


class TrackingService:
    def __init__(self, db: Session):
        self.db = db

    def log_site_visit(self, user_id: int, source: str) -> dict:
        """
        Logs a site visit for a user.
        기본 구현으로 실제 DB 저장 없이 결과만 반환
        """
        result = {
            "user_id": user_id,
            "source": source,
            "visit_timestamp": datetime.utcnow().isoformat()
        }
        return result
