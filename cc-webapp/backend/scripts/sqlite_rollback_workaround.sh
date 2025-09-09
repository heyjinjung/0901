#!/bin/bash
# SQLite 롤백 불가 제약 우회 스크립트 (테이블 recreate/백업)
# 사용법: bash scripts/sqlite_rollback_workaround.sh [DB_PATH]
set -e
DB_PATH=${1:-"../../dev.db"}
BACKUP_PATH="${DB_PATH}.bak_$(date +%Y%m%d_%H%M%S)"
echo "== [SQLite] DB 백업: $DB_PATH → $BACKUP_PATH =="
cp "$DB_PATH" "$BACKUP_PATH"
echo "== [SQLite] Alembic upgrade head =="
alembic upgrade head
echo "== [SQLite] Alembic downgrade -1 (실패 시 테이블 recreate 필요) =="
if ! alembic downgrade -1; then
  echo "== [SQLite] 롤백 실패: 테이블 recreate/restore 필요 =="
  echo "== [SQLite] 백업본 복구: $BACKUP_PATH → $DB_PATH =="
  cp "$BACKUP_PATH" "$DB_PATH"
  echo "== [SQLite] 복구 완료 =="
else
  echo "== [SQLite] 롤백 성공 =="
fi
