-- ============================================================
-- load_test.sql
-- TAS-PM predictive maintenance performance smoke queries.
-- Run after applying 007/008 and optional demo seed.
-- PostgreSQL 16
-- ============================================================

-- Recommended session options for repeatable local measurement.
SET statement_timeout = '30s';
SET lock_timeout = '5s';

-- Refresh planner statistics after demo or bulk seed.
ANALYZE camera_health_samples;
ANALYZE traffic_context_samples;
ANALYZE anomaly_events;
ANALYZE anomaly_event_evidence;
ANALYZE model_prediction_logs;
ANALYZE maintenance_tickets;

-- 1. Latest camera health status by camera.
EXPLAIN (ANALYZE, BUFFERS)
SELECT DISTINCT ON (camera_id)
    camera_id,
    sampled_at,
    fps_avg,
    frame_drop_rate,
    latency_p95_ms,
    blur_score_avg,
    ocr_fail_rate,
    cpu_usage_pct,
    memory_usage_pct,
    network_rtt_ms,
    data_source
FROM camera_health_samples
WHERE data_source = 'SIMULATED'
  AND is_late_sample = FALSE
ORDER BY camera_id, sampled_at DESC;

-- 2. Recent 60-minute camera health window.
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    camera_id,
    sampled_at,
    fps_avg,
    frame_drop_rate,
    latency_p95_ms,
    blur_score_avg,
    ocr_fail_rate,
    cpu_usage_pct,
    memory_usage_pct,
    network_rtt_ms
FROM camera_health_samples
WHERE camera_id = 1
  AND data_source = 'SIMULATED'
  AND sampled_at >= NOW() - INTERVAL '60 minutes'
  AND is_late_sample = FALSE
ORDER BY sampled_at DESC;

-- 3. Baseline 14-day same 30-minute bucket sample count.
EXPLAIN (ANALYZE, BUFFERS)
WITH time_bucket AS (
    SELECT
        EXTRACT(HOUR FROM NOW()) AS eval_hour,
        FLOOR(EXTRACT(MINUTE FROM NOW()) / 30) * 30 AS eval_bucket
)
SELECT
    COUNT(*) AS sample_count,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY fps_avg) AS fps_median
FROM camera_health_samples chs
CROSS JOIN time_bucket tb
WHERE chs.camera_id = 1
  AND chs.sampled_at >= NOW() - INTERVAL '14 days'
  AND chs.sampled_at < NOW()
  AND chs.data_source = 'SIMULATED'
  AND chs.quality_status = 'COMPLETE'
  AND chs.is_imputed = FALSE
  AND chs.is_late_sample = FALSE
  AND EXTRACT(HOUR FROM chs.sampled_at) = tb.eval_hour
  AND FLOOR(EXTRACT(MINUTE FROM chs.sampled_at) / 30) * 30 = tb.eval_bucket;

-- 4. Predictive dashboard active anomaly list.
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    ae.id,
    ae.target_camera_id,
    ae.anomaly_type,
    ae.severity,
    ae.status,
    ae.detection_method,
    ae.first_detected_at,
    mt.ticket_number,
    mt.priority,
    mt.status AS ticket_status
FROM anomaly_events ae
LEFT JOIN maintenance_tickets mt ON mt.anomaly_event_id = ae.id
WHERE ae.status IN ('OPEN', 'ACKNOWLEDGED')
  AND ae.data_source = 'SIMULATED'
ORDER BY
    CASE ae.severity WHEN 'CRITICAL' THEN 0 ELSE 1 END,
    ae.first_detected_at DESC
LIMIT 20 OFFSET 0;

-- 5. Latest LSTM AE shadow prediction by camera.
EXPLAIN (ANALYZE, BUFFERS)
SELECT DISTINCT ON (mpl.camera_id)
    mpl.camera_id,
    mpl.evaluated_at,
    dv.detector_name,
    dv.version,
    mpl.anomaly_score,
    mpl.warning_threshold,
    mpl.critical_threshold,
    mpl.predicted_anomaly,
    mpl.predicted_severity
FROM model_prediction_logs mpl
JOIN detector_versions dv ON dv.id = mpl.detector_version_id
WHERE dv.detection_method = 'LSTM_AUTOENCODER'
ORDER BY mpl.camera_id, mpl.evaluated_at DESC;

-- 6. Index usage quick check after running representative queries.
SELECT
    schemaname,
    relname,
    indexrelname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE relname IN (
    'camera_health_samples',
    'traffic_context_samples',
    'anomaly_events',
    'model_prediction_logs',
    'maintenance_tickets'
)
ORDER BY relname, idx_scan DESC;
