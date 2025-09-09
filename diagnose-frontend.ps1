# Frontend Configuration Diagnosis Script
$frontendPath = ".\cc-webapp\frontend"
$issues = @()

Write-Host "`n🔍 Starting Frontend Configuration Diagnosis..." -ForegroundColor Cyan

# 1. package.json 검증
Write-Host "`n=== Checking package.json ===" -ForegroundColor Yellow
if (Test-Path "$frontendPath\package.json") {
    $packageJson = Get-Content "$frontendPath\package.json" -Raw | ConvertFrom-Json
    
    # 필수 스크립트 확인
    $requiredScripts = @("dev", "build", "start")
    foreach ($script in $requiredScripts) {
        if (-not $packageJson.scripts.$script) {
            $issues += "Missing script: $script in package.json"
            Write-Host "❌ Missing script: $script" -ForegroundColor Red
        } else {
            Write-Host "✅ Script '$script' found" -ForegroundColor Green
        }
    }
    
    # Next.js 버전 확인
    if ($packageJson.dependencies.next) {
        Write-Host "✅ Next.js version: $($packageJson.dependencies.next)" -ForegroundColor Green
    } else {
        $issues += "Next.js not found in dependencies"
        Write-Host "❌ Next.js not found in dependencies" -ForegroundColor Red
    }
}

# 2. next.config.js 검증
Write-Host "`n=== Checking next.config.js ===" -ForegroundColor Yellow
if (Test-Path "$frontendPath\next.config.js") {
    $nextConfig = Get-Content "$frontendPath\next.config.js" -Raw
    if ($nextConfig -match "module\.exports" -or $nextConfig -match "export default") {
        Write-Host "✅ next.config.js has valid export" -ForegroundColor Green
    } else {
        $issues += "next.config.js missing proper export"
        Write-Host "❌ Invalid next.config.js format" -ForegroundColor Red
    }
} else {
    $issues += "next.config.js not found"
}

# 3. postcss.config.js 검증
Write-Host "`n=== Checking postcss.config.js ===" -ForegroundColor Yellow
if (Test-Path "$frontendPath\postcss.config.js") {
    $postcssConfig = Get-Content "$frontendPath\postcss.config.js" -Raw
    if ($postcssConfig -match "@tailwindcss/postcss") {
        Write-Host "✅ Using Tailwind CSS v4 PostCSS plugin" -ForegroundColor Green
    } elseif ($postcssConfig -match "tailwindcss") {
        $issues += "Using old tailwindcss plugin instead of @tailwindcss/postcss"
        Write-Host "⚠️  Using old Tailwind plugin" -ForegroundColor Yellow
    }
}

# 4. app 디렉토리 구조 확인
Write-Host "`n=== Checking app directory ===" -ForegroundColor Yellow
if (Test-Path "$frontendPath\app") {
    $appFiles = Get-ChildItem "$frontendPath\app" -Filter "*.tsx" -Recurse
    Write-Host "✅ Found $($appFiles.Count) .tsx files in app directory" -ForegroundColor Green
    
    # 필수 파일 확인
    $requiredFiles = @("layout.tsx", "page.tsx")
    foreach ($file in $requiredFiles) {
        if (Test-Path "$frontendPath\app\$file") {
            Write-Host "✅ $file exists" -ForegroundColor Green
        } else {
            $issues += "Missing required file: app/$file"
            Write-Host "❌ Missing: app/$file" -ForegroundColor Red
        }
    }
}

# 5. 환경 변수 파일 확인
Write-Host "`n=== Checking environment files ===" -ForegroundColor Yellow
$envFiles = @(".env", ".env.local", ".env.development")
$envFound = $false
foreach ($envFile in $envFiles) {
    if (Test-Path "$frontendPath\$envFile") {
        Write-Host "✅ Found $envFile" -ForegroundColor Green
        $envFound = $true
    }
}
if (-not $envFound) {
    Write-Host "⚠️  No environment files found" -ForegroundColor Yellow
}

# 결과 요약
Write-Host "`n=== Diagnosis Summary ===" -ForegroundColor Cyan
if ($issues.Count -eq 0) {
    Write-Host "✅ No critical issues found!" -ForegroundColor Green
} else {
    Write-Host "❌ Found $($issues.Count) issues:" -ForegroundColor Red
    foreach ($issue in $issues) {
        Write-Host "  - $issue" -ForegroundColor Red
    }
}
