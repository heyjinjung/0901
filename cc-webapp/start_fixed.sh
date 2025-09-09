#!/bin/bash

# Start the backend server with the fixed main file
cd $(dirname "$0")
cd backend

echo "Starting backend server with fixed main file..."
uvicorn app.main_fixed:app --host 0.0.0.0 --port 8000 --reload
