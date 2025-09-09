from fastapi.testclient import TestClient
import random
from app.main import app
from app.database import engine, SessionLocal
from app.tests._testdb import reset_db
from app.models import User

client = TestClient(app)

# Prepare DB and user like tests
reset_db(engine)
db = SessionLocal()
try:
    u = User(site_id="shopper_diag", nickname="shopper_diag", phone_number="010", password_hash="x", invite_code="5858")
    db.add(u)
    db.commit()
    db.refresh(u)
    user_id = u.id
finally:
    db.close()

# Happy path
random.seed(1)
resp = client.post('/api/shop/buy', json={'user_id': user_id, 'product_id': 1001, 'quantity': 2})
print('HAPPY status', resp.status_code)
print('HAPPY body', resp.json())

# VIP guard
resp2 = client.post('/api/shop/buy', json={'user_id': user_id, 'product_id': 1004})
print('VIP status', resp2.status_code)
print('VIP body', resp2.json())

# Payment fail
random.seed(999999)
resp3 = client.post('/api/shop/buy', json={'user_id': user_id, 'product_id': 1001})
print('FAIL status', resp3.status_code)
print('FAIL body', resp3.json())
