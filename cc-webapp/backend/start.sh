#!/bin/bash
set -e

echo "🚀 Starting Casino-Club Backend..."

# Wait for database connection
echo "⏳ Waiting for PostgreSQL..."
sleep 5
echo "✅ PostgreSQL is ready!"

# Create database tables
echo "📊 Creating database tables..."
python -c "
import os
import sys
sys.path.insert(0, '/app')

from app.database import engine, get_db
from app.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Test database connection
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        logger.info(f'✅ Database connection successful: postgres:5432/cc_webapp')
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info('✅ Database tables created successfully')
    
except Exception as e:
    logger.warning(f'⚠️ Table creation warning: {e}')
"

# Create initial data
echo "🌱 Creating initial data..."
python -c "
import os
import sys
sys.path.insert(0, '/app')

from app.database import get_db
from app.models import User, InviteCode
from sqlalchemy.orm import Session
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    db = next(get_db())
    
    # Create basic invite codes if they don't exist
    existing_codes = db.query(InviteCode).count()
    if existing_codes == 0:
        logger.info('Creating basic invite codes...')
        codes = ['ALPHA1', 'BETA22', 'GAMMA3', 'DELTA4', 'OMEGA5']
        for code in codes:
            invite_code = InviteCode(
                code=code,
                is_active=True,
                created_at=datetime.utcnow(),
                max_uses=100,
                current_uses=0
            )
            db.add(invite_code)
        db.commit()
        logger.info(f'✅ Created {len(codes)} invite codes')
    
    db.close()
    logger.info('✅ Initial data setup completed')
    
except Exception as e:
    logger.warning(f'⚠️ Initial data warning: {e}')
"

# Start FastAPI server
echo "🎮 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload