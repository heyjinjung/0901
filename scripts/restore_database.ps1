<#!
Database restore script for PostgreSQL / SQLite.
Usage:
  ./scripts/restore_database.ps1 -BackupFile backups/db_20240101_010101.sql.gz [-PgHost ... -PgUser ... -PgDatabase ...]
#>
param(
  [string]$BackupFile,
  [string]$PgHost = $env:PGHOST,
  [int]$PgPort = [int]($env:PGPORT | ForEach-Object { if ($_ -eq $null -or $_ -eq '') {5432} else {$_} }),
  [string]$PgUser = $env:PGUSER,
  [string]$PgDatabase = $env:PGDATABASE,
  [switch]$DropExisting,
  [string]$SqliteTarget = "cc-webapp/backend/app/test_app.db"
)

$ErrorActionPreference = "Stop"
if (!(Test-Path $BackupFile)) { throw "Backup file not found: $BackupFile" }

function Test-Command($name) { Get-Command $name -ErrorAction SilentlyContinue | ForEach-Object { return $true }; return $false }

if ($BackupFile -match "sqlite_.*\.db$") {
  Write-Host "[*] Restoring SQLite copy -> $SqliteTarget"
  Copy-Item $BackupFile $SqliteTarget -Force
  Write-Host "✅ SQLite restore complete"
  exit 0
}

if ($PgDatabase -and (Test-Command "psql")) {
  Write-Host "[*] Restoring PostgreSQL database: $PgDatabase from $BackupFile"
  if ($DropExisting) {
    Write-Host "[*] Dropping and recreating database"
    psql --host=$PgHost --port=$PgPort --username=$PgUser --dbname=postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$PgDatabase';" | Out-Null
    psql --host=$PgHost --port=$PgPort --username=$PgUser --dbname=postgres -c "DROP DATABASE IF EXISTS \"$PgDatabase\";" | Out-Null
    psql --host=$PgHost --port=$PgPort --username=$PgUser --dbname=postgres -c "CREATE DATABASE \"$PgDatabase\";" | Out-Null
  }
  if ($BackupFile -match "\.gz$") {
    Write-Host "[*] Using gzip decompression"
    & bash -c "gunzip -c '$BackupFile' | psql --host=$PgHost --port=$PgPort --username=$PgUser --dbname=$PgDatabase"
  } else {
    psql --host=$PgHost --port=$PgPort --username=$PgUser --dbname=$PgDatabase -f $BackupFile
  }
  Write-Host "✅ PostgreSQL restore complete"
} else {
  Write-Error "PostgreSQL restore requested but prerequisites missing (psql or env vars)."
}
