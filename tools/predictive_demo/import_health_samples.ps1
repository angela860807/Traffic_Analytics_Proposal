param(
  [string]$CsvPath = "test-media/smoke-runs/predictive-demo/camera-health-samples.csv",
  [string]$BaseUrl = "http://localhost:8080",
  [string]$InternalApiKey = "traffic-ai-internal-key-2026",
  [string]$ProcessorCode = "predictive-demo-video",
  [string]$RunId = (Get-Date -Format "yyyyMMddHHmmss"),
  [switch]$PreserveCsvTimestamps,
  [int]$SampleWindowSeconds = 300,
  [int]$OcrAttemptCount = 100,
  [int]$DetectionCount = 25
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $CsvPath)) {
  throw "CSV not found: $CsvPath"
}

$headers = @{
  "Content-Type" = "application/json"
  "X-Internal-Api-Key" = $InternalApiKey
}

$rows = Import-Csv -LiteralPath $CsvPath
$rowIndex = 0
foreach ($row in $rows) {
  $ocrFailureCount = [int][Math]::Round([double]$row.ocr_fail_rate * $OcrAttemptCount)
  $sampledAt = $row.sampled_at
  if (-not $PreserveCsvTimestamps) {
    $sampledAt = [DateTimeOffset]::Now.AddMinutes($rowIndex * 5).ToString("yyyy-MM-ddTHH:mm:ss.ffffffzzz")
  }

  $payload = [ordered]@{
    idempotencyKey = "demo-$RunId-$($row.scenario)-$($row.camera_id)-$rowIndex"
    cameraId = [long]$row.camera_id
    processorCode = $ProcessorCode
    sampledAt = $sampledAt
    sampleWindowSeconds = $SampleWindowSeconds
    fpsAvg = [decimal]$row.fps_avg
    frameDropRate = [decimal]$row.frame_drop_rate
    latencyP95Ms = [int]$row.latency_p95_ms
    blurScoreAvg = [decimal]$row.blur_score_avg
    brightnessScoreAvg = [decimal]0.5
    detectionCount = $DetectionCount
    ocrAttemptCount = $OcrAttemptCount
    ocrFailureCount = $ocrFailureCount
    ocrFailRate = [decimal]$row.ocr_fail_rate
    cpuUsagePct = [decimal]$row.cpu_usage_pct
    memoryUsagePct = [decimal]$row.memory_usage_pct
    diskUsagePct = [decimal]50
    networkRttMs = [int]$row.network_rtt_ms
    lastFrameAt = $sampledAt
    dataSource = $row.data_source
    qualityStatus = $row.quality_status
    isImputed = $false
  }

  $body = $payload | ConvertTo-Json -Depth 5
  try {
    $response = Invoke-RestMethod `
      -Method Post `
      -Uri "$BaseUrl/internal/v1/camera-health-samples" `
      -Headers $headers `
      -Body $body

    [pscustomobject]@{
      Scenario = $row.scenario
      CameraId = $row.camera_id
      SampledAt = $sampledAt
      SampleId = $response.sampleId
      Created = $response.created
      Status = "Imported"
    }
  } catch {
    $statusCode = $null
    $errorBody = $null
    if ($_.Exception.Response) {
      $statusCode = [int]$_.Exception.Response.StatusCode
      $stream = $_.Exception.Response.GetResponseStream()
      if ($stream) {
        $reader = New-Object System.IO.StreamReader($stream)
        $errorBody = $reader.ReadToEnd()
        $reader.Dispose()
      }
    }

    if ($statusCode -eq 409) {
      [pscustomobject]@{
        Scenario = $row.scenario
        CameraId = $row.camera_id
        SampledAt = $sampledAt
        SampleId = $null
        Created = $false
        Status = "Skipped duplicate"
        Error = $errorBody
      }
      $rowIndex += 1
      continue
    }

    throw
  }
  $rowIndex += 1
}
