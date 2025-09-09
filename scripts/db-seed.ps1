param(
  [string]$DbName = "cc_webapp",
  [string]$User = "cc_user",
  [SecureString]$Password = $(Read-Host -AsSecureString -Prompt "DB Password"),
  [string]$SqlFile = "${PSScriptRoot}\\..\\database\\seed.sql"
)

$ErrorActionPreference = "Stop"
if (!(Test-Path $SqlFile)) { throw "SQL file not found: $SqlFile" }
Write-Host "Seeding database from $SqlFile ..."
# Convert SecureString to plain text only for the docker exec scope
$plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password))
try {
  $env:PGPASSWORD = $plain
  # Copy the file into container to preserve UTF-8 encoding reliably
  docker cp $SqlFile cc_postgres:/tmp/seed.sql
  docker exec cc_postgres psql -U $User -d $DbName -v ON_ERROR_STOP=1 -f /tmp/seed.sql
  Write-Host "Seed completed."
}
finally {
  Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
  if ($plain) { [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password)) | Out-Null }
}
