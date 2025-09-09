"""User 테이블 구조 확인"""
from sqlalchemy import inspect
from app.database import engine

inspector = inspect(engine)
columns = inspector.get_columns('users')
print('👤 users 테이블 컬럼들:')
for col in columns:
    print(f'  - {col["name"]}: {col["type"]}')
