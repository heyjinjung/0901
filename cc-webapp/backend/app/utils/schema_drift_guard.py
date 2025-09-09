"""스키마 드리프트 감지 유틸리티

목적: ORM(Base.metadata)과 실제 PostgreSQL 스키마 간 불일치를 조기에 탐지하여
배포/기동 전에 마이그레이션 누락을 차단한다.

정책(현재 버전):
  1) ORM 테이블이 DB에 없으면 critical
  2) core table(users,user_actions,user_rewards,shop_transactions) 컬럼이 DB에 없으면 critical
  3) DB에만 존재하는 테이블/컬럼은 정보/경고 (alembic_version 제외)
  4) 환경변수 ignore 목록으로 임시 예외 허용

환경변수:
  SCHEMA_DRIFT_IGNORE_TABLES=table1,table2
  SCHEMA_DRIFT_IGNORE_COLUMNS=table.col1,table.col2
  SCHEMA_DRIFT_CORE_TABLES=users,user_actions,user_rewards,shop_transactions
"""

from __future__ import annotations

import logging
import os
from typing import Dict, List, Set, Tuple
from sqlalchemy import text
from sqlalchemy.engine import Engine
from app.database import Base, engine

logger = logging.getLogger(__name__)


class SchemaDriftDetector:
    """스키마 드리프트 탐지기"""

    def __init__(self, engine: Engine):
        self.engine = engine

    # ---------------- 수집 -----------------
    def get_orm_columns(self) -> Dict[str, Set[str]]:
        return {tbl_name: {c.name for c in table.columns} for tbl_name, table in Base.metadata.tables.items()}

    def get_db_columns(self) -> Dict[str, Set[str]]:
        db_columns: Dict[str, Set[str]] = {}
        with self.engine.connect() as conn:
            dialect_name = conn.dialect.name
            if dialect_name == "sqlite":
                # SQLite: list tables
                tables = [r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))]
                for tbl in tables:
                    # skip internal sqlite tables
                    if tbl.startswith("sqlite_"):
                        continue
                    cols = conn.execute(text(f"PRAGMA table_info('{tbl}')"))
                    for row in cols:
                        db_columns.setdefault(tbl, set()).add(row[1])  # row[1] = name
            else:
                result = conn.execute(
                    text(
                        """
                        SELECT table_name, column_name
                        FROM information_schema.columns
                        WHERE table_schema = 'public'
                        ORDER BY table_name, column_name
                        """
                    )
                )
                for table_name, column_name in result:
                    db_columns.setdefault(table_name, set()).add(column_name)
        return db_columns

    # ---------------- 핵심 로직 -----------------
    def detect_drift(self) -> Tuple[Dict[str, List[str]], bool]:
        try:
            orm_columns = self.get_orm_columns()
            db_columns = self.get_db_columns()
            is_sqlite = False
            # 간단한 dialect 판정 (engine.url.drivername 활용)
            try:
                is_sqlite = self.engine.url.get_dialect().name == "sqlite"  # type: ignore[attr-defined]
            except Exception:  # pragma: no cover
                is_sqlite = "sqlite" in str(self.engine.url)

            report = {
                "table_missing_in_db": [],   # ORM 정의 O / DB 테이블 없음
                "table_missing_in_orm": [],  # DB 테이블 O / ORM 정의 없음
                "missing_in_db": [],         # ORM 컬럼 O / DB 컬럼 없음
                "missing_in_orm": [],        # DB 컬럼 O / ORM 컬럼 없음
            }

            ignore_tables = {t.strip() for t in os.getenv("SCHEMA_DRIFT_IGNORE_TABLES", "").split(',') if t.strip()}
            ignore_columns_entries = [c.strip() for c in os.getenv("SCHEMA_DRIFT_IGNORE_COLUMNS", "").split(',') if c.strip()]
            ignore_columns: Dict[str, Set[str]] = {}
            for entry in ignore_columns_entries:
                if '.' in entry:
                    tbl, col = entry.split('.', 1)
                    ignore_columns.setdefault(tbl, set()).add(col)

            core_tables = {t.strip() for t in os.getenv(
                "SCHEMA_DRIFT_CORE_TABLES",
                "users,user_actions,user_rewards,shop_transactions"
            ).split(',') if t.strip()}

            # 테스트(SQLite) 환경에서는 achievements 관련 테이블이 아직 ORM에만 존재하거나 반대일 수 있으므로 기본 ignore에 추가
            if is_sqlite:
                ignore_tables.update({"achievements", "user_achievements"})

            orm_tables = set(orm_columns.keys())
            db_tables = set(db_columns.keys())

            # 테이블 비교
            for tbl in sorted((orm_tables - db_tables) - ignore_tables):
                report["table_missing_in_db"].append(tbl)
            for tbl in sorted((db_tables - orm_tables) - ignore_tables - {"alembic_version"}):
                report["table_missing_in_orm"].append(tbl)

            # 컬럼 비교 (공통 테이블)
            for tbl in sorted((orm_tables & db_tables) - ignore_tables):
                orm_cols = orm_columns[tbl]
                db_cols = db_columns.get(tbl, set())
                ignored = ignore_columns.get(tbl, set())

                for col in sorted((orm_cols - db_cols) - ignored):
                    report["missing_in_db"].append(f"{tbl}.{col}")
                for col in sorted((db_cols - orm_cols) - ignored):
                    if tbl == "alembic_version":
                        continue
                    report["missing_in_orm"].append(f"{tbl}.{col}")

            # critical 판정
            has_critical = False
            if not is_sqlite:
                # 실제 배포 DB (postgres 등) => 엄격
                if report["table_missing_in_db"]:
                    has_critical = True
                else:
                    for entry in report["missing_in_db"]:
                        tbl, _ = entry.split('.', 1)
                        if tbl in core_tables:
                            has_critical = True
                            break
            else:
                # SQLite 테스트에서는 critical 완화 (추가 정책 필요시 확장)
                has_critical = False

            return report, has_critical
        except Exception as e:  # 실패시 fail-fast: critical 로 반환
            logger.exception("Schema drift detection failed")
            return {"error": [str(e)]}, True

    # ---------------- 로깅 -----------------
    def log_drift_report(self, report: Dict[str, List[str]], has_critical: bool):
        if "error" in report:
            logger.error("스키마 드리프트 검사 오류: %s", report["error"])
            return
        if not any(report.values()):
            logger.info("✅ Schema drift 없음 (ORM ↔ DB 동기화)")
            return
        header = "🛑 CRITICAL SCHEMA DRIFT" if has_critical else "⚠️ Schema drift (warning)"
        logger.warning(header)
        for k, items in report.items():
            if not items:
                continue
            logger.warning("[%s] (%d)", k, len(items))
            for item in items:
                if has_critical and k in ("missing_in_db", "table_missing_in_db"):
                    logger.error("  - %s", item)
                else:
                    logger.warning("  - %s", item)


def check_schema_drift(return_report: bool = False):
    """외부 호출 편의 함수.

    return_report=True 이면 (has_critical, report) 반환.
    """
    try:
        detector = SchemaDriftDetector(engine)
        report, critical = detector.detect_drift()
        detector.log_drift_report(report, critical)
        if critical:
            logger.error("🛑 Application blocked - run 'alembic upgrade head'")
        return (critical, report) if return_report else critical
    except Exception as e:
        logger.exception("Schema drift check failed (wrapper)")
        err_report = {"error": [str(e)]}
        return (True, err_report) if return_report else True
