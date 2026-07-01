param(
  [string]$CsvPath = "test-media/smoke-runs/predictive-demo/camera-health-samples.csv",
  [string]$BaseUrl = "http://localhost:8080",
  [string]$InternalApiKey = "traffic-ai-internal-key-2026",
  [string]$PostgresContainer = "traffic-postgres",
  [string]$Database = "traffic",
  [string]$User = "postgres",
  [string]$ProcessorCode = "predictive-demo-video",
  [string]$RunId = (Get-Date -Format "yyyyMMddHHmmss"),
  [switch]$PreserveCsvTimestamps,
  [switch]$SkipShadowLog,
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

if (-not $SkipShadowLog) {
  if ($RunId -notmatch '^[0-9A-Za-z_-]+$') {
    throw "Invalid RunId for shadow log seeding: $RunId"
  }

  $shadowSql = @"
WITH detector AS (
  UPDATE detector_versions
     SET operating_mode = 'SHADOW',
         active = FALSE
   WHERE detector_name = 'camera-lstm-autoencoder'
     AND version = '1.0.0'
  RETURNING id
),
fallback_detector AS (
  SELECT id
    FROM detector_versions
   WHERE detector_name = 'camera-lstm-autoencoder'
     AND version = '1.0.0'
   LIMIT 1
),
imported AS (
  SELECT
    camera_id,
    data_source,
    MAX(sampled_at) AS evaluated_at,
    MIN(sampled_at) AS first_sampled_at,
    AVG(fps_avg) AS fps_avg,
    MAX(frame_drop_rate) AS frame_drop_rate,
    MAX(latency_p95_ms) AS latency_p95_ms,
    MAX(blur_score_avg) AS blur_score_avg,
    MAX(ocr_fail_rate) AS ocr_fail_rate,
    MAX(cpu_usage_pct) AS cpu_usage_pct,
    MAX(memory_usage_pct) AS memory_usage_pct,
    MAX(network_rtt_ms) AS network_rtt_ms
  FROM camera_health_samples
  WHERE idempotency_key LIKE 'demo-$RunId-%'
  GROUP BY camera_id, data_source
),
scored AS (
  SELECT
    i.*,
    LEAST(0.980000, GREATEST(
      0.180000,
      (1 - LEAST(COALESCE(i.fps_avg, 30) / 30.0, 1)) * 0.90,
      COALESCE(i.frame_drop_rate, 0),
      COALESCE(i.latency_p95_ms, 0) / 1000.0,
      COALESCE(i.blur_score_avg, 0),
      COALESCE(i.ocr_fail_rate, 0),
      COALESCE(i.cpu_usage_pct, 0) / 100.0,
      COALESCE(i.memory_usage_pct, 0) / 100.0,
      COALESCE(i.network_rtt_ms, 0) / 500.0
    ))::NUMERIC(7,6) AS anomaly_score
  FROM imported i
)
INSERT INTO model_prediction_logs (
  camera_id,
  detector_version_id,
  evaluated_at,
  input_window_from,
  input_window_to,
  anomaly_score,
  warning_threshold,
  critical_threshold,
  predicted_anomaly,
  predicted_severity,
  data_source,
  quality_status,
  feature_schema_version,
  top_features_json
)
SELECT
  s.camera_id,
  COALESCE((SELECT id FROM detector), (SELECT id FROM fallback_detector)),
  s.evaluated_at,
  LEAST(s.first_sampled_at, s.evaluated_at - INTERVAL '60 minutes'),
  s.evaluated_at,
  s.anomaly_score,
  0.410734,
  0.462065,
  s.anomaly_score >= 0.410734,
  CASE
    WHEN s.anomaly_score >= 0.462065 THEN 'CRITICAL'
    WHEN s.anomaly_score >= 0.410734 THEN 'WARNING'
    ELSE NULL
  END,
  s.data_source,
  'COMPLETE',
  'camera-health-sequence-v1',
  jsonb_build_array(
    jsonb_build_object('featureName', 'fps_avg', 'featureValue', ROUND(((1 - LEAST(COALESCE(s.fps_avg, 30) / 30.0, 1)) * 0.90)::NUMERIC, 2)),
    jsonb_build_object('featureName', 'frame_drop_rate', 'featureValue', ROUND(COALESCE(s.frame_drop_rate, 0)::NUMERIC, 2)),
    jsonb_build_object('featureName', 'latency_p95_ms', 'featureValue', ROUND((COALESCE(s.latency_p95_ms, 0) / 1000.0)::NUMERIC, 2)),
    jsonb_build_object('featureName', 'blur_score_avg', 'featureValue', ROUND(COALESCE(s.blur_score_avg, 0)::NUMERIC, 2)),
    jsonb_build_object('featureName', 'cpu_usage_pct', 'featureValue', ROUND((COALESCE(s.cpu_usage_pct, 0) / 100.0)::NUMERIC, 2))
  )
FROM scored s
WHERE COALESCE((SELECT id FROM detector), (SELECT id FROM fallback_detector)) IS NOT NULL
ON CONFLICT (camera_id, detector_version_id, evaluated_at)
DO UPDATE SET
  anomaly_score = EXCLUDED.anomaly_score,
  warning_threshold = EXCLUDED.warning_threshold,
  critical_threshold = EXCLUDED.critical_threshold,
  predicted_anomaly = EXCLUDED.predicted_anomaly,
  predicted_severity = EXCLUDED.predicted_severity,
  quality_status = EXCLUDED.quality_status,
  feature_schema_version = EXCLUDED.feature_schema_version,
  top_features_json = EXCLUDED.top_features_json,
  created_at = CURRENT_TIMESTAMP;
"@

  $insertedSql = @"
SELECT
  camera_id,
  data_source,
  evaluated_at,
  anomaly_score,
  predicted_anomaly,
  predicted_severity
FROM model_prediction_logs
WHERE evaluated_at IN (
  SELECT MAX(sampled_at)
  FROM camera_health_samples
  WHERE idempotency_key LIKE 'demo-$RunId-%'
  GROUP BY camera_id, data_source
)
ORDER BY camera_id;
"@

  $shadowSql | docker exec -i $PostgresContainer psql -U $User -d $Database
  docker exec $PostgresContainer psql -U $User -d $Database -c $insertedSql
}
