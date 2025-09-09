"""단일 초대코드 '5858' 멱등 시드.

요구: 하나만 생성, 추가 메타/설명 붙이지 말 것.

존재하면 아무 것도 하지 않고 종료.
"""
from datetime import datetime
from ..database import SessionLocal
from sqlalchemy import text
from .. import models

CODE = "5858"


def main():  # pragma: no cover
    db = SessionLocal()
    try:
        # invite_codes 테이블 존재 확인 (간단 try)
        try:
            db.execute(text("SELECT 1 FROM invite_codes LIMIT 1"))
        except Exception:
            db.rollback()
            print("invite_codes 테이블 없음")
            return
        row = db.query(models.InviteCode).filter(models.InviteCode.code == CODE).first()
        if row:
            print({"ok": True, "code": CODE, "action": "exists"})
            return
        new_row = models.InviteCode(
            code=CODE,
            is_used=False,
            is_active=True,
            used_count=0,
            created_at=datetime.utcnow(),
        )
        db.add(new_row)
        db.commit()
        print({"ok": True, "code": CODE, "action": "created"})
    except Exception as e:
        db.rollback()
        print({"ok": False, "error": str(e)})
        raise
    finally:
        db.close()


if __name__ == "__main__":  # pragma: no cover
    main()
