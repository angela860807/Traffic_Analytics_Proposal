param(
  [string]$PostgresContainer = "traffic-postgres",
  [string]$Database = "traffic",
  [string]$User = "postgres",
  [string]$DataSource = "REAL"
)

$ErrorActionPreference = "Stop"

if ($DataSource -notmatch '^[A-Z_]+$') {
  throw "Invalid DataSource: $DataSource"
}

$resetSql = @"
BEGIN;

CREATE TEMP TABLE _demo_events AS
SELECT id
FROM anomaly_events
WHERE data_source = '$DataSource';

CREATE TEMP TABLE _demo_tickets AS
SELECT id
FROM maintenance_tickets
WHERE anomaly_event_id IN (SELECT id FROM _demo_events);

DELETE FROM maintenance_ticket_histories
WHERE maintenance_ticket_id IN (SELECT id FROM _demo_tickets);

DELETE FROM maintenance_tickets
WHERE id IN (SELECT id FROM _demo_tickets);

DELETE FROM anomaly_event_evidence
WHERE anomaly_event_id IN (SELECT id FROM _demo_events);

DELETE FROM anomaly_events
WHERE id IN (SELECT id FROM _demo_events);

DELETE FROM model_prediction_logs
WHERE data_source = '$DataSource';

DELETE FROM camera_health_samples
WHERE data_source = '$DataSource';

INSERT INTO camera_health_samples (
  camera_id,
  sampled_at,
  sample_window_seconds,
  fps_avg,
  frame_drop_rate,
  latency_p95_ms,
  blur_score_avg,
  brightness_score_avg,
  ocr_fail_rate,
  cpu_usage_pct,
  memory_usage_pct,
  disk_usage_pct,
  network_rtt_ms,
  detection_count,
  ocr_attempt_count,
  ocr_failure_count,
  quality_status,
  is_late_sample,
  is_imputed,
  processor_code,
  data_source,
  idempotency_key
)
SELECT
  c.camera_id,
  CURRENT_TIMESTAMP,
  60,
  25.00,
  0.010000,
  120,
  0.120000,
  0.650000,
  0.020000,
  35.00,
  42.00,
  48.00,
  30,
  24,
  20,
  0,
  'COMPLETE',
  FALSE,
  FALSE,
  'predictive-demo-reset',
  '$DataSource',
  'demo-reset-normal-' || c.camera_id
FROM cameras c;

COMMIT;
"@

$resetSql | docker exec -i $PostgresContainer psql -U $User -d $Database

docker exec $PostgresContainer psql -U $User -d $Database -c "select 'camera_health_samples' as table_name, count(*) from camera_health_samples where data_source = '$DataSource' union all select 'anomaly_events', count(*) from anomaly_events where data_source = '$DataSource' union all select 'maintenance_tickets', count(*) from maintenance_tickets mt join anomaly_events ae on ae.id = mt.anomaly_event_id where ae.data_source = '$DataSource' union all select 'model_prediction_logs', count(*) from model_prediction_logs where data_source = '$DataSource';"
