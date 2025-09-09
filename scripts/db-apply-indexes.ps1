param(
  [string]$DbName = "cc_webapp",
  [string]$User = "cc_user",
  [string]$Password = "cc_password",
  [string]$SqlFile = "${PSScriptRoot}\db-apply-indexes.sql"
)

$ErrorActionPreference = "Stop"
if (!(Test-Path $SqlFile)) { throw "SQL file not found: $SqlFile" }
Write-Host "Applying indexes using $SqlFile ..."
$env:PGPASSWORD = $Password
Get-Content -Raw -Path $SqlFile | docker exec -i cc_postgres psql -U $User -d $DbName -v ON_ERROR_STOP=1
Write-Host "Indexes applied."
