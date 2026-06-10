-- ============================================================
-- purge_old_samples.sql
-- 데이터 보관·정리 쿼리
-- 기준: 08_DB_작업_TODO.md
--
-- 보관 정책:
--   camera_health_samples     : 90일
--   traffic_context_samples   : 90일
--   model_prediction_logs     : 90일
--   anomaly_events + evidence : 1년
--   maintenance_tickets + 이력: 1년
-- ============================================================

-- ------------------------------------------------------------
-- 1. camera_health_samples 정리 (90일)
--    batch delete 10,000건씩
-- ------------------------------------------------------------

-- 삭제 전 건수 확인
SELECT
    'camera_health_samples 삭제 대상' AS info,
    COUNT(*)                           AS target_count
FROM camera_health_samples
WHERE sampled_at < NOW() - INTERVAL '90 days';

-- batch delete
DELETE FROM camera_health_samples
WHERE ctid IN (
    SELECT ctid
    FROM camera_health_samples
    WHERE sampled_at < NOW() - INTERVAL '90 days'
    LIMIT 10000
);

-- 삭제 후 확인
SELECT
    'camera_health_samples 잔여' AS info,
    COUNT(*)                      AS remaining_count,
    MIN(sampled_at)               AS oldest_sampled_at
FROM camera_health_samples;

-- ------------------------------------------------------------
-- 2. traffic_context_samples 정리 (90일)
-- ------------------------------------------------------------
SELECT
    'traffic_context_samples 삭제 대상' AS info,
    COUNT(*)                             AS target_count
FROM traffic_context_samples
WHERE sampled_at < NOW() - INTERVAL '90 days';

DELETE FROM traffic_context_samples
WHERE ctid IN (
    SELECT ctid
    FROM traffic_context_samples
    WHERE sampled_at < NOW() - INTERVAL '90 days'
    LIMIT 10000
);

-- ------------------------------------------------------------
-- 3. model_prediction_logs 정리 (90일)
-- ------------------------------------------------------------
SELECT
    'model_prediction_logs 삭제 대상' AS info,
    COUNT(*)                           AS target_count
FROM model_prediction_logs
WHERE evaluated_at < NOW() - INTERVAL '90 days';

DELETE FROM model_prediction_logs
WHERE ctid IN (
    SELECT ctid
    FROM model_prediction_logs
    WHERE evaluated_at < NOW() - INTERVAL '90 days'
    LIMIT 10000
);

-- ------------------------------------------------------------
-- 4. anomaly_event_evidence 정리 (1년)
--    이벤트가 참조하는 evidence는 보호
-- ------------------------------------------------------------
SELECT
    'anomaly_event_evidence 삭제 대상' AS info,
    COUNT(*)                            AS target_count
FROM anomaly_event_evidence e
JOIN anomaly_events ae ON ae.id = e.anomaly_event_id
WHERE ae.first_detected_at < NOW() - INTERVAL '1 year'
  AND ae.status IN ('RESOLVED','DISMISSED');

DELETE FROM anomaly_event_evidence
WHERE ctid IN (
    SELECT e.ctid
    FROM anomaly_event_evidence e
    JOIN anomaly_events ae ON ae.id = e.anomaly_event_id
    WHERE ae.first_detected_at < NOW() - INTERVAL '1 year'
      AND ae.status IN ('RESOLVED','DISMISSED')
    LIMIT 10000
);

-- ------------------------------------------------------------
-- 5. anomaly_events 정리 (1년)
--    evidence 삭제 후 실행
-- ------------------------------------------------------------
SELECT
    'anomaly_events 삭제 대상'  AS info,
    COUNT(*)                     AS target_count
FROM anomaly_events
WHERE first_detected_at < NOW() - INTERVAL '1 year'
  AND status IN ('RESOLVED','DISMISSED');

DELETE FROM anomaly_events
WHERE ctid IN (
    SELECT ctid
    FROM anomaly_events
    WHERE first_detected_at < NOW() - INTERVAL '1 year'
      AND status IN ('RESOLVED','DISMISSED')
    LIMIT 10000
);

-- ------------------------------------------------------------
-- 6. maintenance_ticket_histories 정리 (1년)
-- ------------------------------------------------------------
SELECT
    'maintenance_ticket_histories 삭제 대상' AS info,
    COUNT(*)                                  AS target_count
FROM maintenance_ticket_histories h
JOIN maintenance_tickets mt ON mt.id = h.maintenance_ticket_id
WHERE mt.closed_at < NOW() - INTERVAL '1 year';

DELETE FROM maintenance_ticket_histories
WHERE ctid IN (
    SELECT h.ctid
    FROM maintenance_ticket_histories h
    JOIN maintenance_tickets mt ON mt.id = h.maintenance_ticket_id
    WHERE mt.closed_at < NOW() - INTERVAL '1 year'
    LIMIT 10000
);

-- ------------------------------------------------------------
-- 7. maintenance_tickets 정리 (1년)
--    histories 삭제 후 실행
-- ------------------------------------------------------------
SELECT
    'maintenance_tickets 삭제 대상' AS info,
    COUNT(*)                         AS target_count
FROM maintenance_tickets
WHERE closed_at < NOW() - INTERVAL '1 year'
  AND status = 'CLOSED';

DELETE FROM maintenance_tickets
WHERE ctid IN (
    SELECT ctid
    FROM maintenance_tickets
    WHERE closed_at < NOW() - INTERVAL '1 year'
      AND status = 'CLOSED'
    LIMIT 10000
);

-- ------------------------------------------------------------
-- 8. 정리 후 VACUUM (autovacuum 대신 수동 실행 시)
--    운영 시간 외에 실행 권장
-- ------------------------------------------------------------
-- VACUUM (ANALYZE) camera_health_samples;
-- VACUUM (ANALYZE) traffic_context_samples;
-- VACUUM (ANALYZE) model_prediction_logs;
-- VACUUM (ANALYZE) anomaly_events;
-- VACUUM (ANALYZE) maintenance_tickets;
