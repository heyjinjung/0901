from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine
from app.tests._testdb import reset_db
from app.models import User
import json


def main():
    try:
        reset_db(engine)
    except Exception as e:
        print('reset_db failed:', e)
    db = SessionLocal()
    try:
        u = User(site_id="shopper", nickname="shopper", phone_number="010", password_hash="x", invite_code="5858")
        db.add(u)
        db.commit()
        db.refresh(u)
        uid = u.id
    finally:
        db.close()

    client = TestClient(app)

    def do(payload):
        r = client.post("/api/shop/buy", json=payload)
        out = {"payload": payload, "status": r.status_code}
        try:
            out["body"] = r.json()
        except Exception:
            out["text"] = r.text
        print(json.dumps(out, ensure_ascii=False, indent=2))

    print('\n=== HAPPY PATH ===')
    do({"user_id": uid, "product_id": 1001, "quantity": 2})

    print('\n=== VIP GUARD ===')
    do({"user_id": uid, "product_id": 1004})

    print('\n=== PAYMENT FAIL ===')
    do({"user_id": uid, "product_id": 1001})


if __name__ == '__main__':
    main()
