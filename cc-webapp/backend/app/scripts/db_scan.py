"""전수 테이블 스캔 유틸리티

사용: python -m app.scripts.db_scan [--limit 1] [--schema public]

출력: JSON (각 테이블별 row count, 선택적 샘플)
"""
from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List
from datetime import datetime, date, time
from decimal import Decimal

from sqlalchemy import inspect, text

from app.database import engine, SessionLocal


def scan(schema: str = "public", sample_limit: int = 1) -> List[Dict[str, Any]]:
    insp = inspect(engine)
    tables = []
    for t in insp.get_table_names(schema=schema):
        tables.append((schema, t))

    sess = SessionLocal()
    out: List[Dict[str, Any]] = []
    for sch, tbl in sorted(tables, key=lambda x: x[1]):
        full = f'"{sch}"."{tbl}"'
        entry: Dict[str, Any] = {"table": f"{sch}.{tbl}"}
        try:
            cnt = sess.execute(text(f"SELECT COUNT(*) FROM {full}")).scalar()  # type: ignore
            entry["count"] = cnt
            if cnt and cnt > 0 and sample_limit > 0:
                sample_rows = sess.execute(
                    text(f"SELECT * FROM {full} LIMIT :lim").bindparams(lim=sample_limit)
                ).mappings().all()
                entry["sample"] = [_serialize_row(dict(r)) for r in sample_rows]
        except Exception as e:  # pylint: disable=broad-except
            entry["error"] = str(e)
        out.append(entry)
    sess.close()
    return out


def _serialize_value(v: Any) -> Any:
    if isinstance(v, (datetime, date, time)):
        return v.isoformat()
    if isinstance(v, Decimal):
        # 소수 자릿수 보존 위해 문자열로 반환 (필요시 float로 변경 가능)
        return str(v)
    return v


def _serialize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {k: _serialize_value(v) for k, v in row.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", default="public")
    ap.add_argument("--limit", type=int, default=1)
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    data = scan(schema=args.schema, sample_limit=args.limit)
    if args.pretty:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":  # pragma: no cover
    main()
