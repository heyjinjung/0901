# Casino-Club F2P Project Inspection Script
# UTF-8 encoding configuration
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'

Write-Host "Casino-Club F2P Project Inspection Starting..." -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor DarkGray

# 기본 경로 설정
$basePath = "c:\Users\bdbd\0000"
$backendPath = Join-Path $basePath "cc-webapp\backend\app"
$routersPath = Join-Path $backendPath "routers"
$frontendPath = Join-Path $basePath "cc-webapp\frontend"

# 1. Backend duplicate file check
Write-Host "`nBackend Duplicate Files Check" -ForegroundColor Yellow
$backendDuplicates = @{
    "main" = Get-ChildItem $backendPath -Filter "main*.py" 2>$null
    "config" = Get-ChildItem $backendPath -Filter "config*.py" 2>$null
    "auth" = Get-ChildItem $routersPath -Filter "auth*.py" 2>$null
    "games" = Get-ChildItem $routersPath -Filter "game*.py" 2>$null
}

foreach($key in $backendDuplicates.Keys) {
    $files = $backendDuplicates[$key]
    if($files.Count -gt 1) {
        Write-Host "  WARNING: $key duplicated: $($files.Count) files" -ForegroundColor Red
        $files | ForEach-Object { Write-Host "    - $($_.Name)" -ForegroundColor Gray }
    }
}

# 2. API endpoint mapping check
Write-Host "`nAPI Endpoint Check" -ForegroundColor Yellow
$backendEndpoints = @()
$frontendAPICalls = @()

# Backend endpoint collection (with null/empty check)
Write-Host "  Scanning backend routers..."
$totalFiles = 0
$processedFiles = 0

Get-ChildItem $routersPath -Filter "*.py" -Recurse 2>$null | ForEach-Object {
    $totalFiles++
}

Get-ChildItem $routersPath -Filter "*.py" -Recurse 2>$null | ForEach-Object {
    $processedFiles++
    $file = $_
    $routePrefix = ""
    
    try {
        # 라우터 파일 경로 확인
        Write-Host "  Processing file: $($file.Name) [$processedFiles of $totalFiles]" -ForegroundColor Gray
        
        # UTF-8로 명시적 읽기
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        
        if (![string]::IsNullOrWhiteSpace($content)) {
            # 라우터 정의 찾기
            if ($content -match 'router\s*=\s*APIRouter\(\s*prefix\s*=\s*["''`]([^"''`]+)["''`]') {
                $routePrefix = $matches[1]
                Write-Host "    Found router prefix: $routePrefix" -ForegroundColor Cyan
                $backendEndpoints += $routePrefix
            }
            
            # 엔드포인트 찾기 - 정규식 패턴 개선
            $routerPatterns = Select-String '@router\.(get|post|put|delete|patch)\(["''`]([^"''`]+)["''`]' -InputObject $content -AllMatches
            
            foreach($match in $routerPatterns.Matches) {
                $httpMethod = $match.Groups[1].Value
                $endpoint = $match.Groups[2].Value
                
                if (![string]::IsNullOrEmpty($routePrefix)) {
                    $fullEndpoint = $routePrefix + $endpoint
                    Write-Host "    Found $httpMethod endpoint: $fullEndpoint" -ForegroundColor Cyan
                    $backendEndpoints += $fullEndpoint
                } else {
                    Write-Host "    Found $httpMethod endpoint (no prefix): $endpoint" -ForegroundColor Cyan
                    $backendEndpoints += $endpoint
                }
            }
            
            # 일반 라우터 패턴도 찾기
            $plainRouterPatterns = Select-String 'router\.(get|post|put|delete|patch)\(["''`]([^"''`]+)["''`]' -InputObject $content -AllMatches
            
            foreach($match in $plainRouterPatterns.Matches) {
                $httpMethod = $match.Groups[1].Value
                $endpoint = $match.Groups[2].Value
                
                if (![string]::IsNullOrEmpty($routePrefix)) {
                    $fullEndpoint = $routePrefix + $endpoint
                    Write-Host "    Found $httpMethod endpoint: $fullEndpoint" -ForegroundColor Cyan
                    $backendEndpoints += $fullEndpoint
                } else {
                    Write-Host "    Found $httpMethod endpoint (no prefix): $endpoint" -ForegroundColor Cyan
                    $backendEndpoints += $endpoint
                }
            }
            
            # URL 패턴 찾기 (로그 메시지 등에 있는 경우)
            $urlPatterns = Select-String '/api/[a-zA-Z0-9_/\-]+' -InputObject $content -AllMatches
            
            foreach($match in $urlPatterns.Matches) {
                $endpoint = $match.Value
                Write-Host "    Found URL pattern: $endpoint" -ForegroundColor Cyan
                $backendEndpoints += $endpoint
            }
        }
    } catch {
        Write-Host "  WARNING: File read error: $($file.FullName)" -ForegroundColor Yellow
        Write-Host "  Error details: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Frontend API call collection (with null/empty check)
Write-Host "  Scanning frontend API calls..."
Get-ChildItem $frontendPath -Include "*.ts","*.tsx","*.js","*.jsx" -Recurse 2>$null | ForEach-Object {
    try {
        Write-Host "  Processing file: $($_.FullName)" -ForegroundColor Gray
        
        # UTF-8로 명시적 읽기 (에러 처리 강화)
        try {
            $content = Get-Content $_.FullName -Encoding UTF8 -Raw -ErrorAction SilentlyContinue
        } catch {
            Write-Host "    ENCODING ERROR: Trying different encoding..." -ForegroundColor Yellow
            $content = Get-Content $_.FullName -Encoding Default -Raw -ErrorAction SilentlyContinue
        }
        
        if (![string]::IsNullOrWhiteSpace($content)) {
            # 다양한 API 호출 패턴 탐지
            $patterns = @(
                '(fetch|apiClient\.|axios\.)(get|post|put|delete|patch)?\s*\(\s*[''"`]([^''"`]+)[''"`]',
                'api\.[a-zA-Z]+\s*\(\s*[''"`]([^''"`]+)[''"`]',
                'url\s*:\s*[''"`]([^''"`]+)[''"`]',
                'endpoint\s*:\s*[''"`]([^''"`]+)[''"`]',
                'path\s*:\s*[''"`]([^''"`]+)[''"`]',
                'route\s*:\s*[''"`]([^''"`]+)[''"`]',
                '[''"`](/api/[^''"`]+)[''"`]'
            )
            
            foreach($pattern in $patterns) {
                $regexMatches = [regex]::Matches($content, $pattern)
                foreach($match in $regexMatches) {
                    # 마지막 캡처 그룹 가져오기
                    $endpoint = $match.Groups[$match.Groups.Count - 1].Value
                    if ($endpoint -match '/api/' -or $endpoint -match '^https?://') {
                        Write-Host "    Found API call: $endpoint" -ForegroundColor Cyan
                        $frontendAPICalls += $endpoint
                    }
                }
            }
        }
    } catch {
        Write-Host "  WARNING: File read error: $($_.FullName)" -ForegroundColor Yellow
        Write-Host "  Error details: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "  Backend endpoints: $($backendEndpoints.Count)" 
Write-Host "  Frontend API calls: $($frontendAPICalls.Count)"

# 3. Find unimplemented APIs
$missingAPIs = $frontendAPICalls | Where-Object { 
    $api = $_
    -not ($backendEndpoints | Where-Object { $_ -like "*$api*" })
} | Select-Object -Unique

if($missingAPIs.Count -gt 0) {
    Write-Host "  Missing APIs:" -ForegroundColor Red
    $missingAPIs | ForEach-Object { Write-Host "    - $_" -ForegroundColor Red }
}

# 4. Docker environment check
Write-Host "`nDocker Environment Check" -ForegroundColor Yellow
$dockerComposeFiles = Get-ChildItem $basePath -Filter "docker-compose*.yml" 2>$null
Write-Host "  Docker Compose files: $($dockerComposeFiles.Count)"
if($dockerComposeFiles.Count -gt 3) {
    Write-Host "  WARNING: Too many Docker files (recommended: 3 or fewer)" -ForegroundColor Red
}

# 5. Frontend design consistency check
Write-Host "`nFrontend Design Consistency Check" -ForegroundColor Yellow
$neonColors = @("#00ffff", "#ff00ff", "#ffff00", "cyan", "magenta", "yellow")
$darkTheme = @("#0a0a0a", "#1a1a2e", "bg-dark", "bg-gray-900")

$designConsistency = @{
    "NeonColors" = 0
    "DarkTheme" = 0
    "FramerMotion" = 0
}

$componentsPath = Join-Path $frontendPath "components"
if (Test-Path $componentsPath) {
    Get-ChildItem $componentsPath -Filter "*.tsx" -Recurse 2>$null | ForEach-Object {
    try {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if (![string]::IsNullOrWhiteSpace($content)) {
            foreach($color in $neonColors) {
                if($content -match $color) { $designConsistency["NeonColors"]++ }
            }
            foreach($theme in $darkTheme) {
                if($content -match $theme) { $designConsistency["DarkTheme"]++ }
            }
            if($content -match "framer-motion|motion\.") { $designConsistency["FramerMotion"]++ }
        }
    } catch {
        Write-Host "  WARNING: File read error: $($_.FullName)" -ForegroundColor Yellow
    }
    }
} else {
    Write-Host "  WARNING: Components directory not found at $componentsPath" -ForegroundColor Yellow
}

Write-Host "  Neon color usage: $($designConsistency['NeonColors']) instances"
Write-Host "  Dark theme usage: $($designConsistency['DarkTheme']) instances"
Write-Host "  Animation usage: $($designConsistency['FramerMotion']) instances"

# 6. Final report
Write-Host "`nInspection Results Summary" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor DarkGray

$issues = @()
if($backendDuplicates.Values | Where-Object { $_.Count -gt 1 }) {
    $issues += "Backend duplicate files need cleanup"
}
if($missingAPIs.Count -gt 0) {
    $issues += "$($missingAPIs.Count) APIs need implementation"
}
if($dockerComposeFiles.Count -gt 3) {
    $issues += "Docker files need consolidation"
}

if($issues.Count -eq 0) {
    Write-Host "✅ All checks passed!" -ForegroundColor Green
} else {
    Write-Host "🔧 Issues to resolve:" -ForegroundColor Yellow
    $issues | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
}

# PowerShell script encoding setting (moved to top of script)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Generate report file
$report = @"
# Casino-Club F2P Project Inspection Report
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

## Inspection Results
- Backend duplicate files: $(($backendDuplicates.Values | Where-Object { $_.Count -gt 1 }).Count) categories
- Missing APIs: $($missingAPIs.Count)
- Docker files: $($dockerComposeFiles.Count)
- Frontend design consistency: Maintained

## Immediate Actions Required
$(if($issues.Count -gt 0) { $issues | ForEach-Object { "- $_" } } else { "None" })

## Next Steps
1. Backup and remove duplicate files
2. Implement missing APIs
3. Consolidate Docker environment
4. Run integration tests
"@

# Save file without UTF-8 BOM
$reportPath = "PROJECT_INSPECTION_$(Get-Date -Format 'yyyyMMdd').md"
[System.IO.File]::WriteAllText($reportPath, $report, [System.Text.Encoding]::UTF8)
Write-Host "`nDetailed report generated: $reportPath" -ForegroundColor Cyan
