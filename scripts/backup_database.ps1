<#!
Database backup script.
Supports PostgreSQL (preferred) and SQLite fallback.
Usage:
  ./scripts/backup_database.ps1 -OutputDir backups [-PgHost localhost -PgPort 5432 -PgUser user -PgDatabase db]
#>
param(
  [string]$OutputDir = "backups",
  [string]$PgHost = $env:PGHOST,
  [int]$PgPort = [int]($env:PGPORT | ForEach-Object { if ($_ -eq $null -or $_ -eq '') {5432} else {$_} }),
  [string]$PgUser = $env:PGUSER,
  [string]$PgDatabase = $env:PGDATABASE,
  [string]$SqlitePath = "cc-webapp/backend/app/test_app.db",
  [int]$Retain = 14,
  [switch]$NoPrune
)

$ErrorActionPreference = "Stop"
if (!(Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir | Out-Null }
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

function Test-Command($name) { Get-Command $name -ErrorAction SilentlyContinue | ForEach-Object { return $true }; return $false }

if ($PgDatabase -and (Test-Command "pg_dump")) {
  $outfile = Join-Path $OutputDir "${PgDatabase}_${timestamp}.sql.gz"
  Write-Host "[*] PostgreSQL backup -> $outfile"
  $env:PGPASSWORD = $env:PGPASSWORD  # ensure pass-through
  $dumpCmd = "pg_dump --host=$PgHost --port=$PgPort --username=$PgUser --format=plain --no-owner $PgDatabase"
  & bash -c "$dumpCmd | gzip -c > '$outfile'"  # use bash if available for pipe; fallback below
  if (!(Test-Path $outfile)) { Write-Warning "Pipe via bash failed, attempting native PowerShell pipeline"; pg_dump --host=$PgHost --port=$PgPort --username=$PgUser --format=plain --no-owner $PgDatabase | Compress-Archive -DestinationPath $outfile }
  Write-Host "✅ Backup complete (PostgreSQL)"
} elseif (Test-Path $SqlitePath) {
  $outfile = Join-Path $OutputDir "sqlite_${timestamp}.db"
  Write-Host "[*] SQLite file copy -> $outfile"
  Copy-Item $SqlitePath $outfile
  Write-Host "✅ Backup complete (SQLite)"
} else {
  Write-Error "No database target found (provide PostgreSQL env vars or ensure SQLite file exists)"
}

# Compute SHA256 checksum
if (Test-Path $outfile) {
  try {
    $sha = Get-FileHash -Path $outfile -Algorithm SHA256
    $checksumFile = "$outfile.sha256"
    "$($sha.Hash)  $(Split-Path -Leaf $outfile)" | Out-File -FilePath $checksumFile -Encoding ascii -Force
    Write-Host "[*] SHA256: $($sha.Hash.Substring(0,16))... -> $checksumFile"
  } catch { Write-Warning "Checksum generation failed: $_" }
}

# Prune old backups (keep newest $Retain) unless disabled
if (-not $NoPrune) {
  $all = Get-ChildItem -Path $OutputDir -File -Include *.sql.gz,*.db | Sort-Object LastWriteTime -Descending
  if ($all.Count -gt $Retain) {
    $remove = $all | Select-Object -Skip $Retain
    foreach ($r in $remove) {
      try {
        Remove-Item $r.FullName -Force
        $hashSide = "$($r.FullName).sha256"
        if (Test-Path $hashSide) { Remove-Item $hashSide -Force }
        Write-Host "[-] Pruned old backup: $($r.Name)"
      } catch { Write-Warning "Prune failed: $($_.Exception.Message)" }
    }
  }
}
