param(
  [Parameter(Mandatory=$true)][string]$DumpFile,
  [string]$DbName = "cc_webapp",
  [string]$User = "cc_user",
  [string]$Password = "cc_password"
)

$ErrorActionPreference = "Stop"
if (!(Test-Path $DumpFile)) { throw "Dump file not found: $DumpFile" }
Write-Host "Restoring '$DumpFile' into database '$DbName'..."
$env:PGPASSWORD = $Password
Get-Content -Path $DumpFile -Encoding Byte | docker exec -i cc_postgres pg_restore -U $User -d $DbName --clean --if-exists
Write-Host "Restore completed."
