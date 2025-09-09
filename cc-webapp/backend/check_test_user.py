from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

def check_test_user():
    # Get database connection details from environment
    POSTGRES_SERVER = os.environ.get("POSTGRES_SERVER", "postgres")
    POSTGRES_USER = os.environ.get("POSTGRES_USER", "cc_user")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "cc_password")
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "cc_webapp")
    
    # Create database URL
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
    
    # Create engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if test users exist
        result = db.execute(text("SELECT id, site_id, nickname, is_active, is_admin, created_at FROM users WHERE site_id LIKE \'test_user%\' LIMIT 10"))
        rows = result.fetchall()
        
        if rows:
            print("Test users found:")
            for row in rows:
                print(f"ID: {row[0]}, site_id: {row[1]}, nickname: {row[2]}, is_active: {row[3]}, is_admin: {row[4]}, created_at: {row[5]}")
        else:
            print("No test users found")
        
    finally:
        db.close()

check_test_user()
