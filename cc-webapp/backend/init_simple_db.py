"""데이터베이스 초기화 스크립트"""
import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 설정
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.simple_auth_models import Base, User, InviteCode
from app.config_simple import settings
from passlib.context import CryptContext

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    print("데이터베이스 초기화 시작...")
    
    # 데이터베이스 연결 문자열
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql://{settings.postgres_user}:{settings.postgres_password}@"
        f"{settings.postgres_server}/{settings.postgres_db}"
    )
    
    # 데이터베이스 엔진 생성
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 테이블 생성
    Base.metadata.drop_all(bind=engine)  # 기존 테이블 삭제
    Base.metadata.create_all(bind=engine)  # 새로운 테이블 생성
    
    # 세션 생성
    db = SessionLocal()
    
    try:
        # 초대코드 생성
        invite_code = InviteCode(code="5858")
        db.add(invite_code)
        
        # 관리자 계정 생성
        admin_user = User(
            site_id="admin",
            nickname="관리자",
            password_hash=pwd_context.hash("admin123"),
            is_admin=True,
        )
        db.add(admin_user)
        
        # 테스트 계정 생성
        test_user = User(
            site_id="test",
            nickname="테스트",
            password_hash=pwd_context.hash("test123"),
            is_admin=False,
        )
        db.add(test_user)
        
        # 변경사항 저장
        db.commit()
        print("데이터베이스 초기화 완료!")
        
    except Exception as e:
        db.rollback()
        print(f"데이터베이스 초기화 실패: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
