-- ============================================================
-- db/retention/purge_old_samples.sql
-- 데이터 보관·정리 SQL
-- 기준: 01_요구사항_정의서 NFR-DATA-001, 02_ERD_설계서 7절
--       08_DB_작업_TODO 10절
--
-- 보관 정책:
--   camera_health_samples       90일
--   traffic_context_samples     90일
--   model_prediction_logs       90일
--   anomaly_events              1년
--   anomaly_event_evidence      1년 (이벤트 참조 행 보호)
--   maintenance_tickets         1년
--   maintenance_ticket_histories 1년
--   detector_versions           영구 (삭제 금지)
--   anomaly_policies            영구 (삭제 금지)
--
-- 실행 방법:
--   Spring Boot scheduler 또는 DBA cron job에서 호출
--   batch 크기 10,000건으로 제한 (DB 부하 분산)
--   대량 삭제 후 VACUUM FULL 금지 → autovacuum 또는 VACUUM (ANALYZE)
-- ============================================================

-- ------------------------------------------------------------
-- 0. 실행 전 행 수 확인 (삭제 전 로그용)
-- ------------------------------------------------------------
SELECT
    'camera_health_samples'    AS table_name,
    COUNT(*)                   AS total_rows,
    COUNT(*) FILTER (WHERE sampled_at < NOW() - INTERVAL '90 days') AS rows_to_delete
FROM camera_health_samples

UNION ALL

SELECT
    'traffic_context_samples',
    COUNT(*),
    COUNT(*) FILTER (WHERE sampled_at < NOW() - INTERVAL '90 days')
FROM traffic_context_samples

UNION ALL

SELECT
    'model_prediction_logs',
    COUNT(*),
    COUNT(*) FILTER (WHERE evaluated_at < NOW() - INTERVAL '90 days')
FROM model_prediction_logs

UNION ALL

SELECT
    'anomaly_events',
    COUNT(*),
    COUNT(*) FILTER (WHERE created_at < NOW() - INTERVAL '1 year')
FROM anomaly_events

UNION ALL

SELECT
    'maintenance_tickets',
    COUNT(*),
    COUNT(*) FILTER (WHERE created_at < NOW() - INTERVAL '1 year')
FROM maintenance_tickets;


-- ------------------------------------------------------------
-- 1. camera_health_samples — 90일 보관
--    batch delete: 10,000건 단위
--    Spring Boot에서 반복 호출하여 전체 삭제
-- ------------------------------------------------------------
DELETE FROM camera_health_samples
WHERE id IN (
    SELECT id
    FROM camera_health_samples
    WHERE sampled_at < NOW() - INTERVAL '90 days'
    LIMIT 10000
);


-- ------------------------------------------------------------
-- 2. traffic_context_samples — 90일 보관
-- ------------------------------------------------------------
DELETE FROM traffic_context_samples
WHERE id IN (
    SELECT id
    FROM traffic_context_samples
    WHERE sampled_at < NOW() - INTERVAL '90 days'
    LIMIT 10000
);


-- ------------------------------------------------------------
-- 3. model_prediction_logs — 90일 보관 (SHADOW 예측 로그)
-- ------------------------------------------------------------
DELETE FROM model_prediction_logs
WHERE id IN (
    SELECT id
    FROM model_prediction_logs
    WHERE evaluated_at < NOW() - INTERVAL '90 days'
    LIMIT 10000
);


-- ------------------------------------------------------------
-- 4. anomaly_event_evidence — 1년 보관
--    단, 아직 활성 이벤트(OPEN/ACKNOWLEDGED/RECOVERED)가
--    참조하는 evidence는 보호
-- ------------------------------------------------------------
DELETE FROM anomaly_event_evidence
WHERE id IN (
    SELECT aee.id
    FROM anomaly_event_evidence aee
    JOIN anomaly_events ae ON aee.anomaly_event_id = ae.id
    WHERE aee.created_at < NOW() - INTERVAL '1 year'
      -- 활성 이벤트가 참조하는 evidence 보호
      AND ae.status NOT IN ('OPEN', 'ACKNOWLEDGED', 'RECOVERED')
    LIMIT 10000
);


-- ------------------------------------------------------------
-- 5. anomaly_events — 1년 보관
--    evidence 삭제 후 실행 (FK 순서)
--    활성 이벤트는 삭제 금지
-- ------------------------------------------------------------
DELETE FROM anomaly_events
WHERE id IN (
    SELECT id
    FROM anomaly_events
    WHERE created_at < NOW() - INTERVAL '1 year'
      AND status NOT IN ('OPEN', 'ACKNOWLEDGED', 'RECOVERED')
    LIMIT 10000
);


-- ------------------------------------------------------------
-- 6. maintenance_ticket_histories — 1년 보관
--    티켓 삭제 전 먼저 실행 (FK 순서)
-- ------------------------------------------------------------
DELETE FROM maintenance_ticket_histories
WHERE id IN (
    SELECT mth.id
    FROM maintenance_ticket_histories mth
    JOIN maintenance_tickets mt ON mth.maintenance_ticket_id = mt.id
    WHERE mth.changed_at < NOW() - INTERVAL '1 year'
      AND mt.status IN ('RESOLVED', 'CLOSED')
    LIMIT 10000
);


-- ------------------------------------------------------------
-- 7. maintenance_tickets — 1년 보관
--    RESOLVED·CLOSED 상태만 삭제
--    OPEN·ASSIGNED·IN_PROGRESS는 보호
-- ------------------------------------------------------------
DELETE FROM maintenance_tickets
WHERE id IN (
    SELECT id
    FROM maintenance_tickets
    WHERE created_at < NOW() - INTERVAL '1 year'
      AND status IN ('RESOLVED', 'CLOSED')
    LIMIT 10000
);


-- ------------------------------------------------------------
-- 8. 영구 보관 대상 — 삭제 금지
--    detector_versions: 버전 추적 및 재현성 보장
--    anomaly_policies:  정책 이력 및 감사 목적
-- ------------------------------------------------------------
-- detector_versions → 삭제 SQL 없음 (영구 보관)
-- anomaly_policies  → 삭제 SQL 없음 (영구 보관)


-- ------------------------------------------------------------
-- 9. 실행 후 행 수 확인 (삭제 후 로그용)
-- ------------------------------------------------------------
SELECT
    'camera_health_samples'    AS table_name,
    COUNT(*)                   AS remaining_rows
FROM camera_health_samples

UNION ALL

SELECT 'traffic_context_samples', COUNT(*)
FROM traffic_context_samples

UNION ALL

SELECT 'model_prediction_logs', COUNT(*)
FROM model_prediction_logs

UNION ALL

SELECT 'anomaly_events', COUNT(*)
FROM anomaly_events

UNION ALL

SELECT 'maintenance_tickets', COUNT(*)
FROM maintenance_tickets;


-- ------------------------------------------------------------
-- 10. 삭제 후 통계 갱신
--     VACUUM FULL은 실행하지 않음
--     autovacuum 확인 후 필요 시 운영 시간에 수동 실행
-- ------------------------------------------------------------
ANALYZE camera_health_samples;
ANALYZE traffic_context_samples;
ANALYZE model_prediction_logs;
ANALYZE anomaly_events;
ANALYZE maintenance_tickets;
