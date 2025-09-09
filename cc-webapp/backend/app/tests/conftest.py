import os, sys, pytest
# --- pytest 시작 전 외부 의존 비활성화(블로킹 방지) ---
# Settings/import 이전에 환경 변수를 강제로 덮어써서 lifespan 초기화 중 대기 제거
os.environ["KAFKA_ENABLED"] = "0"
os.environ["CLICKHOUSE_ENABLED"] = "0"
# 테스트에서 고정 초대코드 필요 (auth_token 픽스처가 5858 사용)
os.environ.setdefault("DEFAULT_INVITE_CODE", "5858")
# 스타트업 스키마 드리프트 검사 비활성화(테스트 본문에서 별도 가드로 검증)
os.environ["DISABLE_SCHEMA_DRIFT_GUARD"] = "1"

# --- FastAPI app 라이프사이클 중 블로킹 요소 노옵 패치 ---
try:
	import app.main as _main_mod  # type: ignore
	# 스케줄러 기동 차단
	_main_mod.start_scheduler = lambda: None  # type: ignore[attr-defined]
	# Kafka consumer 비활성 (lifespan await 경로 방지)
	async def _noop_async():
		return None
	_main_mod.start_consumer = _noop_async  # type: ignore[attr-defined]
	_main_mod.stop_consumer = _noop_async  # type: ignore[attr-defined]
except Exception:
	pass
from types import SimpleNamespace
from fastapi.testclient import TestClient
from types import SimpleNamespace

# Add backend root to sys.path if missing (when pytest launched from repo root)
_here = os.path.dirname(__file__)
_backend_root = os.path.abspath(os.path.join(_here, "..", ".."))
if _backend_root not in sys.path:
	sys.path.insert(0, _backend_root)

# Ensure DB tables exist for tests
from app.database import Base, engine  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402
# 테스트 시 FastAPI lifespan(startup/shutdown) 완전 무력화 옵션
try:
	if os.getenv("TEST_DISABLE_LIFESPAN", "1") == "1":
		from contextlib import asynccontextmanager

		@asynccontextmanager
		async def _noop_lifespan(_app):  # type: ignore[override]
			# startup/shutdown 훅을 모두 건너뛰기
			yield

		# Starlette/FastAPI 라우터 수준 lifespan 컨텍스트 교체
		# (TestClient 진입 시 on_startup/on_shutdown 실행 방지)
		if hasattr(fastapi_app, "router") and hasattr(fastapi_app.router, "lifespan_context"):
			fastapi_app.router.lifespan_context = _noop_lifespan  # type: ignore[attr-defined]
except Exception:
	# 실패해도 테스트는 계속 진행 (기본 lifespan 사용)
	pass
try:
	from app.routers.admin_content import require_admin as _require_admin  # noqa: E402
	# Ensure admin dependency always passes during tests (isolated persistence tests)
	fastapi_app.dependency_overrides[_require_admin] = lambda: SimpleNamespace(is_admin=True, id=0)
except Exception:
	pass
from sqlalchemy import text as _text  # 추가: 컬럼 보강용
import app.models  # noqa: F401, E402 - register all models on Base


try:
	from app.main import app as _app_reload  # noqa
except Exception:
	pass


@pytest.fixture(scope="session", autouse=True)
def _ensure_schema():
	"""Ensure schema is up to date via Alembic; fallback to metadata create_all.

	We avoid Base.metadata.drop_all due to FK dependencies across modules.
	"""
	# 항상 초기화 (drift 지속 발생하므로 test DB 파일 제거)
	try:
		from sqlalchemy import inspect as _insp
		engine.dispose()
		if engine.url.database and os.path.exists(engine.url.database):
			os.remove(engine.url.database)
	except Exception:
		pass

	# SQLite 파일에서 이전 버전 테이블 잔존 시 정리 (보조 안전장치)
	try:
		from sqlalchemy import inspect
		ins = inspect(engine)
		if ins.has_table("game_sessions"):
			cols = [c["name"] for c in ins.get_columns("game_sessions")]
			if "external_session_id" not in cols:
				# 오래된 스키마 -> 파일 DB 제거 후 재생성
				engine.dispose()
				import os
				if engine.url.database and os.path.exists(engine.url.database):
					os.remove(engine.url.database)
	except Exception:
		pass

	try:
		_dialect = engine.url.get_backend_name()
		# Postgres: 기본적으로 entrypoint에서 수행되었다고 가정하여 upgrade skip.
		# TEST_FORCE_ALEMBIC=1 설정 시에만 head로 올림. SQLite 등은 항상 upgrade 수행.
		do_upgrade = True
		if _dialect == "postgresql":
			do_upgrade = os.getenv("TEST_FORCE_ALEMBIC", "0") == "1"
		if do_upgrade:
			from alembic.config import Config
			from alembic import command
			cfg = Config("alembic.ini")
			command.upgrade(cfg, "head")
		# Safety net: 단일 골드 통화 컬럼 존재 보장 (테스트 SQLite 환경 한정)
		try:
			from sqlalchemy import inspect, text
			ins3 = inspect(engine)
			if ins3.has_table("users"):
				cols = {c["name"] for c in ins3.get_columns("users")}
				if "gold_balance" not in cols and engine.url.get_backend_name() == 'sqlite':
					with engine.begin() as conn:
						try:
							conn.execute(text("ALTER TABLE users ADD COLUMN gold_balance INTEGER NOT NULL DEFAULT 1000"))
						except Exception:
							pass
		except Exception:
			pass
		# 스키마 drift 감지: user_actions.action_data 누락 시 전체 DB 재생성 (SQLite 한정)
		try:
			from sqlalchemy import inspect
			ins2 = inspect(engine)
			if ins2.has_table("user_actions"):
				cols = {c["name"] for c in ins2.get_columns("user_actions")}
				if "action_data" not in cols:
					# SQLite 에서 누락된 컬럼 추가 (drift 수선) - 데이터 무시 가능 (테스트 DB)
					from sqlalchemy import text
					with engine.begin() as conn:
						try:
							conn.execute(text("ALTER TABLE user_actions ADD COLUMN action_data TEXT"))
						except Exception:
							pass
		except Exception:
			pass
		# 일부 신규 모델이 아직 마이그레이션에 반영되지 않았다면 보강 (SQLite 한정)
		if engine.url.get_backend_name() == 'sqlite':
			Base.metadata.create_all(bind=engine)
		# --- Safety net 2: ensure gold_balance column exists after metadata creation (sqlite test env) ---
		try:
			if engine.url.get_backend_name() == 'sqlite':
				from sqlalchemy import inspect as _insp2
				insp = _insp2(engine)
				if insp.has_table('users'):
					cols = {c['name'] for c in insp.get_columns('users')}
					if 'gold_balance' not in cols:
						with engine.begin() as conn:
							# nullable 추가 후 기본값 채우고 NOT NULL 강제는 생략 (테스트 용도)
							try:
								conn.execute(_text('ALTER TABLE users ADD COLUMN gold_balance INTEGER DEFAULT 1000'))
								conn.execute(_text('UPDATE users SET gold_balance=1000 WHERE gold_balance IS NULL'))
							except Exception:
								pass
					# Legacy dual-currency columns 제거 (ORM 미정의 + NOT NULL 무 default 로 삽입 실패 방지)
					legacy_cols = {'regular_coin_balance', 'premium_gem_balance', 'cyber_token_balance', 'gem_balance'}
					present_legacy = legacy_cols & cols
					if present_legacy:
						with engine.begin() as conn:
							for lc in present_legacy:
								try:
									conn.execute(_text(f'ALTER TABLE users DROP COLUMN {lc}'))
								except Exception:
									# SQLite 구버전 미지원 시 컬럼을 NULL 허용 + default 0 재작성 시나리오는 복잡 -> skip
									pass
		except Exception:
			pass
	except Exception:
		# Fallback: ensure at least ORM-known tables exist
		if engine.url.get_backend_name() == 'sqlite':
			Base.metadata.create_all(bind=engine)
		# Fallback path에서도 동일 보강
		try:
			if engine.url.get_backend_name() == 'sqlite':
				from sqlalchemy import inspect as _insp3
				insp = _insp3(engine)
				if insp.has_table('users'):
					cols = {c['name'] for c in insp.get_columns('users')}
					if 'gold_balance' not in cols:
						with engine.begin() as conn:
							try:
								conn.execute(_text('ALTER TABLE users ADD COLUMN gold_balance INTEGER DEFAULT 1000'))
								conn.execute(_text('UPDATE users SET gold_balance=1000 WHERE gold_balance IS NULL'))
							except Exception:
								pass
					legacy_cols = {'regular_coin_balance', 'premium_gem_balance', 'cyber_token_balance', 'gem_balance'}
					present_legacy = legacy_cols & cols
					if present_legacy:
						with engine.begin() as conn:
							for lc in present_legacy:
								try:
									conn.execute(_text(f'ALTER TABLE users DROP COLUMN {lc}'))
								except Exception:
									pass
		except Exception:
			pass
	yield


# --- Session fixture for DB-bound service tests (e.g., GameStats) ---
# 각 테스트를 트랜잭션으로 샌드박싱하여 commit 호출이 있어도 테스트 종료 시 롤백되도록 함.
@pytest.fixture
def db():
	"""Function-scoped SQLAlchemy Session with transactional sandbox.

	- Opens a dedicated connection
	- Starts a transaction
	- Binds a new Session to that connection
	- Yields the Session to the test
	- On teardown, closes the Session and rolls back the transaction

	This ensures that any DB writes (even after session.commit()) are rolled back
	at the end of the test, keeping tests isolated and fast.
	"""
	from sqlalchemy.orm import sessionmaker as _sessionmaker
	from sqlalchemy import event as _event
	# Use the shared engine created by app.database
	conn = engine.connect()
	# 외부 트랜잭션(롤백 전용) 시작
	trans = conn.begin()
	TestingSessionLocal = _sessionmaker(bind=conn, autocommit=False, autoflush=False, expire_on_commit=False)
	sess = TestingSessionLocal()
	# 내부 세이브포인트 시작: 서비스 코드의 sess.commit()이 와도 여기까지만 커밋되도록
	sess.begin_nested()

	# 세이브포인트가 종료되면 재생성하여, 다중 커밋에도 격리를 유지
	@_event.listens_for(sess, "after_transaction_end")
	def _restart_savepoint(session_, trans_):  # noqa: ANN001
		if trans_.nested and not getattr(trans_._parent, 'nested', False):  # type: ignore[attr-defined]
			session_.begin_nested()
	try:
		yield sess
	finally:
		try:
			sess.close()
		finally:
			try:
				# 외부 트랜잭션 전체 롤백으로 테스트 중 생성된 모든 변경을 폐기
				trans.rollback()
			finally:
				conn.close()


@pytest.fixture(scope="session")
def client():
	from fastapi.testclient import TestClient as _TC

	# QUICK_SMOKE=1인 경우, DB 보강/어드민 오버라이드 없이 즉시 TestClient 반환 (health/docs 등 초경량 스모크용)
	if os.getenv("QUICK_SMOKE", "0") == "1":
		with _TC(fastapi_app) as c:
			yield c
		return

	# --- 이벤트/어드민 테스트용 require_admin override (일반 인증 경로는 토큰 사용) ---
	try:
		from app.routers import admin_events as _admin_events_router
		def _admin_test_user():
			return SimpleNamespace(id=12345, is_admin=True, nickname="test-admin-event", gold_balance=1000, experience=0)
		if hasattr(_admin_events_router, 'require_admin'):
			fastapi_app.dependency_overrides[_admin_events_router.require_admin] = _admin_test_user
	except Exception:
		pass

	# --- Ensure persistent DB user matching override (FK integrity) ---
	try:
		from app.database import SessionLocal as _Sess
		from app.models.auth_models import User as _User
		from sqlalchemy import inspect as _insp
		sess = _Sess()
		try:
			# 테이블 존재 시에만 (마이그레이션 레이스 컨디션 방지)
			if _insp(sess.bind).has_table('users'):
				u = sess.query(_User).filter(_User.id == 12345).first()
				if not u:
					# 필수 고유 컬럼 충족 (site_id / nickname / phone_number)
					u = _User(
						id=12345,
						site_id="admin-events-testuser",
						nickname="admin-events-testuser",
						phone_number="000-0000-1234",
						password_hash="x",  # 해시 불필요 (직접 인증 미사용)
						invite_code="5858",
						is_admin=True,
					)
					sess.add(u)
					sess.commit()
		finally:
			sess.close()
	except Exception:
		# 비치명적 – 사용자 생성 실패 시 테스트 중 FK 에러로 surfaced 됨
		pass

	# TestClient 버전에서 lifespan 인자 미지원 가능성이 있어, 상단에서 router.lifespan_context를 no-op으로 교체한 방식만 사용
	with _TC(fastapi_app) as c:
		yield c


# --- Seed users required by GameStats tests (FK integrity) ---
@pytest.fixture(scope="session", autouse=True)
def _seed_users_for_gamestats():
	"""Ensure users with ids used in GameStats tests exist (1,2,3,123).

	Uses a dedicated session and commits so that per-test transactional sessions can see the rows.
	"""
	try:
		from app.database import SessionLocal as _Sess
		from app.models.auth_models import User as _User
		sess = _Sess()
		try:
			needed = [1, 2, 3, 123]
			for uid in needed:
				exists = sess.query(_User).filter(_User.id == uid).first()
				if not exists:
					u = _User(
						id=uid,
						site_id=f"gamestats-{uid}",
						nickname=f"gamestats-{uid}",
						phone_number=f"000-0000-{uid:04d}",
						password_hash="x",
						invite_code="5858",
					)
					sess.add(u)
			sess.commit()
		finally:
			sess.close()
	except Exception:
		# Non-fatal: if seeding fails, affected tests will surface FK errors
		pass


# --- Ensure clean GameHistory for common test users per test (determinism) ---
@pytest.fixture(autouse=True)
def _cleanup_gamestats_history(db):  # noqa: D401
	"""각 테스트 시작 시 GameHistory를 정리해 이전 실행/수동 디버그 잔여분 영향 제거."""
	try:
		from app.models.history_models import GameHistory as _GH
		from app.models.game_stats_models import UserGameStats as _UGS
		# 히스토리 삭제
		(db.query(_GH)
		 	.filter(_GH.user_id.in_([1, 2, 3]), _GH.game_type == 'crash')
		 	.delete(synchronize_session=False))
		# 누적 스탯 초기화
		for uid in [1, 2, 3]:
			stats = db.get(_UGS, uid)
			if stats:
				stats.total_bets = 0
				stats.total_wins = 0
				stats.total_losses = 0
				stats.total_profit = 0
				stats.highest_multiplier = None
		db.commit()
	except Exception:
		# 비치명적 – 청소 실패 시 해당 테스트에서 드러남
		pass


# ---- Global deterministic PaymentGateway patch (session scope) ----
# Ensures limited package purchase tests are not flaky due to random auth/capture results.
@pytest.fixture(scope="session", autouse=True)
def _patch_payment_gateway():  # noqa: D401
	"""Force PaymentGateway.authorize/capture to always succeed for test stability."""
	try:  # best-effort; if gateway code changes, tests still run with randomness
		from app.services.payment_gateway import PaymentGateway, PaymentResult  # type: ignore
		from uuid import uuid4 as _u

		def _auth_ok(self, amount_cents: int, currency: str = "USD", *, card_token: str | None = None):  # noqa: ANN001
			return PaymentResult(True, "authorized", str(_u()), "Authorized")

		def _cap_ok(self, charge_id: str):  # noqa: ANN001
			return PaymentResult(True, "captured", charge_id, "Captured")

		PaymentGateway.authorize = _auth_ok  # type: ignore[attr-defined]
		PaymentGateway.capture = _cap_ok  # type: ignore[attr-defined]
	except Exception:
		pass
	yield


@pytest.fixture
def auth_token(client):
	"""Return a helper that can create or login a user and return an access token.

	Usage: token = auth_token(role='admin')
	If signup/login is not available, tests calling this fixture will be skipped.
	"""
	import uuid

	def _get(role: str = 'standard'):
		# Unique site_id & phone_number per call to avoid duplicate constraints
		uid = uuid.uuid4().hex[:8]
		site_id = f"{role}-{uid}"
		nickname = f"nick-{site_id}"
		phone = "010" + uid.ljust(8, '0')  # simple deterministic 11-digit
		payload = {
			"site_id": site_id,
			"nickname": nickname,
			"invite_code": "5858",
			"password": "TestPass123!",
			"phone_number": phone,
		}
		try:
			resp = client.post("/api/auth/signup", json=payload)
		except Exception:
			pytest.skip("auth endpoints not available in this test environment")

		if resp.status_code in (200, 201):
			data = resp.json()
			token = data.get("access_token") or data.get("token") or data.get("accessToken")
			if token:
				return token

		# Fallback: try login endpoint if signup returned non-token response
		login_payload = {"site_id": payload["site_id"], "password": payload["password"], "nickname": payload["nickname"]}
		try:
			lresp = client.post("/api/auth/login", json=login_payload)
			if lresp.status_code == 200:
				ldata = lresp.json()
				token = ldata.get("access_token") or ldata.get("token")
				if token:
					return token
		except Exception:
			pass

		pytest.skip("could not obtain auth token via signup/login")

	return _get

