Param(
  [string]$DbName = "cc_webapp",
  [string]$User = "cc_user",
  [SecureString]$Password = $(Read-Host -AsSecureString -Prompt "DB Password")
)

$ErrorActionPreference = "Stop"
$plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password))
try {
  $env:PGPASSWORD = $plain
  docker cp "${PSScriptRoot}/disable_test_users.sql" cc_postgres:/tmp/disable_test_users.sql
  docker exec -i cc_postgres psql -U $User -d $DbName -v ON_ERROR_STOP=1 -f /tmp/disable_test_users.sql
} finally {
  Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
  if ($plain) { [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR([Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password)) | Out-Null }
}
