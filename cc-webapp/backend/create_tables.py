#!/usr/bin/env python3
"""
🗄️ Casino-Club F2P - 데이터베이스 테이블 생성
============================================
모든 모델 테이블을 데이터베이스에 생성
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app import models  # 모든 모델 import

def create_all_tables():
    """모든 테이블 생성"""
    try:
        print("🔄 데이터베이스 테이블 생성을 시작합니다...")
        
        # 모든 테이블 생성
        Base.metadata.create_all(bind=engine)
        
        print("✅ 모든 데이터베이스 테이블이 성공적으로 생성되었습니다!")
        
        # 생성된 테이블 목록 출력
        tables = Base.metadata.tables.keys()
        print(f"📊 총 {len(tables)}개 테이블 생성:")
        for table in sorted(tables):
            print(f"  - {table}")
            
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {str(e)}")
        return False
    
    return True

def check_tables():
    """테이블 존재 여부 확인"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print(f"📋 현재 데이터베이스의 테이블 목록 ({len(existing_tables)}개):")
        for table in sorted(existing_tables):
            print(f"  - {table}")
            
        return existing_tables
        
    except Exception as e:
        print(f"❌ 테이블 확인 실패: {str(e)}")
        return []

if __name__ == "__main__":
    print("🎰 Casino-Club F2P - 데이터베이스 초기화")
    print("=" * 50)
    
    # 기존 테이블 확인
    print("\n1️⃣ 기존 테이블 확인:")
    existing_tables = check_tables()
    
    # 새 테이블 생성
    print("\n2️⃣ 새 테이블 생성:")
    success = create_all_tables()
    
    if success:
        print("\n3️⃣ 최종 테이블 확인:")
        final_tables = check_tables()
        
        new_tables = set(final_tables) - set(existing_tables)
        if new_tables:
            print(f"\n🆕 새로 생성된 테이블 ({len(new_tables)}개):")
            for table in sorted(new_tables):
                print(f"  + {table}")
        else:
            print("\n ℹ️ 새로 생성된 테이블이 없습니다. (모든 테이블이 이미 존재)")
    
    print("\n" + "=" * 50)
    print("✅ 데이터베이스 초기화 완료!")
