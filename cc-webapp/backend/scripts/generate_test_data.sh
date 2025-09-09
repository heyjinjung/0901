#!/bin/bash
set -e  # Exit immediately if a command fails

echo "====== Generating test data for Casino-Club F2P ======"

# Check if backend service is running
if ! docker-compose ps | grep -q "backend.*Up"; then
  echo "Error: Backend service is not running. Please start services first."
  echo "Run: docker-compose up -d"
  exit 1
fi

# Generate initial test data
echo "Generating basic test data..."
docker-compose exec -T backend python -c "
import sys
sys.path.append('/app')
from app.scripts.generate_test_data import generate_basic_data
generate_basic_data()
print('✅ Basic test data generated successfully')
"

# Generate game-related test data
echo "Generating game test data..."
docker-compose exec -T backend python -c "
import sys
sys.path.append('/app')
from app.scripts.generate_test_data import generate_game_data
generate_game_data()
print('✅ Game test data generated successfully')
"

# Generate user actions and rewards test data
echo "Generating user actions and rewards data..."
docker-compose exec -T backend python -c "
import sys
sys.path.append('/app')
from app.scripts.generate_test_data import generate_user_activity_data
generate_user_activity_data(days=7)
print('✅ User activity data for last 7 days generated successfully')
"

# Generate admin test account
echo "Creating admin test account..."
docker-compose exec -T backend python -c "
import sys
sys.path.append('/app')
from app.scripts.create_admin import create_test_admin
create_test_admin('admin@test.com', 'adminpass123')
print('✅ Admin test account created')
"

echo "====== Test data generation completed ======"
echo "Test credentials:"
echo "- Admin: admin@test.com / adminpass123"
echo "- Regular user: test@example.com / password123"
