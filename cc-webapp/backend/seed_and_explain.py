import os, random, datetime, sys
from sqlalchemy import text, create_engine

DB_URL = os.getenv("SQLALCHEMY_DATABASE_URI") or os.getenv("DATABASE_URL") or "postgresql://cc_user:cc_password@cc_postgres:5432/cc_webapp"
engine = create_engine(DB_URL)

ROWS = int(os.getenv("SEED_ROWS", "5000"))
now = datetime.datetime.utcnow()

GAME_TYPES = ["slot","gacha","crash"]

with engine.begin() as conn:
    # 실제 시드 계정(site_id) 기준 user_id 목록 조회 (멱등/안전)
    seed_site_ids = os.getenv("SEED_USER_SITE_IDS", "admin,user001,user002,user003,user004").split(",")
    seed_site_ids = [s.strip() for s in seed_site_ids if s.strip()]
    rows = conn.execute(
        text("SELECT id, site_id FROM users WHERE site_id = ANY(:ids) ORDER BY id")
        .bindparams(ids=seed_site_ids)
    ).fetchall()

    seed_user_ids = [r[0] for r in rows]
    if not seed_user_ids:
        print("[seed_and_explain] 시드 유저를 찾지 못했습니다. 먼저 기본 계정을 생성하세요: python -m app.scripts.seed_basic_accounts", file=sys.stderr)
        sys.exit(1)

    # seed game_sessions (시드 유저 범위 내)
    for i in range(ROWS):
        uid = random.choice(seed_user_ids)
        gt = random.choice(GAME_TYPES)
        start = now - datetime.timedelta(minutes=random.randint(0, 10000))
        total_rounds = random.randint(1, 30)
        total_bet = random.randint(10, 5000)
        total_win = int(total_bet * random.uniform(0, 2))
        status = random.choice(["active","ended","aborted"]) if random.random() < 0.9 else "ended"
        conn.execute(text("""
            INSERT INTO game_sessions (external_session_id,user_id,game_type,initial_bet,total_win,total_bet,total_rounds,start_time,end_time,status,created_at)
            VALUES (:sid,:uid,:gt,:ib,:tw,:tb,:tr,:st,:et,:status,:created)
            ON CONFLICT (external_session_id) DO NOTHING
        """), {
            "sid": f"seed-{i}-{uid}-{gt}",
            "uid": uid,
            "gt": gt,
            "ib": random.randint(1, 100),
            "tw": total_win,
            "tb": total_bet,
            "tr": total_rounds,
            "st": start,
            "et": start + datetime.timedelta(minutes=total_rounds),
            "status": status,
            "created": start,
        })

    # seed shop_transactions (통화 kind를 gold로 표준화)
    for i in range(ROWS):
        uid = random.choice(seed_user_ids)
        amount = random.randint(100, 10000)
        created = now - datetime.timedelta(hours=random.randint(0, 24 * 14))
        conn.execute(text("""
            INSERT INTO shop_transactions (user_id, product_id, kind, quantity, unit_price, amount, status, created_at)
            VALUES (:uid,'prod-basic','gold',1,:amt,:amt,'success',:created)
        """), {"uid": uid, "amt": amount, "created": created})

    # seed notifications (테이블이 없으면 무시)
    try:
        for i in range(ROWS):
            uid = random.choice(seed_user_ids)
            created = now - datetime.timedelta(hours=random.randint(0, 240))
            is_read = random.random() < 0.7
            conn.execute(text("""
                INSERT INTO notifications (user_id, is_read, created_at)
                VALUES (:uid, :is_read, :created)
            """), {"uid": uid, "is_read": is_read, "created": created})
    except Exception:
        pass

print("Seed complete")

EXPLAINS = []
try:
    # 하나의 시드 유저를 고정 대상으로 사용
    sample_uid = seed_user_ids[0]
    EXPLAINS = [
        ("recent_sessions", f"EXPLAIN SELECT * FROM game_sessions WHERE user_id={sample_uid} AND game_type='slot' ORDER BY start_time DESC LIMIT 20"),
        ("purchase_sum", f"EXPLAIN SELECT SUM(amount) FROM shop_transactions WHERE user_id={sample_uid} AND created_at >= NOW() - INTERVAL '7 days'"),
        ("unread_count", f"EXPLAIN SELECT COUNT(*) FROM notifications WHERE user_id={sample_uid} AND is_read = false"),
    ]
except Exception:
    # 조회 실패 시 EXPLAIN 생략
    EXPLAINS = []

with engine.connect() as conn:
    for name, sql in EXPLAINS:
        print(f"--- {name} ---")
        for row in conn.execute(text(sql)):
            print(row[0])
