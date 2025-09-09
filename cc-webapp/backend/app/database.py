"SQLAlchemy engine and session configuration."
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import time

# Base class for all models
Base = declarative_base()

def get_database_url():
    """Return database URL based on environment"""
    # Docker/Production environment - PostgreSQL
    postgres_server = os.getenv('POSTGRES_SERVER')
    postgres_user = os.getenv('POSTGRES_USER')
    postgres_password = os.getenv('POSTGRES_PASSWORD')
    postgres_db = os.getenv('POSTGRES_DB')
    
    if postgres_server and postgres_user and postgres_password and postgres_db:
        return f"postgresql://{postgres_user}:{postgres_password}@{postgres_server}:5432/{postgres_db}"
    
    # Fallback to legacy environment variables
    if os.getenv('DB_HOST'):
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'cc_webapp')
        db_user = os.getenv('DB_USER', 'cc_user')
        db_password = os.getenv('DB_PASSWORD', 'cc_password')
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    # 개발 환경 fallback - SQLite (only when no Postgres env)
    return os.getenv("DATABASE_URL", "sqlite:///./auth.db")

# 데이터베이스 URL 설정
DATABASE_URL = get_database_url()

# PostgreSQL vs SQLite 연결 옵션
if DATABASE_URL.startswith("postgresql"):
    connect_args = {}
    echo = os.getenv('DEBUG', 'false').lower() == 'true'
else:
    connect_args = {"check_same_thread": False}
    echo = False

def _create_engine_with_retry(url: str):
    """Create engine with retry for Postgres; avoid SQLite fallback when Postgres env is configured.

    In containerized env (POSTGRES_* set), we should not silently fallback to SQLite.
    Instead, retry until Postgres is ready, then raise to let the container restart if still failing.
    """
    is_postgres = url.startswith("postgresql")
    has_postgres_env = all(
        os.getenv(k) for k in ("POSTGRES_SERVER", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB")
    )

    if is_postgres:
        attempts = int(os.getenv("DB_CONNECT_RETRIES", "30"))
        delay = float(os.getenv("DB_CONNECT_RETRY_DELAY", "1.0"))
        last_err: Exception | None = None
        for i in range(1, attempts + 1):
            try:
                eng = create_engine(url, connect_args=connect_args, echo=echo)
                with eng.connect():
                    pass
                print(f"✅ 데이터베이스 연결 성공: {url.split('@')[-1] if '@' in url else url}")
                return eng
            except Exception as e:
                last_err = e
                print(f"⏳ 데이터베이스 연결 재시도 {i}/{attempts}: {e}")
                time.sleep(delay)
        # If we reach here, all retries failed.
        # If Postgres env is present, do NOT fallback to SQLite (to avoid split-brain between DBs).
        if has_postgres_env:
            raise RuntimeError(f"Postgres 연결 실패 (재시도 {attempts}회): {last_err}")
        # Otherwise, allow fallback for local dev (rare path when url constructed as postgres but no envs)
        print("⚠️ Postgres 연결 실패, 개발 모드로 SQLite로 폴백합니다.")
        fb_url = "sqlite:///./fallback.db"
        eng = create_engine(fb_url, connect_args={"check_same_thread": False})
        print(f"🔄 Fallback 데이터베이스 사용: {fb_url}")
        return eng
    else:
        # SQLite or other DBs: create directly
        eng = create_engine(url, connect_args=connect_args, echo=echo)
        try:
            with eng.connect():
                pass
        except Exception as e:
            # As a last resort for dev, use fallback SQLite
            print(f"⚠️ 주 데이터베이스 연결 실패: {e}")
            fb_url = "sqlite:///./fallback.db"
            eng = create_engine(fb_url, connect_args={"check_same_thread": False})
            print(f"🔄 Fallback 데이터베이스 사용: {fb_url}")
        else:
            print(f"✅ 데이터베이스 연결 성공: {url}")
        return eng

# Create engine with robust behavior
engine = _create_engine_with_retry(DATABASE_URL)

# ---------------------------------------------------------------------------
# SQLite compatibility: emulate NOW() for models using server_default=func.now()
# ---------------------------------------------------------------------------
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _register_sqlite_now(dbapi_connection, connection_record):  # type: ignore
        try:
            # Register only if not already present
            dbapi_connection.create_function("now", 0, lambda: __import__("datetime").datetime.utcnow().isoformat())
        except Exception:
            # Silent: function might already exist or driver doesn't support create_function
            pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_url():
    """현재 데이터베이스 URL 반환"""
    return DATABASE_URL

def get_db():
    """Database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()