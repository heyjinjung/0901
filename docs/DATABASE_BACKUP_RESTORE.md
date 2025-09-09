# Database Backup & Restore Runbook (MVP)

## Goals
- Reliable daily backup (retain 7-14 days)
- Fast restore for local debugging or staging refresh (< 10 min typical size)
- Works with PostgreSQL primary; falls back to SQLite dev file copy

## 1. Backup Strategy
| Aspect | Decision |
|--------|----------|
| Tool | `pg_dump` plain SQL piped to gzip |
| Frequency | Daily cron (recommend 02:00 UTC) |
| Retention | Keep last 14 files, prune older |
| Naming | `<db>_YYYYMMDD_HHMMSS.sql.gz` |
| Integrity | Size > 0 & first line starts with `--` comment |
| Storage | Local `backups/` (short term) + off-host copy (S3 or object store) |

### 1.1 Manual Backup (PowerShell)
```
./scripts/backup_database.ps1 -PgHost localhost -PgPort 5432 -PgUser app -PgDatabase casino
```

### 1.2 Size / Quick Integrity Check
```
Get-ChildItem backups/*.gz | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | ForEach-Object { Write-Host "Latest:" $_.Name $_.Length }
```
Optionally decompress head:
```
bash -c "gunzip -c backups/casino_20250101_010101.sql.gz | head -n 5"
```

## 2. Restore Procedure
### 2.1 PostgreSQL
```
./scripts/restore_database.ps1 -BackupFile backups/casino_20250101_010101.sql.gz -PgHost localhost -PgPort 5432 -PgUser app -PgDatabase casino_restored -DropExisting
```
Validate row counts of critical tables (example):
```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM game_sessions;
```

### 2.2 SQLite (Dev Fallback)
If using local SQLite dev file (`test_app.db`):
```
./scripts/backup_database.ps1
# later
./scripts/restore_database.ps1 -BackupFile backups/sqlite_20250101_010101.db
```

## 3. Automation Hooks (Future)
- Add GitHub Action / scheduled job uploading newest file to S3.
- Add WAL archiving for point-in-time once prod traffic justifies it.

## 4. Disaster Recovery Drill (Quarterly)
1. Choose random backup < 7 days old.
2. Restore to isolated DB name.
3. Run smoke queries (counts, a representative user journey).
4. Log duration + anomalies in `docs/DR_DRILL_LOG.md`.

## 5. Security Notes
- Restrict backup storage permissions (read/write only CICD + admins).
- Never commit `.sql` dumps to repo.
- If using cloud storage enable server-side encryption (AES-256 / KMS).

## 6. Standard Error Cases
| Symptom | Cause | Resolution |
|---------|-------|------------|
| `pg_dump: error: connection to database failed` | Bad credentials / host | Verify env vars, try `psql` manually |
| Empty gzip file | Permission or disk full | Check free space & rerun |
| Restore FK errors | Out-of-order statements (rare) | Use plain format (already) or add `--disable-triggers` |
| Encoding issues | Client encoding mismatch | Ensure DB + client `UTF8` |

## 7. Next Improvements
- Add checksum manifest (SHA256) per backup.
- Introduce incremental/WAL shipping.
- Add pruning script to keep newest N + weekly snapshots.

---
MVP implemented: scripts + runbook ready for initial operations.
