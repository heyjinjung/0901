import os
from sqlalchemy import text
from sqlalchemy.engine import Engine


def reset_db(engine: Engine) -> None:
    """Reset the current schema for tests.

    변경 사항:
    - 기본값: RESTART IDENTITY 비활성 (시퀀스 유지) → 데이터만 TRUNCATE 후 각 주요 시퀀스 setval 보정
    - 환경변수 TEST_DB_RESTART_IDENTITY=true 일 때만 RESTART IDENTITY CASCADE 수행

    이유:
    - RESTART IDENTITY 가 다중 실행/부분 재사용 시 낮은 id 재사용으로 user 기반 로직(per-user limit 등) 오작동 유발
    - max(id)+1 로 보정(setval) 하면 누적 id 증가 방식 유지되어 충돌 방지
    """
    with engine.connect() as conn:
        # Drop dependent views first (best-effort)
        try:
            conn.execute(text("DROP VIEW IF EXISTS gacha_log CASCADE"))
        except Exception:
            pass

        # Collect all tables in the current schema
        rows = conn.execute(
            text(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = current_schema()
                """
            )
        ).fetchall()
        table_names = [r[0] for r in rows]

        if table_names:
            idents = ", ".join([f'"{n}"' for n in table_names])
            restart_flag = os.getenv("TEST_DB_RESTART_IDENTITY", "false").lower() == "true"
            if restart_flag:
                conn.execute(text(f"TRUNCATE TABLE {idents} RESTART IDENTITY CASCADE"))
            else:
                conn.execute(text(f"TRUNCATE TABLE {idents} CASCADE"))
                # 핵심 user 관련 시퀀스 보정 (존재 시)
                try:
                    seqs = conn.execute(
                        text(
                            """
                            SELECT sequence_name
                            FROM information_schema.sequences
                            WHERE sequence_schema = current_schema()
                              AND (sequence_name LIKE 'users%_id_seq' OR sequence_name='users_id_seq')
                            """
                        )
                    ).fetchall()
                except Exception:
                    seqs = []
                # users_id_seq + 기타 user_* 시퀀스 대상 max(id)+1 보정 (존재 컬럼 가정: id)
                for (seq_name,) in seqs:
                    table_guess = seq_name.rsplit('_id_seq', 1)[0]
                    try:
                        max_id = conn.execute(text(f"SELECT COALESCE(MAX(id),0) FROM {table_guess}"))
                        max_val = max_id.scalar() or 0
                        target = max_val + 1
                        conn.execute(text("SELECT setval(:seq, :target, false)"), {"seq": seq_name, "target": target})
                    except Exception:
                        # best-effort: 특정 테이블이 없거나 id 컬럼 없으면 스킵
                        pass

        conn.commit()
