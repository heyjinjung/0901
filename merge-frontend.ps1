#!/usr/bin/env pwsh
# Casino-Club F2P Frontend Code Integration Script
# Created: 2025-08-04

# Generate timestamp
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

# Set paths
$sourceDir = "c:\Users\bdbd\0000\archive\frontend-backup-20250803-114502"
$targetDir = "c:\Users\bdbd\0000\cc-webapp\frontend"
$backupDir = "c:\Users\bdbd\0000\backups\frontend-$timestamp"

# Set log file
$logFile = "c:\Users\bdbd\0000\frontend-merge-$timestamp.log"

function Write-Log {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        [string]$LogLevel = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$LogLevel] $Message"
    Write-Host $logEntry
    Add-Content -Path $logFile -Value $logEntry
}

# Start
Write-Log "Starting frontend code integration" "START"

# 1. Create backup directory
if (Test-Path $backupDir) {
    Write-Log "Backup directory already exists: $backupDir" "INFO"
}
else {
    Write-Log "Creating backup directory: $backupDir" "INFO"
    New-Item -ItemType Directory -Path $backupDir -Force
}

# 2. Preserve Docker config files
$dockerFiles = @(
    "Dockerfile",
    "Dockerfile.dev",
    ".dockerignore"
)

foreach ($file in $dockerFiles) {
    if (Test-Path "$targetDir\$file") {
        Copy-Item -Path "$targetDir\$file" -Destination "$backupDir\$file"
        Write-Log "Docker config file backed up: $file" "INFO"
    }
}

# 3. Preserve environment config files
$configFiles = @(
    "next.config.js",
    "postcss.config.js",
    "tailwind.config.mjs",
    ".env",
    ".env.local",
    ".env.development",
    ".env.production"
)

foreach ($file in $configFiles) {
    if (Test-Path "$targetDir\$file") {
        Copy-Item -Path "$targetDir\$file" -Destination "$backupDir\$file"
        Write-Log "Environment config file backed up: $file" "INFO"
    }
}

# 4. Copy code (excluding Docker-related files)
$dirsToSync = @(
    "app",
    "components",
    "contexts",
    "hooks",
    "public",
    "styles",
    "types",
    "utils"
)

foreach ($dir in $dirsToSync) {
    if (Test-Path "$sourceDir\$dir") {
        # Backup and remove existing content if target directory already exists
        if (Test-Path "$targetDir\$dir") {
            Write-Log "Backing up existing contents of $dir directory..." "INFO"
            Copy-Item -Path "$targetDir\$dir" -Destination "$backupDir\" -Recurse
            Remove-Item -Path "$targetDir\$dir" -Recurse -Force
        }
        
        # Copy from source to target
        Write-Log "Copying $dir directory..." "INFO"
        Copy-Item -Path "$sourceDir\$dir" -Destination "$targetDir\" -Recurse
    }
}

# 5. Integrate package.json (merge dependencies)
Write-Log "Integrating package.json..." "INFO"
if ((Test-Path "$sourceDir\package.json") -and (Test-Path "$targetDir\package.json")) {
    Copy-Item -Path "$targetDir\package.json" -Destination "$backupDir\package.json"
    Copy-Item -Path "$sourceDir\package.json" -Destination "$targetDir\package.json"
    Write-Log "package.json updated - manual review needed for environment compatibility" "WARN"
}

# 6. Restore Docker config files
foreach ($file in $dockerFiles) {
    if (Test-Path "$backupDir\$file") {
        Copy-Item -Path "$backupDir\$file" -Destination "$targetDir\$file" -Force
        Write-Log "Docker config file restored: $file" "INFO"
    }
}

Write-Log "Code copy complete" "INFO"
Write-Log "Important: Build and test with docker-compose needed after integration" "WARN"
Write-Log "Integration process complete. Check log at $logFile" "DONE"
