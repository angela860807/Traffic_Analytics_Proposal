-- ============================================================
-- data_quality_checks.sql
-- TAS-PM predictive maintenance DB data-quality checks.
-- Each query returns abnormal rows or a small verification result.
-- PostgreSQL 16
-- ============================================================

-- 1. Duplicate camera health samples by camera and sampled_at.
SELECT
    'duplicate_camera_health_samples' AS check_name,
    camera_id,
    sampled_at,
    COUNT(*) AS duplicate_count
FROM camera_health_samples
GROUP BY camera_id, sampled_at
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC, camera_id, sampled_at;

-- 2. Duplicate camera health idempotency keys.
SELECT
    'duplicate_camera_health_idempotency_key' AS check_name,
    idempotency_key,
    COUNT(*) AS duplicate_count
FROM camera_health_samples
GROUP BY idempotency_key
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC, idempotency_key;

-- 3. Sample timestamps that are later than created_at by more than 1 minute.
SELECT
    'future_camera_health_sample' AS check_name,
    id,
    camera_id,
    sampled_at,
    created_at
FROM camera_health_samples
WHERE sampled_at > created_at + INTERVAL '1 minute'
ORDER BY sampled_at DESC;

-- 4. Camera health metric range violations.
SELECT
    'camera_health_range_violation' AS check_name,
    id,
    camera_id,
    sampled_at,
    fps_avg,
    frame_drop_rate,
    blur_score_avg,
    brightness_score_avg,
    ocr_fail_rate,
    cpu_usage_pct,
    memory_usage_pct,
    disk_usage_pct
FROM camera_health_samples
WHERE (fps_avg IS NOT NULL AND fps_avg < 0)
   OR (frame_drop_rate IS NOT NULL AND frame_drop_rate NOT BETWEEN 0 AND 1)
   OR (blur_score_avg IS NOT NULL AND blur_score_avg NOT BETWEEN 0 AND 1)
   OR (brightness_score_avg IS NOT NULL AND brightness_score_avg NOT BETWEEN 0 AND 1)
   OR (ocr_fail_rate IS NOT NULL AND ocr_fail_rate NOT BETWEEN 0 AND 1)
   OR (cpu_usage_pct IS NOT NULL AND cpu_usage_pct NOT BETWEEN 0 AND 100)
   OR (memory_usage_pct IS NOT NULL AND memory_usage_pct NOT BETWEEN 0 AND 100)
   OR (disk_usage_pct IS NOT NULL AND disk_usage_pct NOT BETWEEN 0 AND 100)
ORDER BY id;

-- 5. OCR failure count greater than OCR attempt count.
SELECT
    'camera_health_ocr_count_violation' AS check_name,
    id,
    camera_id,
    sampled_at,
    ocr_attempt_count,
    ocr_failure_count
FROM camera_health_samples
WHERE ocr_attempt_count IS NOT NULL
  AND ocr_failure_count IS NOT NULL
  AND ocr_failure_count > ocr_attempt_count
ORDER BY id;

-- 6. Orphan camera health samples.
SELECT
    'orphan_camera_health_sample' AS check_name,
    s.id,
    s.camera_id,
    s.sampled_at
FROM camera_health_samples s
LEFT JOIN cameras c ON c.camera_id = s.camera_id
WHERE c.camera_id IS NULL
ORDER BY s.id;

-- 7. Duplicate traffic context samples by camera, zone and sampled_at.
SELECT
    'duplicate_traffic_context_samples' AS check_name,
    camera_id,
    zone_id,
    sampled_at,
    COUNT(*) AS duplicate_count
FROM traffic_context_samples
GROUP BY camera_id, zone_id, sampled_at
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC, camera_id, zone_id, sampled_at;

-- 8. Traffic context OCR success/failure count violation.
SELECT
    'traffic_context_ocr_count_violation' AS check_name,
    id,
    camera_id,
    zone_id,
    sampled_at,
    ocr_attempt_count,
    ocr_success_count,
    ocr_failure_count
FROM traffic_context_samples
WHERE ocr_attempt_count IS NOT NULL
  AND ocr_success_count IS NOT NULL
  AND ocr_failure_count IS NOT NULL
  AND ocr_success_count + ocr_failure_count > ocr_attempt_count
ORDER BY id;

-- 9. Baseline source mixing in the same camera/day.
SELECT
    'baseline_source_mixed_by_camera_day' AS check_name,
    camera_id,
    DATE_TRUNC('day', sampled_at) AS stat_date,
    COUNT(DISTINCT data_source) AS source_count,
    STRING_AGG(DISTINCT data_source, ', ' ORDER BY data_source) AS sources
FROM camera_health_samples
WHERE quality_status = 'COMPLETE'
  AND is_imputed = FALSE
GROUP BY camera_id, DATE_TRUNC('day', sampled_at)
HAVING COUNT(DISTINCT data_source) > 1
ORDER BY camera_id, stat_date;

-- 10. Baseline groups with fewer than 30 valid samples in the last 14 days.
SELECT
    'insufficient_baseline_samples' AS check_name,
    camera_id,
    data_source,
    COUNT(*) AS sample_count
FROM camera_health_samples
WHERE quality_status = 'COMPLETE'
  AND is_imputed = FALSE
  AND is_late_sample = FALSE
  AND sampled_at >= NOW() - INTERVAL '14 days'
GROUP BY camera_id, data_source
HAVING COUNT(*) < 30
ORDER BY sample_count ASC, camera_id, data_source;

-- 11. Active duplicate anomaly events by camera and anomaly_type.
SELECT
    'active_duplicate_anomaly_events' AS check_name,
    target_camera_id,
    anomaly_type,
    COUNT(*) AS active_count,
    ARRAY_AGG(id ORDER BY id) AS event_ids
FROM anomaly_events
WHERE status IN ('OPEN', 'ACKNOWLEDGED', 'RECOVERED')
GROUP BY target_camera_id, anomaly_type
HAVING COUNT(*) > 1
ORDER BY active_count DESC, target_camera_id, anomaly_type;

-- 12. Tickets without a matching anomaly event.
SELECT
    'ticket_without_anomaly_event' AS check_name,
    mt.id,
    mt.ticket_number,
    mt.anomaly_event_id
FROM maintenance_tickets mt
LEFT JOIN anomaly_events ae ON ae.id = mt.anomaly_event_id
WHERE ae.id IS NULL
ORDER BY mt.id;

-- 13. Invalid ticket status transitions.
SELECT
    'invalid_ticket_status_transition' AS check_name,
    h.id,
    h.maintenance_ticket_id,
    h.from_status,
    h.to_status,
    h.changed_at
FROM maintenance_ticket_histories h
WHERE (h.from_status IS NULL AND h.to_status <> 'OPEN')
   OR (h.from_status = 'OPEN' AND h.to_status NOT IN ('ASSIGNED', 'CLOSED'))
   OR (h.from_status = 'ASSIGNED' AND h.to_status NOT IN ('IN_PROGRESS', 'CLOSED'))
   OR (h.from_status = 'IN_PROGRESS' AND h.to_status NOT IN ('RESOLVED'))
   OR (h.from_status = 'RESOLVED' AND h.to_status NOT IN ('CLOSED'))
ORDER BY h.changed_at DESC;

-- 14. Model prediction logs with severity while predicted_anomaly is false.
SELECT
    'model_prediction_severity_mismatch' AS check_name,
    id,
    camera_id,
    detector_version_id,
    evaluated_at,
    predicted_anomaly,
    predicted_severity
FROM model_prediction_logs
WHERE predicted_anomaly = FALSE
  AND predicted_severity IS NOT NULL
ORDER BY evaluated_at DESC;

-- 15. Model input window ordering violations.
SELECT
    'model_prediction_window_violation' AS check_name,
    id,
    camera_id,
    detector_version_id,
    evaluated_at,
    input_window_from,
    input_window_to
FROM model_prediction_logs
WHERE input_window_from >= input_window_to
ORDER BY evaluated_at DESC;

-- 16. Warning threshold greater than or equal to critical threshold.
SELECT
    'model_prediction_threshold_order_violation' AS check_name,
    id,
    camera_id,
    detector_version_id,
    evaluated_at,
    warning_threshold,
    critical_threshold
FROM model_prediction_logs
WHERE warning_threshold IS NOT NULL
  AND critical_threshold IS NOT NULL
  AND warning_threshold >= critical_threshold
ORDER BY evaluated_at DESC;

-- 17. Late samples used as event evidence.
SELECT
    'late_sample_used_as_event_evidence' AS check_name,
    chs.id AS sample_id,
    chs.camera_id,
    chs.sampled_at,
    aee.anomaly_event_id
FROM camera_health_samples chs
JOIN anomaly_event_evidence aee
    ON aee.sampled_at = chs.sampled_at
JOIN anomaly_events ae
    ON ae.id = aee.anomaly_event_id
   AND ae.target_camera_id = chs.camera_id
WHERE chs.is_late_sample = TRUE
ORDER BY chs.sampled_at DESC;

-- 18. Expected design check: model_prediction_logs must not directly reference anomaly_events.
SELECT
    'model_prediction_logs_has_no_anomaly_event_fk' AS check_name,
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'model_prediction_logs'
              AND column_name = 'anomaly_event_id'
        )
        THEN 'FAIL'
        ELSE 'OK'
    END AS result;
