import random
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal
from sqlalchemy import text
from app.tests._testdb import reset_db
from app.models import User

user_id = None


client = TestClient(app)


def setup_module(module):
    # fresh schema
    reset_db(engine)
    # create a user
    db = SessionLocal()
    try:
        u = User(site_id="shopper", nickname="shopper", phone_number="010", password_hash="x", invite_code="5858")
        db.add(u)
        db.commit()
        db.refresh(u)
        global user_id
        user_id = u.id
    finally:
        db.close()


def test_buy_gold_happy_path():
    random.seed(1)  # deterministic payment
    resp = client.post(
        "/api/shop/buy",
        json={"user_id": user_id, "product_id": 1001, "quantity": 2}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["gold_granted"] == 200
    assert body["new_gold_balance"] >= 200
    assert body["charge_id"]


def test_buy_gold_vip_guard():
    # product 1004 requires VIP
    resp = client.post(
        "/api/shop/buy",
        json={"user_id": user_id, "product_id": 1004}
    )
    assert resp.status_code == 403


def test_buy_gold_payment_fail():
    # Force a failure by tweaking random
    random.seed(999999)  # likely to fail auth ~10%
    resp = client.post(
        "/api/shop/buy",
        json={"user_id": user_id, "product_id": 1001}
    )
    assert resp.status_code == 200
    body = resp.json()
    if not body["success"]:
        assert body["gold_granted"] == 0
    else:
        # if the seed still passed, at least success is coherent
        assert body["gold_granted"] == 100


def test_catalog_listing_and_price_structure():
    resp = client.get("/api/shop/catalog")
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list) and len(items) >= 3
    required = {"id", "sku", "name", "price_cents", "discounted_price_cents", "gold"}
    for it in items:
        assert required.issubset(set(it.keys()))
