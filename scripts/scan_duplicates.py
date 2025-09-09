#!/usr/bin/env python
"""중복 스캔 스크립트

Usage:
  docker compose exec backend python scripts/scan_duplicates.py

기능:
  - event_participations (user_id,event_id) 중복 탐지
  - user_missions (user_id,mission_id) 중복 탐지
  - 결과 JSON 출력 및 파일 저장(scripts/scan_duplicates_report.json)
  - 향후 UNIQUE 제약 적용 전 사전 검증에 사용
"""
import json
import os
import sys
from datetime import datetime

from sqlalchemy import text

# FastAPI 앱 세션 재사용을 위한 간단한 bootstrap
# (app.core.db 혹은 세션 팩토리 위치 프로젝트 구조에 맞춰 조정 필요)
try:
    from app.db.session import SessionLocal  # 표준 세션 팩토리 추정
except (ImportError, ModuleNotFoundError) as e:  # pragma: no cover
    print("[scan_duplicates] 세션 임포트 실패", e, file=sys.stderr)
    sys.exit(1)


def scan(sql: str):
    with SessionLocal() as db:
        return db.execute(text(sql)).mappings().all()


def main():
    event_sql = (
        "SELECT user_id, event_id, COUNT(*) AS dup_count, array_agg(id ORDER BY id) AS ids "
        "FROM event_participations GROUP BY 1,2 HAVING COUNT(*)>1 ORDER BY dup_count DESC"
    )
    mission_sql = (
        "SELECT user_id, mission_id, COUNT(*) AS dup_count, array_agg(id ORDER BY id) AS ids "
        "FROM user_missions GROUP BY 1,2 HAVING COUNT(*)>1 ORDER BY dup_count DESC"
    )

    event_dups = scan(event_sql)
    mission_dups = scan(mission_sql)

    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "event_participations": [dict(r) for r in event_dups],
        "user_missions": [dict(r) for r in mission_dups],
        "summary": {
            "event_participations_dup_pairs": len(event_dups),
            "user_missions_dup_pairs": len(mission_dups),
        },
    }

    path = os.path.join(os.path.dirname(__file__), "scan_duplicates_report.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("[scan_duplicates] 완료", json.dumps(report["summary"], ensure_ascii=False))
    if report["summary"]["event_participations_dup_pairs"] == 0 and report["summary"]["user_missions_dup_pairs"] == 0:
        print("[scan_duplicates] ✅ 중복 없음 - UNIQUE 제약 적용 안전")
    else:
        print("[scan_duplicates] ⚠️ 중복 존재 - 정리 후 마이그레이션 진행 필요")


if __name__ == "__main__":  # pragma: no cover
    main()
