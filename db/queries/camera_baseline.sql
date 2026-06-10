-- ============================================================
-- camera_baseline.sql
-- 카메라별 기준선 조회 (Robust Z-Score 탐지용)
-- 기준: 08_DB_작업_TODO.md
--
-- 조건:
--   - 최근 14일
--   - 평가 시각과 동일한 30분 시간대
--   - data_source = :baselineDataSource (REAL 또는 SIMULATED)
--   - quality_status = 'COMPLETE'
--   - is_imputed = false
--   - 활성·확정 장애 구간 제외
--   - 평가 시각 이후 데이터 제외
--   - metric별 median, MAD, sample_count 반환
-- ============================================================

-- ------------------------------------------------------------
-- 1. 단일 카메라 전체 metric 기준선 조회
--    파라미터:
--      :cameraId          BIGINT
--      :evaluatedAt       TIMESTAMP
--      :baselineDataSource VARCHAR  (REAL | SIMULATED)
-- ------------------------------------------------------------
WITH

-- 평가 시각 기준 동일 30분 시간대 계산
time_bucket AS (
    SELECT
        DATE_TRUNC('hour', :evaluatedAt::TIMESTAMP)
        + INTERVAL '30 min'
          * FLOOR(EXTRACT(MINUTE FROM :evaluatedAt::TIMESTAMP) / 30) AS bucket_start
),

-- 장애·확정 구간 (기준선 제외 대상)
excluded_intervals AS (
    SELECT
        first_detected_at,
        COALESCE(recovered_at, resolved_at, :evaluatedAt::TIMESTAMP) AS end_at
    FROM anomaly_events
    WHERE target_camera_id = :cameraId
      AND status NOT IN ('DISMISSED')
      AND first_detected_at < :evaluatedAt::TIMESTAMP
),

-- 필터링된 원본 샘플
filtered AS (
    SELECT
        s.fps_avg,
        s.frame_drop_rate,
        s.latency_p95_ms,
        s.blur_score_avg,
        s.ocr_fail_rate,
        s.cpu_usage_pct,
        s.memory_usage_pct,
        s.network_rtt_ms
    FROM camera_health_samples s
    CROSS JOIN time_bucket tb
    WHERE s.camera_id      = :cameraId
      AND s.sampled_at     >= :evaluatedAt::TIMESTAMP - INTERVAL '14 days'
      AND s.sampled_at     <  :evaluatedAt::TIMESTAMP          -- 미래 데이터 제외
      AND s.data_source    = :baselineDataSource
      AND s.quality_status = 'COMPLETE'
      AND s.is_imputed     = false
      -- 동일 30분 시간대 필터
      AND (
            DATE_TRUNC('hour', s.sampled_at)
            + INTERVAL '30 min'
              * FLOOR(EXTRACT(MINUTE FROM s.sampled_at) / 30)
          ) = tb.bucket_start
      -- 장애 구간 제외
      AND NOT EXISTS (
            SELECT 1
            FROM excluded_intervals ei
            WHERE s.sampled_at BETWEEN ei.first_detected_at AND ei.end_at
          )
)

-- metric별 median, MAD, sample_count
SELECT
    'fps_avg'           AS metric_name,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fps_avg)                              AS median,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ABS(fps_avg - (
        SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fps_avg) FROM filtered
    )))                                                                                AS mad,
    COUNT(fps_avg)      AS sample_count
FROM filtered
WHERE fps_avg IS NOT NULL

UNION ALL

SELECT
    'frame_drop_rate',
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY frame_drop_rate),
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ABS(frame_drop_rate - (
        SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY frame_drop_rate) FROM filtered
    ))),
    COUNT(frame_drop_rate)
FROM filtered WHERE frame_drop_rate IS NOT NULL

UNION ALL

SELECT
    'latency_p95_ms',
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_p95_ms),
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ABS(latency_p95_ms - (
        SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_p95_ms) FROM filtered
    ))),
    COUNT(latency_p95_ms)
FROM filtered WHERE latency_p95_ms IS NOT NULL

UNION ALL

SELECT
    'blur_score_avg',
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY blur_score_avg),
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ABS(blur_score_avg - (
        SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY blur_score_avg) FROM filtered
    ))),
    COUNT(blur_score_avg)
FROM filtered WHERE blur_score_avg IS NOT NULL

UNION ALL

SELECT
    'ocr_fail_rate',
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ocr_fail_rate),
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ABS(ocr_fail_rate - (
        SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ocr_fail_rate) FROM filtered
    ))),
    COUNT(ocr_fail_rate)
FROM filtered WHERE ocr_fail_rate IS NOT NULL

UNION ALL

SELECT
    'cpu_usage_pct',
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cpu_usage_pct),
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ABS(cpu_usage_pct - (
        SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cpu_usage_pct) FROM filtered
    ))),
    COUNT(cpu_usage_pct)
FROM filtered WHERE cpu_usage_pct IS NOT NULL

UNION ALL

SELECT
    'memory_usage_pct',
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY memory_usage_pct),
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ABS(memory_usage_pct - (
        SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY memory_usage_pct) FROM filtered
    ))),
    COUNT(memory_usage_pct)
FROM filtered WHERE memory_usage_pct IS NOT NULL

UNION ALL

SELECT
    'network_rtt_ms',
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY network_rtt_ms),
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ABS(network_rtt_ms - (
        SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY network_rtt_ms) FROM filtered
    ))),
    COUNT(network_rtt_ms)
FROM filtered WHERE network_rtt_ms IS NOT NULL

ORDER BY metric_name;


-- ------------------------------------------------------------
-- 2. 기준선 표본 부족 카메라 식별
--    표본 30개 미만 → BASELINE_LEARNING 상태
--    파라미터:
--      :evaluatedAt        TIMESTAMP
--      :baselineDataSource VARCHAR
-- ------------------------------------------------------------
SELECT
    c.camera_id,
    c.camera_name,
    COUNT(s.id) AS sample_count,
    CASE
        WHEN COUNT(s.id) < 30 THEN 'BASELINE_LEARNING'
        ELSE 'READY'
    END AS baseline_status
FROM cameras c
LEFT JOIN camera_health_samples s
    ON s.camera_id      = c.camera_id
    AND s.sampled_at    >= :evaluatedAt::TIMESTAMP - INTERVAL '14 days'
    AND s.sampled_at    <  :evaluatedAt::TIMESTAMP
    AND s.data_source   = :baselineDataSource
    AND s.quality_status = 'COMPLETE'
    AND s.is_imputed    = false
WHERE c.is_active = true
GROUP BY c.camera_id, c.camera_name
ORDER BY sample_count ASC;


-- ------------------------------------------------------------
-- 3. 최근 60분 상태 샘플 조회 (Trend·LSTM AE 입력용)
--    파라미터:
--      :cameraId     BIGINT
--      :evaluatedAt  TIMESTAMP
-- ------------------------------------------------------------
SELECT
    sampled_at,
    fps_avg,
    frame_drop_rate,
    latency_p95_ms,
    blur_score_avg,
    ocr_fail_rate,
    cpu_usage_pct,
    memory_usage_pct,
    network_rtt_ms,
    quality_status,
    is_imputed
FROM camera_health_samples
WHERE camera_id      = :cameraId
  AND sampled_at     >= :evaluatedAt::TIMESTAMP - INTERVAL '60 minutes'
  AND sampled_at     <  :evaluatedAt::TIMESTAMP
  AND quality_status IN ('COMPLETE', 'PARTIAL')
ORDER BY sampled_at ASC;
