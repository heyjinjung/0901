param(
    [string]$DashboardsSource = "c:\\Users\\task2\\0114\\0801\\cc-webapp\\monitoring",
    [string]$ProvisionRoot = "c:\\Users\\task2\\0114\\0801\\monitoring_provision"
)

$ErrorActionPreference = 'Stop'

Write-Host "[provision_grafana] 시작: 소스=$DashboardsSource, 타깃=$ProvisionRoot"

# 타깃 디렉터리 구조 생성 (Grafana 컨테이너 마운트 대상으로 사용)
$dashboardsDir = Join-Path $ProvisionRoot "dashboards"
$datasourcesDir = Join-Path $ProvisionRoot "datasources"

New-Item -ItemType Directory -Force -Path $dashboardsDir | Out-Null
New-Item -ItemType Directory -Force -Path $datasourcesDir | Out-Null

# 대시보드 복사 (json만)
if (Test-Path $DashboardsSource) {
    Get-ChildItem -Path $DashboardsSource -Filter "*.json" -File | ForEach-Object {
        Copy-Item $_.FullName -Destination (Join-Path $dashboardsDir $_.Name) -Force
    }
    Write-Host "[provision_grafana] 대시보드 복사 완료: $dashboardsDir"
} else {
    Write-Warning "[provision_grafana] 대시보드 소스 경로가 없습니다: $DashboardsSource"
}

# 기본 데이터소스 템플릿 생성(없으면)
$defaultDatasource = @{
    apiVersion = 1
    datasources = @(
        @{ name = "Prometheus"; type = "prometheus"; access = "proxy"; url = "http://prometheus:9090"; isDefault = $true }
    )
} | ConvertTo-Json -Depth 5

$datasourcePath = Join-Path $datasourcesDir "default.yml"
if (-not (Test-Path $datasourcePath)) {
    $defaultDatasource | Out-File -FilePath $datasourcePath -Encoding utf8
    Write-Host "[provision_grafana] 기본 데이터소스 생성: $datasourcePath"
} else {
    Write-Host "[provision_grafana] 기존 데이터소스 유지: $datasourcePath"
}

Write-Host "[provision_grafana] 완료. docker-compose.monitoring.yml에서 해당 경로를 Grafana provisioning에 마운트하세요."
