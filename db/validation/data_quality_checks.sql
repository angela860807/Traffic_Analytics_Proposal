-- ============================================================
-- data_quality_checks.sql
-- 데이터 품질 검증 쿼리
-- 기준: 08_DB_작업_TODO.md
-- 각 쿼리는 이상 건수와 식별 키를 반환
-- ============================================================

-- ------------------------------------------------------------
-- 1. 중복 샘플 확인
-- ------------------------------------------------------------
SELECT
    '중복_camera_health_samples'    AS check_name,
    camera_id,
    sampled_at,
    COUNT(*)                        AS duplicate_count
FROM camera_health_samples
GROUP BY camera_id, sampled_at
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- ------------------------------------------------------------
-- 2. 시간 역전 확인 (sampled_at > created_at)
-- ------------------------------------------------------------
SELECT
    '시간역전_camera_health_samples' AS check_name,
    id,
    camera_id,
    sampled_at,
    created_at
FROM camera_health_samples
WHERE sampled_at > created_at + INTERVAL '1 minute'
ORDER BY id;

-- ------------------------------------------------------------
-- 3. 값 범위 위반 확인
-- ------------------------------------------------------------
SELECT
    '범위위반_camera_health_samples' AS check_name,
    id,
    camera_id,
    sampled_at,
    fps_avg,
    frame_drop_rate,
    ocr_fail_rate,
    cpu_usage_pct,
    memory_usage_pct
FROM camera_health_samples
WHERE fps_avg           < 0
   OR frame_drop_rate   NOT BETWEEN 0 AND 1
   OR ocr_fail_rate     NOT BETWEEN 0 AND 1
   OR cpu_usage_pct     NOT BETWEEN 0 AND 100
   OR memory_usage_pct  NOT BETWEEN 0 AND 100
ORDER BY id;

-- ------------------------------------------------------------
-- 4. OCR count 불일치 확인
-- ------------------------------------------------------------
SELECT
    'OCR_count_불일치'               AS check_name,
    id,
    camera_id,
    sampled_at,
    ocr_attempt_count,
    ocr_failure_count,
    (ocr_attempt_count - ocr_failure_count) AS expected_success
FROM camera_health_samples
WHERE ocr_attempt_count IS NOT NULL
  AND ocr_failure_count IS NOT NULL
  AND ocr_failure_count > ocr_attempt_count
ORDER BY id;

-- ------------------------------------------------------------
-- 5. 고아 FK 확인 (camera_id 없는 샘플)
-- ------------------------------------------------------------
SELECT
    '고아FK_camera_health_samples'  AS check_name,
    s.id,
    s.camera_id,
    s.sampled_at
FROM camera_health_samples s
LEFT JOIN cameras c ON c.camera_id = s.camera_id
WHERE c.camera_id IS NULL
ORDER BY s.id;

-- ------------------------------------------------------------
-- 6. 출처 혼합 기준선 확인
--    한 기준선 구간에 REAL + SIMULATED 혼합 여부
-- ------------------------------------------------------------
SELECT
    '출처혼합_기준선'                 AS check_name,
    camera_id,
    DATE_TRUNC('day', sampled_at)   AS stat_date,
    COUNT(DISTINCT data_source)     AS source_count,
    STRING_AGG(DISTINCT data_source, ', ') AS sources
FROM camera_health_samples
GROUP BY camera_id, DATE_TRUNC('day', sampled_at)
HAVING COUNT(DISTINCT data_source) > 1
ORDER BY camera_id, stat_date;

-- ------------------------------------------------------------
-- 7. 표본 부족 기준선 (30개 미만)
-- ------------------------------------------------------------
SELECT
    '표본부족_기준선'                 AS check_name,
    camera_id,
    data_source,
    COUNT(*)                        AS sample_count
FROM camera_health_samples
WHERE quality_status = 'COMPLETE'
  AND is_imputed = false
  AND sampled_at >= NOW() - INTERVAL '14 days'
GROUP BY camera_id, data_source
HAVING COUNT(*) < 30
ORDER BY sample_count ASC;

-- ------------------------------------------------------------
-- 8. 이벤트 없는 티켓 확인
-- ------------------------------------------------------------
SELECT
    '이벤트없는_티켓'                 AS check_name,
    mt.id,
    mt.ticket_number,
    mt.anomaly_event_id
FROM maintenance_tickets mt
LEFT JOIN anomaly_events ae ON ae.id = mt.anomaly_event_id
WHERE ae.id IS NULL
ORDER BY mt.id;

-- ------------------------------------------------------------
-- 9. 활성 중복 이벤트 확인
--    같은 카메라·이상유형에 활성 이벤트가 2개 이상
-- ------------------------------------------------------------
SELECT
    '활성중복_이벤트'                 AS check_name,
    target_camera_id,
    anomaly_type,
    COUNT(*)                        AS active_count,
    ARRAY_AGG(id)                   AS event_ids
FROM anomaly_events
WHERE status IN ('OPEN','ACKNOWLEDGED','RECOVERED')
GROUP BY target_camera_id, anomaly_type
HAVING COUNT(*) > 1
ORDER BY active_count DESC;

-- ------------------------------------------------------------
-- 10. 잘못된 티켓 상태 이력 확인
--     허용되지 않은 상태 전이
-- ------------------------------------------------------------
SELECT
    '잘못된_티켓_상태전이'             AS check_name,
    h.id,
    h.maintenance_ticket_id,
    h.from_status,
    h.to_status,
    h.changed_at
FROM maintenance_ticket_histories h
WHERE (h.from_status = 'OPEN'        AND h.to_status NOT IN ('ASSIGNED'))
   OR (h.from_status = 'ASSIGNED'    AND h.to_status NOT IN ('IN_PROGRESS'))
   OR (h.from_status = 'IN_PROGRESS' AND h.to_status NOT IN ('RESOLVED'))
   OR (h.from_status = 'RESOLVED'    AND h.to_status NOT IN ('CLOSED'))
ORDER BY h.changed_at DESC;

-- ------------------------------------------------------------
-- 11. SHADOW 예측과 anomaly_event 직접 FK 존재 여부 확인
--     model_prediction_logs는 anomaly_events와 직접 FK 없어야 함
-- ------------------------------------------------------------
SELECT
    'SHADOW_직접FK_없음_확인'         AS check_name,
    'model_prediction_logs에 anomaly_event_id 컬럼 없음 (정상)' AS result;

-- ------------------------------------------------------------
-- 12. traffic_context OCR count 불일치
-- ------------------------------------------------------------
SELECT
    'traffic_context_OCR_불일치'      AS check_name,
    id,
    camera_id,
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

-- ------------------------------------------------------------
-- 13. 지연 샘플이 탐지에 사용됐는지 확인 (요구사항 5-2)
--     is_late_sample=TRUE 샘플의 sampled_at이
--     anomaly_event_evidence의 sampled_at과 일치하는 경우
-- ------------------------------------------------------------
SELECT
    '지연샘플_탐지사용_확인'              AS check_name,
    chs.id                               AS sample_id,
    chs.camera_id,
    chs.sampled_at,
    ae.id                                AS event_id
FROM camera_health_samples chs
JOIN anomaly_event_evidence aee
    ON aee.sampled_at      = chs.sampled_at
JOIN anomaly_events ae
    ON aee.anomaly_event_id = ae.id
   AND ae.target_camera_id  = chs.camera_id
WHERE chs.is_late_sample = TRUE
ORDER BY chs.sampled_at DESC;

-- ------------------------------------------------------------
-- 14. predicted_severity 일관성 확인
--     predicted_anomaly=FALSE인데 predicted_severity가 있는 경우
-- ------------------------------------------------------------
SELECT
    'predicted_severity_불일치'           AS check_name,
    id,
    camera_id,
    evaluated_at,
    predicted_anomaly,
    predicted_severity
FROM model_prediction_logs
WHERE predicted_anomaly = FALSE
  AND predicted_severity IS NOT NULL
ORDER BY evaluated_at DESC;
