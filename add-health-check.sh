#!/bin/bash

# This script adds a health check API endpoint to the FastAPI backend
# Used by Jules to verify the API is working properly

set -e  # Exit immediately if a command fails

echo "====== Adding Health Check API Endpoint ======"

# Define the health check API endpoint code
HEALTH_CHECK_CODE=$(cat << 'EOF'
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
import psutil
import json

from app.core.dependencies import get_db, get_redis
from app.core.security import get_current_user

health_router = APIRouter(tags=["Health"])

@health_router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    """
    Health check endpoint for Jules environment testing
    """
    health_data = {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat(),
        "services": {}
    }
    
    # Check database connection
    try:
        result = await db.execute("SELECT 1")
        health_data["services"]["database"] = {"status": "up"}
    except Exception as e:
        health_data["services"]["database"] = {"status": "down", "error": str(e)}
        health_data["status"] = "degraded"
    
    # Check Redis connection
    try:
        redis_ping = redis.ping()
        health_data["services"]["redis"] = {"status": "up" if redis_ping else "down"}
        if not redis_ping:
            health_data["status"] = "degraded"
    except Exception as e:
        health_data["services"]["redis"] = {"status": "down", "error": str(e)}
        health_data["status"] = "degraded"
    
    # Add system resources info
    health_data["system"] = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }
    
    return health_data
EOF
)

# Check if app directory exists
if [ ! -d "cc-webapp/backend/app" ]; then
  echo "Error: Backend app directory not found"
  exit 1
fi

# Check if API directory exists, create if not
if [ ! -d "cc-webapp/backend/app/api" ]; then
  mkdir -p cc-webapp/backend/app/api
fi

# Create health.py module
HEALTH_FILE="cc-webapp/backend/app/api/health.py"
echo "$HEALTH_CHECK_CODE" > "$HEALTH_FILE"
echo "Created health check API endpoint at $HEALTH_FILE"

# Check for main.py file and add router if it exists
MAIN_FILE="cc-webapp/backend/app/main.py"
if [ -f "$MAIN_FILE" ]; then
  # Check if health_router import already exists
  if ! grep -q "from app.api.health import health_router" "$MAIN_FILE"; then
    # Add import statement
    sed -i '/^from fastapi import/a from app.api.health import health_router' "$MAIN_FILE"
    # Add router to app
    sed -i '/app = FastAPI/a app.include_router(health_router, prefix="/api")' "$MAIN_FILE"
    echo "Added health_router to main.py"
  else
    echo "health_router already imported in main.py"
  fi
else
  echo "Creating minimal main.py file with health endpoint..."
  # Create a minimal main.py file
  cat > "$MAIN_FILE" << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.health import health_router

app = FastAPI(
    title="Casino-Club F2P API",
    description="API for Casino-Club F2P application",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
EOF
  echo "Created minimal main.py file"
fi

echo "====== Health Check API Endpoint Added ======"
echo "Endpoint: /api/health"
echo "Method: GET"
echo "Description: Returns health status of API and connected services"
