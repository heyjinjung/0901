"""시퀀스 헬스 & 정리 유틸리티 (확장판).

기본 사용자(users) 전용 + 다중 시퀀스 스캔 기능.

사용 (backend 컨테이너 내부):
    # 단일 users 시퀀스 점검/수정
    python -m scripts.user_sequence_health --check
    python -m scripts.user_sequence_health --fix

    # 모든 *_id_seq 스캔 (현재 스키마)
    python -m scripts.user_sequence_health --scan-all
    python -m scripts.user_sequence_health --fix-all --dry-run
    python -m scripts.user_sequence_health --fix-all --confirm YES_SEQ_FIX

    # 논시드 사용자 정리
    python -m scripts.user_sequence_health --purge-nonseed --dry-run
    python -m scripts.user_sequence_health --purge-nonseed --confirm YES_PURGE

기능:
 - users_id_seq drift 체크/보정
 - 모든 *_id_seq (테이블명 + '_id_seq') 스캔: max(id) 대비 next allocation drift 보고
 - --fix-all: 각 테이블 max(id)+1 로 setval (RESTART IDENTITY 사용 안함)
 - 논시드 사용자 삭제 (admin/seed/system 패턴 보존)

안전:
 - 파괴적 작업(purge, fix-all)은 --confirm 토큰 없으면 실행 안함 (dry-run 제외)
 - 테이블 존재 여부/ id 컬럼 미존재 시 자동 스킵
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Sequence, List, Tuple
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://cc_user:cc_password@postgres:5432/cc_webapp")
SEED_PATTERNS = ["admin", "seed", "system"]  # simple heuristics


def get_engine():  # lazy
    return create_engine(DATABASE_URL)


def _fetch_one(conn, sql: str):
    return conn.execute(text(sql)).fetchone()


def check_sequence(conn) -> tuple[int, int | None]:
    max_id_row = _fetch_one(conn, "SELECT COALESCE(MAX(id),0) AS max_id FROM users")
    seq_row = _fetch_one(conn, "SELECT last_value, is_called FROM users_id_seq")
    max_id = max_id_row.max_id  # type: ignore
    # next value semantics: if is_called is false, next nextval returns last_value, else last_value+1
    next_alloc = seq_row.last_value if not seq_row.is_called else seq_row.last_value + 1  # type: ignore
    return max_id, next_alloc


def fix_sequence(conn) -> int:
    max_id_row = _fetch_one(conn, "SELECT COALESCE(MAX(id),0) AS max_id FROM users")
    target = max_id_row.max_id + 1  # type: ignore
    conn.execute(text("SELECT setval('users_id_seq', :target, false)"), {"target": target})
    return target


def purge_nonseed(conn, dry_run: bool) -> int:
    # identify keepers
    keep_conditions = ["is_admin = true"] + [f"site_id ILIKE '%{p}%'" for p in SEED_PATTERNS]
    where_keep = " OR ".join(keep_conditions)
    # select victims first
    victims = conn.execute(text(f"SELECT id FROM users WHERE NOT ({where_keep})")).fetchall()
    count = len(victims)
    if count and not dry_run:
        conn.execute(text(f"DELETE FROM users WHERE NOT ({where_keep})"))
    return count


def scan_all_sequences(conn) -> List[Tuple[str, int, int, int]]:
    """모든 *_id_seq 시퀀스 스캔.
    반환: [(seq_name, max_id, next_alloc, drift)]
    drift = next_alloc - (max_id+1)
    """
    rows = conn.execute(
        text(
            """
            SELECT sequence_name
            FROM information_schema.sequences
            WHERE sequence_schema = current_schema()
              AND sequence_name LIKE '%_id_seq'
            ORDER BY sequence_name
            """
        )
    ).fetchall()
    results: List[Tuple[str, int, int, int]] = []
    for (seq_name,) in rows:
        table = seq_name[:-7]  # remove _id_seq
        try:
            max_id_row = _fetch_one(conn, f"SELECT COALESCE(MAX(id),0) AS max_id FROM {table}")
        except Exception:
            continue
        try:
            seq_row = _fetch_one(conn, f"SELECT last_value, is_called FROM {seq_name}")
        except Exception:
            continue
        max_id = max_id_row.max_id  # type: ignore
        next_alloc = seq_row.last_value if not seq_row.is_called else seq_row.last_value + 1  # type: ignore
        drift = next_alloc - (max_id + 1)
        results.append((seq_name, max_id, next_alloc, drift))
    return results


def fix_all_sequences(conn, dry_run: bool) -> List[Tuple[str, int]]:
    """모든 *_id_seq 를 max(id)+1 로 setval (false). dry-run 시 미적용.
    반환: [(seq_name, target)]
    """
    out: List[Tuple[str, int]] = []
    seqs = scan_all_sequences(conn)
    for seq_name, max_id, _, _ in seqs:
        target = max_id + 1
        if not dry_run:
            try:
                conn.execute(text("SELECT setval(:seq, :target, false)"), {"seq": seq_name, "target": target})
            except Exception:
                continue
        out.append((seq_name, target))
    return out


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--purge-nonseed", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", help="confirmation token for destructive ops")
    ap.add_argument("--scan-all", action="store_true", help="scan all *_id_seq sequences")
    ap.add_argument("--fix-all", action="store_true", help="fix all *_id_seq sequences (setval max+1)")
    args = ap.parse_args(argv)

    if not (args.check or args.fix or args.purge_nonseed or args.scan_all or args.fix_all):
        ap.print_help()
        return 1

    engine = get_engine()
    with engine.begin() as conn:
        if args.check:
            max_id, next_alloc = check_sequence(conn)
            print(f"[CHECK] users.max_id={max_id} seq_next={next_alloc} drift={(next_alloc - (max_id+1))}")
        if args.fix:
            target = fix_sequence(conn)
            print(f"[FIX] set sequence to {target}")
        if args.scan_all:
            scan = scan_all_sequences(conn)
            for seq_name, max_id, next_alloc, drift in scan:
                print(f"[SCAN] seq={seq_name} max_id={max_id} next={next_alloc} drift={drift}")
        if args.fix_all:
            if not args.dry_run and args.confirm != "YES_SEQ_FIX":
                print("Refusing to fix-all without --confirm YES_SEQ_FIX or --dry-run")
                return 3
            fixed = fix_all_sequences(conn, args.dry_run)
            for seq_name, target in fixed:
                action = "WOULD_SET" if args.dry_run else "SET"
                print(f"[FIX-ALL] {action} {seq_name} -> {target}")
        if args.purge_nonseed:
            if not args.dry_run and args.confirm != "YES_PURGE":
                print("Refusing to purge without --confirm YES_PURGE or --dry-run")
                return 2
            n = purge_nonseed(conn, args.dry_run)
            action = "WOULD_DELETE" if args.dry_run else "DELETED"
            print(f"[PURGE] {action} {n} non-seed users")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
