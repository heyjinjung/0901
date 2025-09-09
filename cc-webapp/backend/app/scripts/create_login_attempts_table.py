"""Ensure login_attempts table exists.

Run inside backend container:
    docker compose exec backend python -m app.scripts.create_login_attempts_table

Idempotent: only creates table if missing.
"""
from sqlalchemy import inspect
from app.database import engine
from app.models.auth_models import LoginAttempt

def main():  # pragma: no cover
    insp = inspect(engine)
    if 'login_attempts' in insp.get_table_names():
        print('login_attempts already present; nothing to do.')
        return
    print('Creating login_attempts table...')
    LoginAttempt.__table__.create(bind=engine, checkfirst=True)
    print('✅ login_attempts table created.')

if __name__ == '__main__':  # pragma: no cover
    main()
