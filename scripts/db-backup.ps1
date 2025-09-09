param(
  [string]$DbName = "cc_webapp",
  [string]$User = "cc_user",
  [string]$Password = "cc_password",
  [string]$OutDir = "${PSScriptRoot}\..\data\backup"
)

$ErrorActionPreference = "Stop"
if (!(Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$outFile = Join-Path $OutDir "${DbName}_$ts.dump"

Write-Host "Backing up database '$DbName' to '$outFile'..."
$env:PGPASSWORD = $Password
# Use -Encoding Byte to preserve binary format
docker exec cc_postgres pg_dump -Fc -U $User -d $DbName | Set-Content -Path $outFile -Encoding Byte
Write-Host "Backup completed: $outFile"
