import random
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal
from app.tests._testdb import reset_db
from app.models import User

client = TestClient(app)


def setup_module(module):
    reset_db(engine)
    db = SessionLocal()
    global user_id
    try:
        u = User(site_id="shopper", nickname="shopper", phone_number="010", password_hash="x", invite_code="5858")
        db.add(u)
        db.commit()
        db.refresh(u)
        user_id = u.id
    finally:
        db.close()


def test_catalog_gold_applied_for_purchase():
    # product 1001 gold=100, quantity=2 => 200 gold
    random.seed(1)
    resp = client.post("/api/shop/buy", json={"user_id": user_id, "product_id": 1001, "quantity": 2})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["gold_granted"] == 200


def test_vip_guard_blocks_non_vip():
    resp = client.post("/api/shop/buy", json={"user_id": user_id, "product_id": 1004})
    assert resp.status_code == 403
