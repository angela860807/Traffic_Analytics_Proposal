param(
  [string]$PostgresContainer = "traffic-postgres",
  [string]$Database = "traffic",
  [string]$User = "postgres",
  [string]$DataSource = "REAL",
  [long[]]$CameraIds = @(5, 10, 11, 17),
  [string]$IdempotencyPrefix = "demo-"
)

$ErrorActionPreference = "Stop"

if ($DataSource -notmatch '^[A-Z_]+$') {
  throw "Invalid DataSource: $DataSource"
}

if (-not $CameraIds -or $CameraIds.Count -eq 0) {
  throw "CameraIds must not be empty."
}

if ($IdempotencyPrefix -match "'") {
  throw "IdempotencyPrefix must not contain single quotes."
}

$cameraIdList = ($CameraIds | ForEach-Object { [long]$_ }) -join ", "

$resetSql = @"
BEGIN;

CREATE TEMP TABLE _demo_events AS
SELECT id
FROM anomaly_events
WHERE data_source = '$DataSource'
  AND target_camera_id IN ($cameraIdList);

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

DELETE FROM camera_health_samples
WHERE data_source = '$DataSource'
  AND camera_id IN ($cameraIdList)
  AND idempotency_key LIKE '$IdempotencyPrefix%';

COMMIT;
"@

$resetSql | docker exec -i $PostgresContainer psql -U $User -d $Database

docker exec $PostgresContainer psql -U $User -d $Database -c "select 'camera_health_samples' as table_name, count(*) from camera_health_samples where data_source = '$DataSource' and camera_id in ($cameraIdList) and idempotency_key like '$IdempotencyPrefix%' union all select 'anomaly_events', count(*) from anomaly_events where data_source = '$DataSource' and target_camera_id in ($cameraIdList) union all select 'maintenance_tickets', count(*) from maintenance_tickets mt join anomaly_events ae on ae.id = mt.anomaly_event_id where ae.data_source = '$DataSource' and ae.target_camera_id in ($cameraIdList);"
