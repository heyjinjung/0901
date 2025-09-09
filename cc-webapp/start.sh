#!/bin/bash

# 백엔드 실행
cd backend
echo "▶ Starting backend on port 8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 프론트엔드 실행
cd ../frontend
echo "▶ Starting frontend on port 3000..."
npm run dev
