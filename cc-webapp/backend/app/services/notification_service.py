from datetime import datetime, timezone
from typing import Optional, List, Tuple
import json

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app import models
from app.utils.redis import RedisManager
from app.core.config import settings
try:
    from pywebpush import webpush  # type: ignore
except Exception:  # fallback if not installed
    webpush = None


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_oldest_pending_notification(self, user_id: int) -> Optional[models.Notification]:
        """
        Retrieves the oldest pending notification for a user, marks it as sent,
        and returns it.
        """
        try:
            notification = (
                self.db.query(models.Notification)
                .filter(
                    models.Notification.user_id == user_id,
                    models.Notification.is_sent == False,
                )
                .order_by(models.Notification.created_at.asc())
                .first()
            )

            if notification:
                notification.is_sent = True
                notification.sent_at = datetime.utcnow().replace(tzinfo=timezone.utc)
                self.db.commit()
                self.db.refresh(notification)
                return notification
            return None
        except SQLAlchemyError as e:
            # Log the error e.g., logging.error(f"Database error in get_oldest_pending_notification: {e}")
            self.db.rollback()
            # Depending on policy, you might want to raise a custom service exception
            # or return None and let the caller handle it.
            # For now, re-raising.
            # Consider specific exception handling for different error types if necessary.
            raise e # Re-raise the exception after rollback

    def create_notification(
        self,
        user_id: int,
        message: str,
        title: Optional[str] = None,
        notification_type: Optional[str] = None,
    ) -> models.Notification:
        """
        Creates a new notification for a user.
        """
        db_notification = models.Notification(
            user_id=user_id,
            title=(title or "Notification"),
            message=message,
            notification_type=(notification_type or "info"),
            is_sent=False,
            created_at=datetime.utcnow().replace(tzinfo=timezone.utc),
        )

        try:
            self.db.add(db_notification)
            self.db.commit()
            self.db.refresh(db_notification)
            return db_notification
        except SQLAlchemyError as e:
            # Log the error
            self.db.rollback()
            # Raise a custom service exception or handle as per application policy
            raise # Re-raising for now, or transform into a service-specific exception.

    # -----------------------------
    # New helper methods for center
    # -----------------------------
    def list_notifications(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        only_unread: bool = False,
        notification_type: Optional[str] = None,
    ) -> Tuple[List[models.Notification], int]:
        """
        List notifications for a user with pagination and optional filters.

        Returns (items, total_count)
        """
        try:
            q = self.db.query(models.Notification).filter(models.Notification.user_id == user_id)
            if only_unread:
                q = q.filter(models.Notification.is_read == False)
            if notification_type:
                q = q.filter(models.Notification.notification_type == notification_type)
            total = q.count()
            items = (
                q.order_by(models.Notification.created_at.desc())
                 .offset(max(0, int(offset)))
                 .limit(max(1, min(int(limit), 200)))
                 .all()
            )
            return items, total
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def mark_as_read(self, user_id: int, notification_id: int, read: bool = True) -> Optional[models.Notification]:
        """Mark a single notification read/unread if owned by the user."""
        try:
            n = (
                self.db.query(models.Notification)
                .filter(models.Notification.id == notification_id, models.Notification.user_id == user_id)
                .first()
            )
            if not n:
                return None
            n.is_read = bool(read)
            n.read_at = datetime.utcnow().replace(tzinfo=timezone.utc) if read else None
            self.db.commit()
            self.db.refresh(n)
            return n
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications for a user as read. Returns affected count."""
        try:
            updated = (
                self.db.query(models.Notification)
                .filter(models.Notification.user_id == user_id, models.Notification.is_read == False)
                .update({
                    models.Notification.is_read: True,
                    models.Notification.read_at: datetime.utcnow().replace(tzinfo=timezone.utc)
                }, synchronize_session=False)
            )
            self.db.commit()
            return int(updated or 0)
        except SQLAlchemyError:
            self.db.rollback()
            return 0

    def unread_count(self, user_id: int) -> int:
        """Return unread notifications count for user."""
        try:
            return self.db.query(models.Notification).filter(
                models.Notification.user_id == user_id,
                models.Notification.is_read == False
            ).count()
        except SQLAlchemyError:
            self.db.rollback()
            return 0

    # ---------------------
    # Web Push (VAPID)
    # ---------------------
    def push_to_user_subscriptions(self, user_id: int, payload: dict) -> Tuple[int, int, int]:
        """
        사용자 Redis에 저장된 PushSubscription들로 VAPID 웹푸시 발송.
        반환: (sent_count, failed_count, removed_count)
        """
        rm = RedisManager()
        key = f"user:{user_id}:push:subs"
        subs_obj = rm.get_cached_data(key) or {"subs": []}
        subs = subs_obj.get("subs", [])

        if not subs or webpush is None:
            return (0, 0, 0)

        sent = failed = removed = 0
        to_keep = []
        vapid_pub = getattr(settings, "VAPID_PUBLIC_KEY", "") or ""
        vapid_priv = getattr(settings, "VAPID_PRIVATE_KEY", "") or ""
        claims = {"sub": "mailto:admin@casino-club.local"}

        for s in subs:
            try:
                webpush(
                    subscription_info={
                        "endpoint": s.get("endpoint"),
                        "keys": {"p256dh": s.get("p256dh"), "auth": s.get("auth")},
                    },
                    data=json.dumps(payload),
                    vapid_private_key=vapid_priv,
                    vapid_public_key=vapid_pub,
                    vapid_claims=claims,
                )
                sent += 1
                to_keep.append(s)
            except Exception as e:
                failed += 1
                status = getattr(getattr(e, "response", None), "status_code", None)
                if status in (404, 410):
                    removed += 1
                else:
                    to_keep.append(s)

        if removed:
            rm.cache_user_data(key, {"subs": to_keep}, expire_seconds=30 * 24 * 3600)

        return (sent, failed, removed)

    # Potential future method for batch creation or more complex logic
    # def create_notifications_batch(self, notifications_data: List[Dict]) -> List[models.Notification]:
    #     pass

    # Potential future method for marking as read (distinct from sent, if UI supports it)
    # def mark_notification_as_read(self, notification_id: int, user_id: int) -> Optional[models.Notification]:
    #     pass
