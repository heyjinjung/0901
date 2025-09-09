from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# SQLAlchemy 엔진 생성
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, 
    pool_pre_ping=True
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모든 모델의 기본 클래스가 될 Base 클래스
Base = declarative_base()

