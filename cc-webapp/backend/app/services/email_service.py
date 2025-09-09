from typing import Optional, List
import os
import smtplib
from email.message import EmailMessage

from app.core.config import settings
from app.services import email_templates
from app.models.auth_models import User

class EmailService:
    """Simple SMTP email sender using environment-configured settings.
    Uses Mailpit by default in development.
    """

    def __init__(self):
        self.host = os.getenv("SMTP_HOST", getattr(settings, "SMTP_HOST", "mailpit"))
        self.port = int(os.getenv("SMTP_PORT", getattr(settings, "SMTP_PORT", 1025)))
        self.user = os.getenv("SMTP_USER", getattr(settings, "SMTP_USER", ""))
        self.password = os.getenv("SMTP_PASSWORD", getattr(settings, "SMTP_PASSWORD", ""))
        self.from_addr = os.getenv("SMTP_FROM", getattr(settings, "SMTP_FROM", "noreply@casino-club.local"))
        self.from_name = os.getenv("SMTP_FROM_NAME", getattr(settings, "SMTP_FROM_NAME", "Casino Club"))
        self.use_tls = False  # Mailpit dev server doesn't require TLS

    def _build_msg(self, to: str, subject: str, text: str, html: Optional[str] = None) -> EmailMessage:
        msg = EmailMessage()
        msg["From"] = f"{self.from_name} <{self.from_addr}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(text)
        if html:
            msg.add_alternative(html, subtype="html")
        return msg

    def send(self, to: str, subject: str, text: str, html: Optional[str] = None) -> bool:
        msg = self._build_msg(to, subject, text, html)
        try:
            with smtplib.SMTP(self.host, self.port, timeout=10) as server:
                server.ehlo()
                if self.use_tls:
                    server.starttls()
                if self.user and self.password:
                    server.login(self.user, self.password)
                server.send_message(msg)
            return True
        except Exception:
            return False

    def send_bulk(self, recipients: List[str], subject: str, text: str, html: Optional[str] = None) -> int:
        sent = 0
        for r in recipients:
            if self.send(r, subject, text, html):
                sent += 1
        return sent

    @staticmethod
    def dev_email_for_user(user: User) -> str:
        """개발 환경 전용 유저 메일 주소 생성(helper).
        User 모델에 email 필드가 없어 site_id 기반 가상 주소를 사용합니다.
        """
        site_id = getattr(user, "site_id", None) or "user"
        return f"{site_id}@casino-club.local"

    def send_template_to_user(self, user: User, template: str, context: dict) -> bool:
        """템플릿 기반 이메일을 해당 유저의 개발용 주소로 발송합니다.
        실패는 무시하고 False 반환(베스트에포트).
        """
        try:
            subject, text, html = email_templates.render(template, context)
            target = self.dev_email_for_user(user)
            return self.send(target, subject, text, html)
        except Exception:
            return False
