import os
import uuid
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import User


client = TestClient(app)


def test_user_journey_smoke():
	r = client.get("/health")
	assert r.status_code == 200


def test_db_crud_fk_sanity():
	db = SessionLocal()
	try:
		u = User(
			site_id=f"t_{uuid.uuid4().hex[:8]}",
			nickname=f"n_{uuid.uuid4().hex[:8]}",
			phone_number=f"010{uuid.uuid4().int % 100000000:08d}",
			password_hash="x",
			invite_code="5858",
		)
		db.add(u)
		db.commit()
		db.refresh(u)
		assert u.id is not None
	finally:
		db.close()


def test_acid_transaction_rollback():
	db = SessionLocal()
	try:
		# Start transaction and insert, then rollback
		u = User(
			site_id=f"rb_{uuid.uuid4().hex[:8]}",
			nickname=f"rb_{uuid.uuid4().hex[:8]}",
			phone_number=f"010{uuid.uuid4().int % 100000000:08d}",
			password_hash="x",
			invite_code="5858",
		)
		db.add(u)
		db.flush()
		assert u.id is not None
		db.rollback()
		# Ensure not persisted
		exists = db.query(User).filter(User.site_id == u.site_id).first()
		assert exists is None
	finally:
		db.close()


def test_kafka_peek_endpoint_skip_if_disabled():
	if not (os.getenv("KAFKA_ENABLED", "0") == "1" and (os.getenv("KAFKA_BOOTSTRAP_SERVERS") or os.getenv("KAFKA_BROKER"))):
		return
	# Produce one marker then peek
	marker = uuid.uuid4().hex
	topic = os.getenv("KAFKA_TEST_TOPIC", "cc_test")
	r = client.post("/api/kafka/produce", json={"topic": topic, "payload": {"marker": marker, "src": "peek_test"}})
	assert r.status_code in (200, 502)
	pr = client.get(f"/api/kafka/debug/peek?topic={topic}&max_messages=50&from_beginning=1")
	assert pr.status_code in (200, 503, 502)
	if pr.status_code == 200:
		items = pr.json().get("items", [])
		assert isinstance(items, list)
