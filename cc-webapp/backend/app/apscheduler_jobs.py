# cc-webapp/backend/app/apscheduler_jobs.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.schedulers.background import BackgroundScheduler # if not using asyncio for FastAPI
from .utils.segment_utils import compute_rfm_and_update_segments
from .services.campaign_dispatcher import dispatch_due_campaigns
from . import models
# Ensure database.py defines SessionLocal. If it's not created yet, this import will fail at runtime.
# For now, assuming database.py and SessionLocal will be available.
from .database import SessionLocal
from datetime import datetime, timedelta
import logging # For better logging from scheduler

# Configure logging for APScheduler for better visibility
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.INFO)


# Using AsyncIOScheduler as FastAPI is async
scheduler = AsyncIOScheduler(timezone="UTC") # Or your preferred timezone


def cleanup_stale_pending_transactions(max_age_minutes: int = None):
    """VOID/취소 처리: 오래된 pending 결제 트랜잭션을 자동 정리.

    기준:
      - status == 'pending'
      - kind in ('gems','item','?') 제한하지 않고 pending 인 것 모두
      - created_at < now - max_age_minutes
    액션:
      - status -> 'voided'
      - failure_reason = 'STALE_AUTO_VOID'
    참고: status 컬럼은 자유 문자열이므로 별도 마이그레이션 불필요.
    """
    db = None
    try:
        db = SessionLocal()
        # 환경변수 우선
        if max_age_minutes is None:
            import os
            try:
                max_age_minutes = int(os.getenv("PENDING_TX_MAX_AGE_MINUTES", "5"))
            except Exception:
                max_age_minutes = 5
        cutoff = datetime.utcnow() - timedelta(minutes=max_age_minutes)
        # 테이블 존재 여부 방어
        try:
            # Defensive: ensure the ShopTransaction model/table and expected columns exist.
            # This avoids ProgrammingError when migrations are out-of-sync.
            # We do a lightweight existence check using SQLAlchemy's inspection via table name.
            from sqlalchemy import inspect
            inspector = inspect(db.bind)
            if 'shop_transactions' not in inspector.get_table_names():
                print(f"[{datetime.utcnow()}] APScheduler: cleanup skipped - table 'shop_transactions' not present.")
                return 0

            # Check that expected column(s) exist to avoid SELECT referencing missing columns
            try:
                col_names = [c['name'] for c in inspector.get_columns('shop_transactions')]
            except Exception:
                print(f"[{datetime.utcnow()}] APScheduler: cleanup skipped - could not inspect 'shop_transactions' columns.")
                return 0
            # Legacy schemas may lack some columns (e.g., 'extra').
            # If required columns for ORM-mapped model are missing, skip to avoid ProgrammingError
            required_for_safe_query = {'status', 'created_at', 'failure_reason'}
            if 'receipt_signature' not in col_names:
                print(f"[{datetime.utcnow()}] APScheduler: cleanup skipped - column 'receipt_signature' not present in 'shop_transactions'.")
                return 0
            if 'extra' not in col_names:
                print(f"[{datetime.utcnow()}] APScheduler: cleanup skipped - column 'extra' not present in 'shop_transactions' (legacy schema).")
                return 0
            if not required_for_safe_query.issubset(set(col_names)):
                print(f"[{datetime.utcnow()}] APScheduler: cleanup skipped - required columns missing: {required_for_safe_query - set(col_names)}")
                return 0

            # 조건에 맞는 row 수만 먼저 count -> 과도한 업데이트 방지
            stale_q = (
                db.query(models.ShopTransaction)
                .filter(models.ShopTransaction.status == 'pending', models.ShopTransaction.created_at < cutoff)
            )
            stale_count = stale_q.count()
            if stale_count == 0:
                return 0
            # Batch update (row-by-row to set reason + future extensibility)
            updated = 0
            for tx in stale_q.limit(500):  # 1회 실행당 최대 500개 (필요시 반복 실행)
                tx.status = 'voided'
                fr = (tx.failure_reason or '')
                if 'STALE_AUTO_VOID' not in fr:
                    tx.failure_reason = (fr + ';' if fr else '') + 'STALE_AUTO_VOID'
                updated += 1
            db.commit()
            print(f"[{datetime.utcnow()}] APScheduler: Auto-voided {updated} stale pending transactions (> {max_age_minutes}m).")
            return updated
        except Exception as e:
            # Catch and log without propagating to let scheduler continue running.
            try:
                db.rollback()
            except Exception:
                pass
            print(f"[{datetime.utcnow()}] APScheduler: cleanup_stale_pending_transactions error (guarded): {e}")
            logging.exception("cleanup_stale_pending_transactions guarded error")
            return 0
    finally:
        if db:
            db.close()

def job_function():
    """Wrapper to manage DB session for the scheduled job."""
    db = None
    try:
        db = SessionLocal()
        print(f"[{datetime.utcnow()}] APScheduler: Running compute_rfm_and_update_segments job.")
        compute_rfm_and_update_segments(db)
        # Also dispatch due campaigns
        try:
            dispatched = dispatch_due_campaigns(db)
            if dispatched:
                print(f"[{datetime.utcnow()}] APScheduler: Dispatched {dispatched} campaigns.")
        except Exception as e:
            print(f"[{datetime.utcnow()}] APScheduler: Error dispatching campaigns: {e}")
        print(f"[{datetime.utcnow()}] APScheduler: compute_rfm_and_update_segments job finished.")
    except Exception as e:
        print(f"[{datetime.utcnow()}] APScheduler: Error in job_function: {e}")
        logging.exception("APScheduler job_function error") # Log full traceback
    finally:
        if db:
            db.close()

def start_scheduler():
    if scheduler.running:
        print(f"[{datetime.utcnow()}] APScheduler: Scheduler already running.")
        return

    # Schedule to run daily at 2 AM UTC and also every 5 minutes for campaign dispatch
    scheduler.add_job(job_function, 'cron', hour=2, minute=0, misfire_grace_time=3600) # Misfire grace time of 1hr
    scheduler.add_job(job_function, 'interval', minutes=5, misfire_grace_time=300)
    # Stale pending transaction cleanup: every minute
    scheduler.add_job(cleanup_stale_pending_transactions, 'interval', minutes=1, misfire_grace_time=60)

    # Run once on startup for local testing/verification (5 seconds after app start)
    # This helps confirm the job setup without waiting for 2 AM.
    scheduler.add_job(job_function, 'date', run_date=datetime.now() + timedelta(seconds=10))

    try:
        scheduler.start()
        print(f"[{datetime.utcnow()}] APScheduler: Started successfully. RFM job + stale pending cleanup scheduled.")
    except Exception as e:
        print(f"[{datetime.utcnow()}] APScheduler: Error starting: {e}")
        logging.exception("APScheduler startup error")


# To integrate with FastAPI, call start_scheduler() in main.py's startup event
# Example in app/main.py:
# from .apscheduler_jobs import start_scheduler
# @app.on_event("startup")
# async def startup_event():
#     print("FastAPI startup event: Initializing scheduler...")
#     start_scheduler()
#
# @app.on_event("shutdown")
# async def shutdown_event():
#     if scheduler.running:
#          scheduler.shutdown()
