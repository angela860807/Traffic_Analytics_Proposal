-- ============================================================
-- db/queries/camera_baseline.sql
-- 카메라별 robust z-score 기준선 조회
-- 기준: 01_요구사항_정의서 5-6절, 08_DB_작업_TODO 6절
--
-- 사용 방법:
--   :cameraId           조회 대상 카메라 ID
--   :evaluatedAt        평가 시각 (이 시각 이후 데이터 제외)
--   :baselineDataSource 운영='REAL', 데모='SIMULATED'
--                       한 기준선 안에서 출처 혼합 금지
-- ============================================================

-- ------------------------------------------------------------
-- 1. 단일 metric 기준선 조회 (Spring Boot native query용)
--    예시: fps_avg 기준선
--    metric 컬럼명만 바꿔서 각 지표에 재사용
-- ------------------------------------------------------------
WITH
-- 1단계: 평가 시각 기준 30분 시간대 계산
--   PostgreSQL session timezone에 의존하지 않도록
--   epoch 기반으로 명시적 계산
time_bucket AS (
    SELECT
        -- 평가 시각의 시(hour)와 30분 단위 버킷 추출
        EXTRACT(HOUR FROM :evaluatedAt)                    AS eval_hour,
        FLOOR(EXTRACT(MINUTE FROM :evaluatedAt) / 30) * 30 AS eval_bucket
),

-- 2단계: 기준선 필터링
--   - 최근 14일
--   - 평가 시각과 동일한 30분 시간대
--   - data_source 파라미터 기준 (REAL 또는 SIMULATED)
--   - quality_status = COMPLETE
--   - is_imputed = false (보간 샘플 제외)
--   - is_late_sample = false (10분 초과 지연 샘플 제외, 요구사항 5-2)
--   - 평가 시각 이후 데이터 제외 (미래 누수 방지)
--   - 활성 이상 이벤트 구간 제외
--   - 장애 주입(FAULT_INJECTED) 구간 제외
filtered AS (
    SELECT
        chs.fps_avg AS metric_value,
        chs.sampled_at
    FROM camera_health_samples chs
    CROSS JOIN time_bucket tb
    WHERE chs.camera_id     = :cameraId
      AND chs.sampled_at   >= NOW() - INTERVAL '14 days'
      AND chs.sampled_at    < :evaluatedAt                 -- 미래 누수 방지
      AND chs.data_source   = :baselineDataSource          -- 출처 혼합 금지
      AND chs.quality_status = 'COMPLETE'
      AND chs.is_imputed    = FALSE
      AND chs.is_late_sample = FALSE                       -- 지연 샘플 제외 (요구사항 5-2)
      AND chs.fps_avg IS NOT NULL
      -- 평가 시각과 동일한 30분 시간대
      AND EXTRACT(HOUR FROM chs.sampled_at)                    = tb.eval_hour
      AND FLOOR(EXTRACT(MINUTE FROM chs.sampled_at) / 30) * 30 = tb.eval_bucket
      -- 활성 이상 이벤트 구간 제외
      AND NOT EXISTS (
          SELECT 1
          FROM anomaly_events ae
          WHERE ae.target_camera_id = chs.camera_id
            AND ae.status IN ('OPEN', 'ACKNOWLEDGED', 'RECOVERED')
            AND ae.first_detected_at <= chs.sampled_at
            AND (ae.recovered_at IS NULL OR ae.recovered_at >= chs.sampled_at)
      )
      -- 운영자가 확정한 장애 구간 제외 (DISMISSED 아닌 RESOLVED)
      AND NOT EXISTS (
          SELECT 1
          FROM anomaly_events ae
          WHERE ae.target_camera_id = chs.camera_id
            AND ae.status = 'RESOLVED'
            AND ae.first_detected_at <= chs.sampled_at
            AND ae.resolved_at >= chs.sampled_at
      )
),

-- 3단계: 중앙값 계산
median_calc AS (
    SELECT
        percentile_cont(0.5)
            WITHIN GROUP (ORDER BY metric_value) AS median
    FROM filtered
)

-- 4단계: median, MAD, sample_count 반환
--   sample_count < 30이면 BASELINE_LEARNING 상태
SELECT
    m.median,
    percentile_cont(0.5)
        WITHIN GROUP (ORDER BY ABS(f.metric_value - m.median)) AS mad,
    COUNT(f.metric_value)                                        AS sample_count,
    -- 표본 30개 미만 여부 (Spring Boot에서 BASELINE_LEARNING 판단용)
    COUNT(f.metric_value) < 30                                   AS is_learning
FROM median_calc m
LEFT JOIN filtered f ON TRUE
GROUP BY m.median;


-- ------------------------------------------------------------
-- 2. 전체 metric 기준선 한 번에 조회 (8개 feature)
--    LSTM AE 및 z-score 탐지에 사용
-- ------------------------------------------------------------
WITH
time_bucket AS (
    SELECT
        EXTRACT(HOUR FROM :evaluatedAt)                    AS eval_hour,
        FLOOR(EXTRACT(MINUTE FROM :evaluatedAt) / 30) * 30 AS eval_bucket
),

baseline_samples AS (
    SELECT
        chs.fps_avg,
        chs.frame_drop_rate,
        chs.latency_p95_ms,
        chs.blur_score_avg,
        chs.ocr_fail_rate,
        chs.cpu_usage_pct,
        chs.memory_usage_pct,
        chs.network_rtt_ms
    FROM camera_health_samples chs
    CROSS JOIN time_bucket tb
    WHERE chs.camera_id      = :cameraId
      AND chs.sampled_at    >= NOW() - INTERVAL '14 days'
      AND chs.sampled_at     < :evaluatedAt
      AND chs.data_source    = :baselineDataSource
      AND chs.quality_status = 'COMPLETE'
      AND chs.is_imputed     = FALSE
      AND chs.is_late_sample = FALSE
      AND EXTRACT(HOUR FROM chs.sampled_at)                    = tb.eval_hour
      AND FLOOR(EXTRACT(MINUTE FROM chs.sampled_at) / 30) * 30 = tb.eval_bucket
      AND NOT EXISTS (
          SELECT 1 FROM anomaly_events ae
          WHERE ae.target_camera_id = chs.camera_id
            AND ae.status IN ('OPEN','ACKNOWLEDGED','RECOVERED')
            AND ae.first_detected_at <= chs.sampled_at
            AND (ae.recovered_at IS NULL OR ae.recovered_at >= chs.sampled_at)
      )
      AND NOT EXISTS (
          SELECT 1 FROM anomaly_events ae
          WHERE ae.target_camera_id = chs.camera_id
            AND ae.status = 'RESOLVED'
            AND ae.first_detected_at <= chs.sampled_at
            AND ae.resolved_at >= chs.sampled_at
      )
)

SELECT
    -- fps_avg
    percentile_cont(0.5) WITHIN GROUP (ORDER BY fps_avg)           AS fps_avg_median,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY ABS(fps_avg -
        (SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY fps_avg) FROM baseline_samples)))
                                                                    AS fps_avg_mad,
    -- frame_drop_rate
    percentile_cont(0.5) WITHIN GROUP (ORDER BY frame_drop_rate)   AS frame_drop_rate_median,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY ABS(frame_drop_rate -
        (SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY frame_drop_rate) FROM baseline_samples)))
                                                                    AS frame_drop_rate_mad,
    -- latency_p95_ms
    percentile_cont(0.5) WITHIN GROUP (ORDER BY latency_p95_ms)    AS latency_p95_ms_median,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY ABS(latency_p95_ms -
        (SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY latency_p95_ms) FROM baseline_samples)))
                                                                    AS latency_p95_ms_mad,
    -- blur_score_avg
    percentile_cont(0.5) WITHIN GROUP (ORDER BY blur_score_avg)    AS blur_score_avg_median,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY ABS(blur_score_avg -
        (SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY blur_score_avg) FROM baseline_samples)))
                                                                    AS blur_score_avg_mad,
    -- ocr_fail_rate
    percentile_cont(0.5) WITHIN GROUP (ORDER BY ocr_fail_rate)     AS ocr_fail_rate_median,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY ABS(ocr_fail_rate -
        (SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY ocr_fail_rate) FROM baseline_samples)))
                                                                    AS ocr_fail_rate_mad,
    -- cpu_usage_pct
    percentile_cont(0.5) WITHIN GROUP (ORDER BY cpu_usage_pct)     AS cpu_usage_pct_median,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY ABS(cpu_usage_pct -
        (SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY cpu_usage_pct) FROM baseline_samples)))
                                                                    AS cpu_usage_pct_mad,
    -- memory_usage_pct
    percentile_cont(0.5) WITHIN GROUP (ORDER BY memory_usage_pct)  AS memory_usage_pct_median,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY ABS(memory_usage_pct -
        (SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY memory_usage_pct) FROM baseline_samples)))
                                                                    AS memory_usage_pct_mad,
    -- network_rtt_ms
    percentile_cont(0.5) WITHIN GROUP (ORDER BY network_rtt_ms)    AS network_rtt_ms_median,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY ABS(network_rtt_ms -
        (SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY network_rtt_ms) FROM baseline_samples)))
                                                                    AS network_rtt_ms_mad,
    -- 공통
    COUNT(*)                                                        AS sample_count,
    COUNT(*) < 30                                                   AS is_learning
FROM baseline_samples;
