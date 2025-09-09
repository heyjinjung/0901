"""
데이터베이스 초기화 및 고정 초대코드 설정 스크립트
"""
import sys
import os
sys.path.insert(0, '.')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Base, InviteCode
from app.database import engine, SessionLocal

def reset_database():
    """데이터베이스 완전 초기화"""
    print("🗑️ 데이터베이스 초기화 시작")
    
    # 모든 테이블 삭제
    Base.metadata.drop_all(bind=engine)
    print("✅ 기존 테이블 삭제 완료")
    
    # 테이블 재생성
    Base.metadata.create_all(bind=engine)
    print("✅ 새 테이블 생성 완료")

def setup_fixed_invite_codes():
    """고정 초대코드 설정"""
    print("\n🎫 고정 초대코드 설정")
    
    # 고정 초대코드 리스트
    fixed_codes = ["5882", "6969", "6974"]
    
    db = SessionLocal()
    try:
        for code in fixed_codes:
            invite = InviteCode(code=code, is_used=False)
            db.add(invite)
            print(f"✅ 초대코드 추가: {code}")
        
        db.commit()
        print("✅ 모든 초대코드 저장 완료")
        
        # 확인
        all_codes = db.query(InviteCode).all()
        print(f"\n📊 현재 초대코드 목록:")
        for invite in all_codes:
            status = "사용됨" if invite.is_used else "미사용"
            print(f"   - {invite.code} ({status})")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    print("🔄 데이터베이스 초기화 & 고정 초대코드 설정")
    print("=" * 60)
    
    # 1. 데이터베이스 초기화
    reset_database()
    
    # 2. 고정 초대코드 설정
    setup_fixed_invite_codes()
    
    print("\n🎉 설정 완료!")
    print("✅ 데이터베이스가 깨끗하게 초기화되었습니다")
    print("✅ 고정 초대코드 (5882, 6969, 6974)가 설정되었습니다")
    print("\n💡 이제 회원가입 시 위 3개 코드 중 하나를 사용하세요!")

if __name__ == "__main__":
    main()
