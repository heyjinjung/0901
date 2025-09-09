# Compare-Duplicates.ps1
# 중복된 파일들을 분석하여 차이점을 보여주는 스크립트

$outputPath = "file-comparison-report.md"

# 마크다운 보고서 시작
@"
# Casino-Club F2P File Comparison Report
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

This report analyzes the differences between duplicate files in the project to help with consolidation.

"@ | Out-File -FilePath $outputPath -Encoding utf8

# Main 파일 비교
@"
## Main Files Comparison

### Comparing main.py vs main_fixed.py
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8

$diffMain = git diff --no-index -- "cc-webapp\backend\app\main.py" "cc-webapp\backend\app\main_fixed.py"
if ($diffMain) {
    @"
```diff
$diffMain
```

### Key differences:
- [ANALYZE] Differences need manual review
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8
} else {
    "Files are identical" | Out-File -FilePath $outputPath -Append -Encoding utf8
}

@"

### Comparing main.py vs main_simple.py
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8

$diffMainSimple = git diff --no-index -- "cc-webapp\backend\app\main.py" "cc-webapp\backend\app\main_simple.py"
if ($diffMainSimple) {
    @"
```diff
$diffMainSimple
```

### Key differences:
- [ANALYZE] Differences need manual review
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8
} else {
    "Files are identical" | Out-File -FilePath $outputPath -Append -Encoding utf8
}

# Auth 파일 비교
@"

## Auth Files Comparison

### Comparing auth.py vs auth_clean.py
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8

$diffAuth = git diff --no-index -- "cc-webapp\backend\app\routers\auth.py" "cc-webapp\backend\app\routers\auth_clean.py"
if ($diffAuth) {
    @"
```diff
$diffAuth
```

### Key differences:
- [ANALYZE] Differences need manual review
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8
} else {
    "Files are identical" | Out-File -FilePath $outputPath -Append -Encoding utf8
}

@"

### Comparing auth.py vs auth_simple.py
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8

$diffAuthSimple = git diff --no-index -- "cc-webapp\backend\app\routers\auth.py" "cc-webapp\backend\app\routers\auth_simple.py"
if ($diffAuthSimple) {
    @"
```diff
$diffAuthSimple
```

### Key differences:
- [ANALYZE] Differences need manual review
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8
} else {
    "Files are identical" | Out-File -FilePath $outputPath -Append -Encoding utf8
}

@"

### Comparing auth.py vs auth_temp.py
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8

$diffAuthTemp = git diff --no-index -- "cc-webapp\backend\app\routers\auth.py" "cc-webapp\backend\app\routers\auth_temp.py"
if ($diffAuthTemp) {
    @"
```diff
$diffAuthTemp
```

### Key differences:
- [ANALYZE] Differences need manual review
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8
} else {
    "Files are identical" | Out-File -FilePath $outputPath -Append -Encoding utf8
}

# Games 파일 비교
@"

## Games Files Comparison

### Comparing games.py vs games_fixed.py
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8

$diffGames = git diff --no-index -- "cc-webapp\backend\app\routers\games.py" "cc-webapp\backend\app\routers\games_fixed.py"
if ($diffGames) {
    @"
```diff
$diffGames
```

### Key differences:
- [ANALYZE] Differences need manual review
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8
} else {
    "Files are identical" | Out-File -FilePath $outputPath -Append -Encoding utf8
}

@"

### Comparing games.py vs games_direct.py
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8

$diffGamesDirect = git diff --no-index -- "cc-webapp\backend\app\routers\games.py" "cc-webapp\backend\app\routers\games_direct.py"
if ($diffGamesDirect) {
    @"
```diff
$diffGamesDirect
```

### Key differences:
- [ANALYZE] Differences need manual review
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8
} else {
    "Files are identical" | Out-File -FilePath $outputPath -Append -Encoding utf8
}

# Docker 파일 비교
@"

## Docker Files Comparison

### Comparing docker-compose.yml vs docker-compose.simple.yml
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8

$diffDocker = git diff --no-index -- "docker-compose.yml" "docker-compose.simple.yml"
if ($diffDocker) {
    @"
```diff
$diffDocker
```

### Key differences:
- [ANALYZE] Differences need manual review
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8
} else {
    "Files are identical" | Out-File -FilePath $outputPath -Append -Encoding utf8
}

@"

### Comparing docker-compose.yml vs docker-compose.basic.yml
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8

$diffDockerBasic = git diff --no-index -- "docker-compose.yml" "docker-compose.basic.yml"
if ($diffDockerBasic) {
    @"
```diff
$diffDockerBasic
```

### Key differences:
- [ANALYZE] Differences need manual review
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8
} else {
    "Files are identical" | Out-File -FilePath $outputPath -Append -Encoding utf8
}

@"

### Comparing docker-compose.yml vs docker-compose.standalone.yml
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8

$diffDockerStandalone = git diff --no-index -- "docker-compose.yml" "docker-compose.standalone.yml"
if ($diffDockerStandalone) {
    @"
```diff
$diffDockerStandalone
```

### Key differences:
- [ANALYZE] Differences need manual review
"@ | Out-File -FilePath $outputPath -Append -Encoding utf8
} else {
    "Files are identical" | Out-File -FilePath $outputPath -Append -Encoding utf8
}

Write-Host "File comparison report generated at $outputPath"
