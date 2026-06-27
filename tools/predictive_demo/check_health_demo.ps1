param(
  [string]$BaseUrl = "http://localhost:8080",
  [string]$AdminEmail = "admin@email.com",
  [string]$AdminPassword = "1234",
  [string]$InternalApiKey = "traffic-ai-internal-key-2026",
  [string]$CsvPath = "",
  [string]$PostgresContainer = "traffic-postgres",
  [string]$Database = "traffic",
  [string]$User = "postgres",
  [string]$DataSource = "REAL",
  [int]$ExpectedAnomalyEvents = 6,
  [int]$ExpectedMaintenanceTickets = 3,
  [switch]$SkipReset,
  [switch]$SkipImport
)

$ErrorActionPreference = "Stop"

if ($DataSource -notmatch '^[A-Z_]+$') {
  throw "Invalid DataSource: $DataSource"
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $CsvPath) {
  $CsvPath = Join-Path $scriptDir "camera-health-rule-trigger-samples.csv"
}

$resetScript = Join-Path $scriptDir "reset_health_demo.ps1"
$importScript = Join-Path $scriptDir "import_health_samples.ps1"

function Assert-Equal {
  param(
    [string]$Name,
    [long]$Actual,
    [long]$Expected
  )

  if ($Actual -ne $Expected) {
    throw "$Name expected $Expected but was $Actual"
  }

  Write-Host "[OK] $Name = $Actual"
}

function Get-AuthHeaders {
  $login = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/api/auth/login" `
    -ContentType "application/json" `
    -Body (@{
      email = $AdminEmail
      password = $AdminPassword
    } | ConvertTo-Json)

  $token = $login.data.accessToken
  if (-not $token) {
    throw "Login succeeded but accessToken was not found in response.data.accessToken"
  }

  return @{ Authorization = "Bearer $token" }
}

function Get-ApiCounts {
  param([hashtable]$Headers)

  $summary = Invoke-RestMethod `
    -Uri "$BaseUrl/api/v1/predictive/summary?dataSource=$DataSource" `
    -Headers $Headers

  $events = Invoke-RestMethod `
    -Uri "$BaseUrl/api/v1/predictive/anomaly-events?dataSource=$DataSource&page=0&size=100&sort=lastDetectedAt,desc" `
    -Headers $Headers

  return @{
    OpenAnomalies = [long]$summary.openAnomalies
    AnomalyEvents = [long]$events.totalElements
  }
}

function Get-DbCounts {
  $sql = @"
select 'camera_health_samples', count(*) from camera_health_samples where data_source = '$DataSource'
union all
select 'anomaly_events', count(*) from anomaly_events where data_source = '$DataSource'
union all
select 'maintenance_tickets', count(*) from maintenance_tickets mt join anomaly_events ae on ae.id = mt.anomaly_event_id where ae.data_source = '$DataSource'
union all
select 'model_prediction_logs', count(*) from model_prediction_logs where data_source = '$DataSource';
"@

  $lines = docker exec $PostgresContainer psql -U $User -d $Database -t -A -F "," -c $sql
  $counts = @{}
  foreach ($line in $lines) {
    if ($line -match '^([^,]+),([0-9]+)$') {
      $counts[$Matches[1]] = [long]$Matches[2]
    }
  }
  return $counts
}

Write-Host "Predictive maintenance demo check"
Write-Host "BaseUrl=$BaseUrl DataSource=$DataSource CsvPath=$CsvPath"

if (-not $SkipReset) {
  Write-Host ""
  Write-Host "1) Reset REAL demo data"
  & $resetScript `
    -PostgresContainer $PostgresContainer `
    -Database $Database `
    -User $User `
    -DataSource $DataSource

  $headers = Get-AuthHeaders
  $apiCounts = Get-ApiCounts -Headers $headers
  $dbCounts = Get-DbCounts

  Assert-Equal "API openAnomalies after reset" $apiCounts.OpenAnomalies 0
  Assert-Equal "API anomaly-events after reset" $apiCounts.AnomalyEvents 0
  Assert-Equal "DB anomaly_events after reset" $dbCounts["anomaly_events"] 0
  Assert-Equal "DB maintenance_tickets after reset" $dbCounts["maintenance_tickets"] 0
}

if (-not $SkipImport) {
  Write-Host ""
  Write-Host "2) Import health samples"
  & $importScript `
    -CsvPath $CsvPath `
    -BaseUrl $BaseUrl `
    -InternalApiKey $InternalApiKey

  $headers = Get-AuthHeaders
  $apiCounts = Get-ApiCounts -Headers $headers
  $dbCounts = Get-DbCounts

  Assert-Equal "API openAnomalies after import" $apiCounts.OpenAnomalies $ExpectedAnomalyEvents
  Assert-Equal "API anomaly-events after import" $apiCounts.AnomalyEvents $ExpectedAnomalyEvents
  Assert-Equal "DB anomaly_events after import" $dbCounts["anomaly_events"] $ExpectedAnomalyEvents
  Assert-Equal "DB maintenance_tickets after import" $dbCounts["maintenance_tickets"] $ExpectedMaintenanceTickets
}

Write-Host ""
Write-Host "[DONE] Predictive maintenance demo data is ready."
