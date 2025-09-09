from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.auth_models import User
from app.services.email_service import EmailService
from app.services.notification_service import NotificationService
from app.services import email_templates

router = APIRouter(prefix="/api/email", tags=["Email"])

class SendEmailRequest(BaseModel):
    to: EmailStr
    subject: str
    text: str
    html: Optional[str] = None

class BulkEmailRequest(BaseModel):
    recipients: List[EmailStr]
    subject: str
    text: str
    html: Optional[str] = None

class TemplateEmailRequest(BaseModel):
    to: EmailStr
    template: str
    context: dict


def _dev_email_for_user(user: User) -> str:
    """Derive a development email address for a user.
    Since the User model doesn't have a persisted email field,
    we map site_id to a synthetic email for dev/testing.
    """
    site_id = getattr(user, "site_id", None) or "user"
    return f"{site_id}@casino-club.local"

@router.post("/send")
async def send_email(
    body: SendEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Only admin can send arbitrary emails; non-admin can only send to self
    target = str(body.to)
    if not getattr(current_user, "is_admin", False) and getattr(current_user, "role", "").lower() not in ("admin", "superadmin"):
        # Non-admin can only send to their own derived dev email
        if target.lower() != _dev_email_for_user(current_user).lower():
            raise HTTPException(status_code=403, detail="forbidden")

    svc = EmailService()
    ok = svc.send(target, body.subject, body.text, body.html)

    # Log notification record for traceability
    ns = NotificationService(db)
    ns.create_notification(
        user_id=current_user.id,
        title="Email Sent" if ok else "Email Failed",
        message=f"Email to {target}: {'OK' if ok else 'FAILED'}",
        notification_type="system",
    )
    if not ok:
        raise HTTPException(status_code=500, detail="send_failed")
    return {"ok": True}

@router.post("/send-bulk")
async def send_bulk_email(
    body: BulkEmailRequest,
    current_user: User = Depends(get_current_user),
):
    # Admin-only
    if not getattr(current_user, "is_admin", False) and getattr(current_user, "role", "").lower() not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="forbidden")

    svc = EmailService()
    count = svc.send_bulk([str(e) for e in body.recipients], body.subject, body.text, body.html)
    return {"ok": True, "sent": count, "requested": len(body.recipients)}

@router.get("/test")
async def test_email(current_user: User = Depends(get_current_user)):
    svc = EmailService()
    # Send to the caller's derived dev email
    target = _dev_email_for_user(current_user)
    ok = svc.send(target, "Test Email", "This is a test email.")
    return {"ok": ok, "to": target}

@router.post("/send-template")
async def send_template_email(
    body: TemplateEmailRequest,
    current_user: User = Depends(get_current_user),
):
    # Non-admin can only send to self
    target = str(body.to)
    if not getattr(current_user, "is_admin", False) and getattr(current_user, "role", "").lower() not in ("admin", "superadmin"):
        if target.lower() != _dev_email_for_user(current_user).lower():
            raise HTTPException(status_code=403, detail="forbidden")

    subject, text, html = email_templates.render(body.template, body.context)
    svc = EmailService()
    ok = svc.send(target, subject, text, html)
    if not ok:
        raise HTTPException(status_code=500, detail="send_failed")
    return {"ok": True}
