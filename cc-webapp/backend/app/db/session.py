"""DB Session helpers.

NOTE: 기존 코드에서 typing.Generator, Session, database 미 import 로 NameError 발생.
FastAPI 의존성 주입에서 사용되며 테스트/스크립트에서도 SessionLocal 직접 import 가능하도록 노출.
"""

from typing import Generator
from sqlalchemy.orm import Session

from app import database  # app/database.py (엔진 & SessionLocal 정의)

SessionLocal = database.SessionLocal  # re-export 편의


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yield SQLAlchemy session (scoped per-request)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()