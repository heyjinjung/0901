"""현재 사용자 목록 출력 스크립트

사용:
  docker compose exec backend python -m app.scripts.list_users
옵션:
  환경변수 COLUMNS=site_id,nickname 로 선택 컬럼 지정 가능 (기본: site_id,nickname,is_admin,invite_code,gold_balance,created_at)
"""
from __future__ import annotations
import os, json
from sqlalchemy import select
from app.database import SessionLocal
from app.models.auth_models import User

def main():
    columns_env = os.getenv("COLUMNS", "site_id,nickname,is_admin,invite_code,gold_balance,created_at")
    columns = [c.strip() for c in columns_env.split(',') if c.strip()]
    sess = SessionLocal()
    try:
        users = sess.execute(select(User).order_by(User.site_id)).scalars().all()
        out = []
        for u in users:
            row = {}
            for col in columns:
                row[col] = getattr(u, col, None)
            out.append(row)
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    finally:
        sess.close()

if __name__ == "__main__":  # pragma: no cover
    main()
