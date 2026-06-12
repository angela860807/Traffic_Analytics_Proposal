-- ============================================================
-- predictive_dashboard.sql
-- 예지보전 대시보드 조회 쿼리
-- 기준: 08_DB_작업_TODO.md
-- ============================================================

-- ------------------------------------------------------------
-- 1. 운영 요약 (GET /api/v1/predictive/summary)
--    파라미터: :dataSource VARCHAR
-- ------------------------------------------------------------
SELECT
    COUNT(DISTINCT c.camera_id)                                         AS total_cameras,
    COUNT(DISTINCT c.camera_id) FILTER (WHERE hs.health_status = 'NORMAL')      AS normal_cameras,
    COUNT(DISTINCT c.camera_id) FILTER (WHERE hs.health_status = 'DEGRADED')    AS degraded_cameras,
    COUNT(DISTINCT c.camera_id) FILTER (WHERE hs.health_status = 'CRITICAL')    AS critical_cameras,
    COUNT(DISTINCT c.camera_id) FILTER (WHERE hs.health_status = 'OFFLINE')     AS offline_cameras,
    COUNT(DISTINCT c.camera_id) FILTER (WHERE hs.health_status = 'BASELINE_LEARNING') AS baseline_learning_cameras,

    -- 활성 이상 이벤트
    COUNT(DISTINCT ae.id) FILTER (
        WHERE ae.status IN ('OPEN','ACKNOWLEDGED')
    )                                                                   AS open_anomalies,

    -- 악화 예측 이벤트 (TREND_PROJECTION)
    COUNT(DISTINCT ae.id) FILTER (
        WHERE ae.detection_method = 'TREND_PROJECTION'
          AND ae.status IN ('OPEN','ACKNOWLEDGED')
    )                                                                   AS predicted_risks,

    -- SLA 초과 티켓
    COUNT(DISTINCT mt.id) FILTER (
        WHERE mt.status NOT IN ('RESOLVED','CLOSED')
          AND (mt.due_ack_at < NOW() OR mt.due_start_at < NOW())
    )                                                                   AS overdue_tickets,

    -- MTTA (평균 확인 시간, 분)
    ROUND(
        AVG(
            EXTRACT(EPOCH FROM (mt.acknowledged_at - mt.created_at)) / 60.0
        ) FILTER (WHERE mt.acknowledged_at IS NOT NULL),
    1)                                                                  AS mtta_minutes,

    -- MTTR (평균 복구 시간, 분)
    ROUND(
        AVG(
            EXTRACT(EPOCH FROM (mt.resolved_at - mt.created_at)) / 60.0
        ) FILTER (WHERE mt.resolved_at IS NOT NULL),
    1)                                                                  AS mttr_minutes,

    NOW()                                                               AS generated_at

FROM cameras c
LEFT JOIN (
    -- 카메라별 최신 Health 상태
    SELECT DISTINCT ON (camera_id)
        camera_id,
        -- Health Score 기반 상태 분류 (요구사항 8절)
        CASE
            WHEN fps_avg IS NULL OR fps_avg = 0               THEN 'OFFLINE'
            WHEN fps_avg < 5
              OR latency_p95_ms > 5000
              OR cpu_usage_pct > 95                           THEN 'CRITICAL'
            WHEN fps_avg < 10
              OR latency_p95_ms > 2000
              OR cpu_usage_pct > 85                           THEN 'DEGRADED'
            ELSE 'NORMAL'
        END AS health_status
    FROM camera_health_samples
    WHERE data_source    = :dataSource
      AND is_late_sample = false                              -- 지연 샘플 제외 (요구사항 5-2)
    ORDER BY camera_id, sampled_at DESC
) hs ON hs.camera_id = c.camera_id
LEFT JOIN anomaly_events ae
    ON ae.target_camera_id = c.camera_id
    AND ae.data_source = :dataSource
LEFT JOIN maintenance_tickets mt
    ON mt.anomaly_event_id = ae.id
WHERE c.is_active = true;


-- ------------------------------------------------------------
-- 2. 카메라 운영 상태 목록 (Health Score 오름차순)
--    파라미터: :dataSource VARCHAR
-- ------------------------------------------------------------
SELECT
    c.camera_id,
    c.camera_name,
    c.zone_id,

    -- Health Score (0~100, 요구사항 8절 가중치 기준)
    -- 각 지표를 WARNING/CRITICAL 구간으로 정규화 후 가중 평균
    -- 유효 지표 4개 미만이면 NULL
    CASE
        WHEN (
            CASE WHEN s.fps_avg            IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN s.latency_p95_ms     IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN s.frame_drop_rate    IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN s.ocr_fail_rate      IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN s.blur_score_avg     IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN s.cpu_usage_pct      IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN s.network_rtt_ms     IS NOT NULL THEN 1 ELSE 0 END
        ) < 4 THEN NULL
        ELSE ROUND(
            GREATEST(0, LEAST(100,
                -- FPS (가중치 20): 정상=30fps, WARNING=10, CRITICAL=5
                COALESCE(CASE
                    WHEN s.fps_avg >= 30  THEN 20.0
                    WHEN s.fps_avg >= 10  THEN 20.0 * (s.fps_avg - 10) / 20.0
                    WHEN s.fps_avg >= 5   THEN 10.0 * (s.fps_avg - 5) / 5.0
                    ELSE 0.0
                END, 20.0)
                -- latency p95 (가중치 15): 정상=500ms, WARNING=2000, CRITICAL=5000
                + COALESCE(CASE
                    WHEN s.latency_p95_ms <= 500   THEN 15.0
                    WHEN s.latency_p95_ms <= 2000  THEN 15.0 * (2000 - s.latency_p95_ms) / 1500.0
                    WHEN s.latency_p95_ms <= 5000  THEN 7.5 * (5000 - s.latency_p95_ms) / 3000.0
                    ELSE 0.0
                END, 15.0)
                -- frame drop (가중치 15): 정상=0, WARNING=0.30, CRITICAL=0.60
                + COALESCE(CASE
                    WHEN s.frame_drop_rate <= 0.0   THEN 15.0
                    WHEN s.frame_drop_rate <= 0.30  THEN 15.0 * (0.30 - s.frame_drop_rate) / 0.30
                    WHEN s.frame_drop_rate <= 0.60  THEN 7.5 * (0.60 - s.frame_drop_rate) / 0.30
                    ELSE 0.0
                END, 15.0)
                -- OCR 실패율 (가중치 15): 정상=0, WARNING=0.70, CRITICAL=0.90
                + COALESCE(CASE
                    WHEN s.ocr_fail_rate <= 0.0   THEN 15.0
                    WHEN s.ocr_fail_rate <= 0.70  THEN 15.0 * (0.70 - s.ocr_fail_rate) / 0.70
                    WHEN s.ocr_fail_rate <= 0.90  THEN 7.5 * (0.90 - s.ocr_fail_rate) / 0.20
                    ELSE 0.0
                END, 15.0)
                -- blur score (가중치 15): 정상=0, WARNING=0.75, CRITICAL=0.90
                + COALESCE(CASE
                    WHEN s.blur_score_avg <= 0.0   THEN 15.0
                    WHEN s.blur_score_avg <= 0.75  THEN 15.0 * (0.75 - s.blur_score_avg) / 0.75
                    WHEN s.blur_score_avg <= 0.90  THEN 7.5 * (0.90 - s.blur_score_avg) / 0.15
                    ELSE 0.0
                END, 15.0)
                -- CPU·메모리 (가중치 10): 정상=70%, WARNING=85%, CRITICAL=95%
                + COALESCE(CASE
                    WHEN GREATEST(s.cpu_usage_pct, s.memory_usage_pct) <= 70  THEN 10.0
                    WHEN GREATEST(s.cpu_usage_pct, s.memory_usage_pct) <= 85  THEN 10.0 * (85 - GREATEST(s.cpu_usage_pct, s.memory_usage_pct)) / 15.0
                    WHEN GREATEST(s.cpu_usage_pct, s.memory_usage_pct) <= 95  THEN 5.0 * (95 - GREATEST(s.cpu_usage_pct, s.memory_usage_pct)) / 10.0
                    ELSE 0.0
                END, 10.0)
                -- network RTT (가중치 10): 정상=500ms, WARNING=500, CRITICAL=1000
                + COALESCE(CASE
                    WHEN s.network_rtt_ms <= 500   THEN 10.0
                    WHEN s.network_rtt_ms <= 1000  THEN 10.0 * (1000 - s.network_rtt_ms) / 500.0
                    ELSE 0.0
                END, 10.0)
            ))
        , 1)
    END                                             AS health_score,

    -- health_status (요구사항 8절)
    CASE
        WHEN s.fps_avg IS NULL OR s.fps_avg = 0     THEN 'OFFLINE'
        WHEN s.fps_avg < 5
          OR s.latency_p95_ms > 5000
          OR s.cpu_usage_pct > 95                   THEN 'CRITICAL'
        WHEN s.fps_avg < 10
          OR s.latency_p95_ms > 2000
          OR s.cpu_usage_pct > 85                   THEN 'DEGRADED'
        ELSE 'NORMAL'
    END                                             AS health_status,

    COUNT(ae.id) FILTER (
        WHERE ae.status IN ('OPEN','ACKNOWLEDGED')
    )                                               AS active_anomaly_count,

    COUNT(ae.id) FILTER (
        WHERE ae.detection_method = 'TREND_PROJECTION'
          AND ae.status IN ('OPEN','ACKNOWLEDGED')
    )                                               AS predicted_risk_count,

    s.sampled_at                                    AS latest_sampled_at,
    :dataSource                                     AS data_source

FROM cameras c
LEFT JOIN LATERAL (
    SELECT *
    FROM camera_health_samples
    WHERE camera_id    = c.camera_id
      AND data_source  = :dataSource
      AND is_late_sample = false                    -- 지연 샘플 제외 (요구사항 5-2)
    ORDER BY sampled_at DESC
    LIMIT 1
) s ON true
LEFT JOIN anomaly_events ae
    ON ae.target_camera_id = c.camera_id
    AND ae.data_source     = :dataSource

WHERE c.is_active = true
GROUP BY c.camera_id, c.camera_name, c.zone_id,
         s.fps_avg, s.frame_drop_rate, s.latency_p95_ms,
         s.blur_score_avg, s.ocr_fail_rate,
         s.cpu_usage_pct, s.memory_usage_pct,
         s.network_rtt_ms, s.sampled_at
ORDER BY health_score ASC NULLS LAST;


-- ------------------------------------------------------------
-- 3. 활성 이상 이벤트 목록
--    파라미터: :dataSource VARCHAR, :limit INT, :offset INT
-- ------------------------------------------------------------
SELECT
    ae.id,
    ae.target_type,
    ae.target_camera_id             AS camera_id,
    c.camera_name,
    ae.anomaly_type,
    ae.severity,
    ae.status,
    ae.detection_method,
    ae.anomaly_score,
    ae.projected_threshold_crossing_at,
    ae.first_detected_at,
    ae.last_detected_at,
    ae.data_source,
    mt.id                           AS ticket_id,
    mt.ticket_number,
    mt.priority,
    mt.status                       AS ticket_status
FROM anomaly_events ae
JOIN cameras c ON c.camera_id = ae.target_camera_id
LEFT JOIN maintenance_tickets mt ON mt.anomaly_event_id = ae.id
WHERE ae.status IN ('OPEN','ACKNOWLEDGED')
  AND ae.data_source = :dataSource
ORDER BY
    CASE ae.severity WHEN 'CRITICAL' THEN 0 ELSE 1 END,
    ae.first_detected_at DESC
LIMIT :limit OFFSET :offset;


-- ------------------------------------------------------------
-- 4. 정비 티켓 목록 (SLA 포함)
--    파라미터: :dataSource VARCHAR
-- ------------------------------------------------------------
SELECT
    mt.id,
    mt.ticket_number,
    mt.anomaly_event_id,
    ae.target_camera_id             AS camera_id,
    c.camera_name,
    mt.priority,
    mt.status,
    mt.assignee_id,
    m.name                          AS assignee_name,
    mt.due_ack_at,
    mt.due_start_at,
    mt.acknowledged_at,
    mt.started_at,
    mt.created_at,

    -- SLA 초과 여부
    CASE
        WHEN mt.acknowledged_at IS NULL
         AND mt.due_ack_at < NOW()  THEN TRUE
        ELSE FALSE
    END                             AS ack_overdue,

    CASE
        WHEN mt.started_at IS NULL
         AND mt.due_start_at < NOW() THEN TRUE
        ELSE FALSE
    END                             AS start_overdue,

    -- 남은 시간 (분)
    CASE
        WHEN mt.acknowledged_at IS NULL AND mt.due_ack_at IS NOT NULL
            THEN ROUND(EXTRACT(EPOCH FROM (mt.due_ack_at - NOW())) / 60.0, 0)
        ELSE NULL
    END                             AS ack_remaining_minutes

FROM maintenance_tickets mt
JOIN anomaly_events ae ON ae.id = mt.anomaly_event_id
JOIN cameras c ON c.camera_id = ae.target_camera_id
LEFT JOIN members m ON m.member_id = mt.assignee_id
WHERE mt.status NOT IN ('CLOSED')
ORDER BY
    CASE mt.priority WHEN 'P1' THEN 0 WHEN 'P2' THEN 1 ELSE 2 END,
    mt.created_at DESC;


-- ------------------------------------------------------------
-- 5. MTTA · MTTR 통계
-- ------------------------------------------------------------
SELECT
    ROUND(AVG(
        EXTRACT(EPOCH FROM (mt.acknowledged_at - mt.created_at)) / 60.0
    ) FILTER (WHERE mt.acknowledged_at IS NOT NULL), 1)  AS mtta_minutes,

    ROUND(AVG(
        EXTRACT(EPOCH FROM (mt.resolved_at - mt.created_at)) / 60.0
    ) FILTER (WHERE mt.resolved_at IS NOT NULL), 1)      AS mttr_minutes,

    COUNT(*) FILTER (WHERE mt.resolved_at IS NOT NULL)   AS resolved_count,
    COUNT(*) FILTER (WHERE mt.acknowledged_at IS NOT NULL) AS acknowledged_count

FROM maintenance_tickets mt
WHERE mt.created_at >= NOW() - INTERVAL '30 days';
