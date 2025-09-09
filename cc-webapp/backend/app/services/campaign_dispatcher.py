from __future__ import annotations

"""Campaign Dispatcher

Processes due NotificationCampaigns by creating Notification rows for targeted users
and marking campaigns as sent. Designed to be called by a scheduler periodically.
"""

from datetime import datetime, timezone
from typing import List, Set
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app import models


def _parse_user_ids(csv_text: str | None) -> List[int]:
    if not csv_text:
        return []
    ids: List[int] = []
    for part in csv_text.split(','):
        p = part.strip()
        if not p:
            continue
        try:
            ids.append(int(p))
        except ValueError:
            continue
    return ids


def _target_user_ids(db: Session, campaign: models.NotificationCampaign) -> Set[int]:
    if campaign.targeting_type == "all":
        q = db.query(models.User.id).filter(models.User.is_active == True)  # noqa: E712
        return {uid for (uid,) in q.all()}
    if campaign.targeting_type == "segment":
        if not campaign.target_segment:
            return set()
        # Join users with user_segments on user_id, filter by rfm_group label
        q = (
            db.query(models.User.id)
            .join(models.UserSegment, models.UserSegment.user_id == models.User.id)
            .filter(models.User.is_active == True, models.UserSegment.rfm_group == campaign.target_segment)  # noqa: E712
        )
        return {uid for (uid,) in q.all()}
    if campaign.targeting_type == "user_ids":
        ids = _parse_user_ids(campaign.user_ids)
        if not ids:
            return set()
        q = db.query(models.User.id).filter(and_(models.User.id.in_(ids), models.User.is_active == True))  # noqa: E712
        return {uid for (uid,) in q.all()}
    return set()


def dispatch_due_campaigns(db: Session, now: datetime | None = None) -> int:
    """Dispatch campaigns that are due (scheduled and time <= now).

    Returns number of campaigns processed.
    """
    if now is None:
        now = datetime.utcnow().replace(tzinfo=timezone.utc)

    due_campaigns: List[models.NotificationCampaign] = (
        db.query(models.NotificationCampaign)
        .filter(
            models.NotificationCampaign.status == "scheduled",
            # If scheduled_at is NULL, treat as immediate
            (models.NotificationCampaign.scheduled_at == None)  # noqa: E711
            | (models.NotificationCampaign.scheduled_at <= now)
        )
        .all()
    )

    processed = 0
    for camp in due_campaigns:
        user_ids = _target_user_ids(db, camp)
        if not user_ids:
            # Nothing to do, mark as sent to avoid endless retries
            camp.status = "sent"
            camp.sent_at = now
            db.add(camp)
            db.commit()
            processed += 1
            continue
        # Create notifications for each user
        for uid in user_ids:
            notif = models.Notification(
                user_id=uid,
                title=getattr(camp, "title", ""),
                message=getattr(camp, "message", ""),
                is_sent=False,
            )
            db.add(notif)
        # Mark campaign as sent
        camp.status = "sent"
        camp.sent_at = now
        db.add(camp)
        db.commit()
        processed += 1

    return processed
