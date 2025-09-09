import concurrent.futures, uuid
from datetime import datetime, timedelta
from app.database import SessionLocal
from app import models
from app.services.auth_service import AuthService, SECRET_KEY, ALGORITHM

from jose import jwt


def _create_user_and_token():
    sess = SessionLocal()
    try:
        u = models.User(
            site_id=f"race-{uuid.uuid4().hex[:8]}",
            nickname=f"race-nick-{uuid.uuid4().hex[:6]}",
            phone_number=f"010{uuid.uuid4().hex[:8]}",
            password_hash=AuthService.get_password_hash("Pass1234!"),
            invite_code="5858",
        )
        sess.add(u)
        sess.commit()
        sess.refresh(u)
        payload = {
            "sub": u.site_id,
            "user_id": u.id,
            "is_admin": False,
        }
        token = AuthService.create_access_token(payload, expires_delta=timedelta(minutes=15))
        return u.id, token
    finally:
        sess.close()


def test_race_idempotent_purchase_conversion(client):
    user_id, token = _create_user_and_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 고립된 conversion 상품 생성
    conv_id = f"RCONV_{uuid.uuid4().hex[:8]}"
    session = SessionLocal()
    try:
        p = models.ShopProduct(
            product_id=conv_id,
            name="Race Conv",
            price=1000,
            is_active=True,
            extra={"category": "conversion", "gold_out": 1000},
        )
        session.add(p)
        session.commit()
    finally:
        session.close()

    idem = uuid.uuid4().hex

    def do_req():
        return client.post(
            "/api/shop/purchase",
            json={"product_id": conv_id, "idempotency_key": idem},
            headers=headers,
        )

    # 병렬 5 요청
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futures = [ex.submit(do_req) for _ in range(5)]
        results = [f.result() for f in futures]

    successes = [r for r in results if r.status_code == 200 and r.json().get("success")]
    assert len(successes) == 5, [r.status_code for r in results]

    firsts = [r for r in successes if not r.json().get("idempotent")]
    assert len(firsts) == 1, f"expected exactly 1 non-idempotent success, got {len(firsts)}"

    after_balances = {r.json().get("gold_after") for r in successes}
    assert len(after_balances) == 1, after_balances

    # 트랜잭션 테이블에 실제 성공 row 1개만 존재 확인 (idempotent_key 동일)
    session = SessionLocal()
    try:
        count = session.query(models.ShopTransaction).filter(
            models.ShopTransaction.user_id == user_id,
            models.ShopTransaction.product_id == conv_id,
            models.ShopTransaction.idempotency_key == idem,
            models.ShopTransaction.status == 'success',
        ).count()
    finally:
        session.close()
    assert count == 1, f"expected 1 transaction row, got {count}"
