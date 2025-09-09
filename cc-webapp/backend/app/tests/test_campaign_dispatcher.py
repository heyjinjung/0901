from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from app.database import Base, engine, SessionLocal
from app.models import User, NotificationCampaign, Notification, UserSegment
from app.services.auth_service import AuthService
from app.services.campaign_dispatcher import dispatch_due_campaigns


def _seed_users(db):
    u1 = User(site_id="u1", nickname="u1", phone_number="01000000001", password_hash=AuthService.get_password_hash("pw"), invite_code="5858", is_active=True)
    u2 = User(site_id="u2", nickname="u2", phone_number="01000000002", password_hash=AuthService.get_password_hash("pw"), invite_code="5858", is_active=True)
    db.add_all([u1, u2])
    db.commit()
    db.refresh(u1)
    db.refresh(u2)
    # Segment u2 only
    db.add(UserSegment(user_id=u2.id, rfm_group="VIP"))
    db.commit()
    return u1, u2


def test_dispatch_campaigns_all_and_user_ids():
    db = SessionLocal()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    u1, u2 = _seed_users(db)
    now = datetime.utcnow().replace(tzinfo=timezone.utc)

    # All users campaign
    c1 = NotificationCampaign(title="hello", message="to all", targeting_type="all", scheduled_at=now)
    # Specific user_ids campaign
    c2 = NotificationCampaign(title="hi", message="to u1", targeting_type="user_ids", user_ids=str(u1.id), scheduled_at=now)
    # Segment campaign that will match u2 only
    c3 = NotificationCampaign(title="seg", message="vip only", targeting_type="segment", target_segment="VIP", scheduled_at=now)

    db.add_all([c1, c2, c3])
    db.commit()

    count = dispatch_due_campaigns(db, now=now)
    assert count == 3

    # Verify notifications
    notifs = db.query(Notification).all()
    # c1 -> u1,u2; c2 -> u1; c3 -> u2  => total 4
    assert len(notifs) == 4
    titles = sorted([n.title for n in notifs])
    assert titles.count("hello") == 2
    assert titles.count("hi") == 1
    assert titles.count("seg") == 1

    # Idempotency per run: nothing to dispatch now
    count2 = dispatch_due_campaigns(db, now=now)
    assert count2 == 0

    db.close()
