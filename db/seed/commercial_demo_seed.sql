-- ============================================================
-- commercial_demo_seed.sql
-- TAS-PM 발표용 대용량 운영 데모 데이터
--
-- 목적:
--   - 공백 DB에서도 여러 구역/카메라/시계열/이상/정비 이력이 있는
--     상용 운영 환경처럼 보이도록 데이터를 보강한다.
--   - demo_seed.sql 실행 후 추가로 실행한다.
--
-- 재실행 안전:
--   - idempotency_key / ticket_number / NOT EXISTS 조건으로 중복 삽입 방지
-- ============================================================

BEGIN;

-- ============================================================
-- 1. 운영 구역과 카메라 확장
-- ============================================================
INSERT INTO zones (zone_id, zone_code, zone_name, zone_type, is_active, created_at)
VALUES
    (2, 'ZONE_002', 'Bupyeong Station North Gate', 'ENTRY', TRUE, NOW()),
    (3, 'ZONE_003', 'Bupyeong Market Junction', 'INTERNAL', TRUE, NOW()),
    (4, 'ZONE_004', 'Gulpocheon Riverside Road', 'EXIT', TRUE, NOW())
ON CONFLICT (zone_code) DO NOTHING;

INSERT INTO cameras (camera_id, zone_id, camera_code, camera_name, stream_url, direction_type, is_active, created_at)
VALUES
    (6,  2, 'CAM_006', '부평역 북광장 진입 카메라', NULL, 'IN', TRUE, NOW()),
    (7,  2, 'CAM_007', '부평역 북광장 출차 카메라', NULL, 'OUT', TRUE, NOW()),
    (8,  2, 'CAM_008', '북광장 버스전용차로 카메라', NULL, 'BOTH', TRUE, NOW()),
    (9,  2, 'CAM_009', '북광장 주차장 출구 카메라', NULL, 'OUT', TRUE, NOW()),
    (10, 3, 'CAM_010', '부평시장 동측 진입 카메라', NULL, 'IN', TRUE, NOW()),
    (11, 3, 'CAM_011', '부평시장 서측 출차 카메라', NULL, 'OUT', TRUE, NOW()),
    (12, 3, 'CAM_012', '부평시장 교차로 중앙 카메라', NULL, 'BOTH', TRUE, NOW()),
    (13, 3, 'CAM_013', '시장 보행자 횡단로 카메라', NULL, 'IN', TRUE, NOW()),
    (14, 3, 'CAM_014', '시장 상가 배송차로 카메라', NULL, 'OUT', TRUE, NOW()),
    (15, 4, 'CAM_015', '굴포천변 진입로 카메라', NULL, 'IN', TRUE, NOW()),
    (16, 4, 'CAM_016', '굴포천변 출구 카메라', NULL, 'OUT', TRUE, NOW()),
    (17, 4, 'CAM_017', '굴포천 지하차도 카메라', NULL, 'BOTH', TRUE, NOW()),
    (18, 4, 'CAM_018', '굴포천 램프 A 카메라', NULL, 'IN', TRUE, NOW()),
    (19, 4, 'CAM_019', '굴포천 램프 B 카메라', NULL, 'OUT', TRUE, NOW()),
    (20, 4, 'CAM_020', '굴포천 긴급차로 카메라', NULL, 'BOTH', TRUE, NOW())
ON CONFLICT (camera_code) DO UPDATE
SET camera_name = EXCLUDED.camera_name,
    zone_id = EXCLUDED.zone_id,
    direction_type = EXCLUDED.direction_type,
    is_active = TRUE;

SELECT setval(pg_get_serial_sequence('zones', 'zone_id'), GREATEST((SELECT MAX(zone_id) FROM zones), 4));
SELECT setval(pg_get_serial_sequence('cameras', 'camera_id'), GREATEST((SELECT MAX(camera_id) FROM cameras), 20));

-- ============================================================
-- 2. 14일 기준선 health sample: 20대 x 14일 x 8구간 = 2,240건
-- ============================================================
INSERT INTO camera_health_samples
    (camera_id, processor_code, sampled_at, sample_window_seconds,
     fps_avg, frame_drop_rate, latency_p95_ms,
     blur_score_avg, brightness_score_avg,
     detection_count, ocr_attempt_count, ocr_failure_count, ocr_fail_rate,
     cpu_usage_pct, memory_usage_pct, disk_usage_pct, network_rtt_ms,
     last_frame_at,
     data_source, quality_status, is_imputed, is_late_sample,
     idempotency_key)
SELECT
    c.camera_id,
    'proc-cam' || c.camera_id,
    TIMESTAMP '2026-05-20 00:00:00'
        + (d || ' days')::INTERVAL
        + (slot * INTERVAL '180 minutes')
        + (c.camera_id * INTERVAL '1 second'),
    60,
    27.8 + (c.camera_id % 4) * 0.35 + (slot % 3) * 0.20,
    0.010 + (c.camera_id % 5) * 0.002 + (slot % 2) * 0.001,
    118 + (c.camera_id % 6) * 8 + (slot % 4) * 5,
    0.050 + (c.camera_id % 4) * 0.008,
    0.810 + (slot % 3) * 0.020,
    38 + (c.camera_id % 7) + (slot % 4),
    35 + (c.camera_id % 6) + (slot % 5),
    1 + (c.camera_id % 3),
    0.040 + (c.camera_id % 4) * 0.006,
    31.0 + (c.camera_id % 8) * 2.2,
    51.0 + (c.camera_id % 6) * 2.1,
    38.0 + (c.camera_id % 5) * 1.5,
    18 + (c.camera_id % 8) * 4,
    TIMESTAMP '2026-05-20 00:00:00'
        + (d || ' days')::INTERVAL
        + (slot * INTERVAL '180 minutes')
        + (c.camera_id * INTERVAL '1 second')
        - INTERVAL '2 seconds',
    'SIMULATED',
    'COMPLETE',
    FALSE,
    FALSE,
    'commercial-bl-cam' || c.camera_id || '-day' || d || '-slot' || slot
FROM cameras c
CROSS JOIN generate_series(0, 13) AS d
CROSS JOIN generate_series(0, 7) AS slot
WHERE c.camera_id BETWEEN 1 AND 20
ON CONFLICT (idempotency_key) DO NOTHING;

-- ============================================================
-- 3. 장애 구간 health sample: 발표용 활성/처리 이벤트의 최근 원천 데이터
-- ============================================================
WITH scenario(camera_id, anomaly_type) AS (
    VALUES
        (6,  'LATENCY_DEGRADATION'),
        (7,  'NETWORK_INSTABILITY'),
        (8,  'RESOURCE_SATURATION'),
        (9,  'BLUR_DEGRADATION'),
        (10, 'FPS_DEGRADATION'),
        (11, 'FRAME_DROP_DEGRADATION'),
        (12, 'OCR_QUALITY_DEGRADATION'),
        (13, 'CAMERA_OFFLINE'),
        (14, 'LATENCY_DEGRADATION'),
        (15, 'NETWORK_INSTABILITY'),
        (16, 'RESOURCE_SATURATION'),
        (17, 'BLUR_DEGRADATION'),
        (18, 'FPS_DEGRADATION'),
        (19, 'FRAME_DROP_DEGRADATION'),
        (20, 'OCR_QUALITY_DEGRADATION')
)
INSERT INTO camera_health_samples
    (camera_id, processor_code, sampled_at, sample_window_seconds,
     fps_avg, frame_drop_rate, latency_p95_ms,
     blur_score_avg, brightness_score_avg,
     detection_count, ocr_attempt_count, ocr_failure_count, ocr_fail_rate,
     cpu_usage_pct, memory_usage_pct, disk_usage_pct, network_rtt_ms,
     last_frame_at,
     data_source, quality_status, is_imputed, is_late_sample,
     idempotency_key)
SELECT
    s.camera_id,
    'proc-cam' || s.camera_id,
    NOW()::TIMESTAMP - (n * INTERVAL '1 minute') - (s.camera_id * INTERVAL '1 second'),
    60,
    CASE WHEN s.anomaly_type = 'FPS_DEGRADATION' THEN 6.0 ELSE 25.0 END,
    CASE WHEN s.anomaly_type = 'FRAME_DROP_DEGRADATION' THEN 0.680000 ELSE 0.040000 END,
    CASE WHEN s.anomaly_type = 'LATENCY_DEGRADATION' THEN 4200 ELSE 180 END,
    CASE WHEN s.anomaly_type = 'BLUR_DEGRADATION' THEN 0.880000 ELSE 0.080000 END,
    0.72,
    CASE WHEN s.anomaly_type = 'CAMERA_OFFLINE' THEN 0 ELSE 30 END,
    CASE WHEN s.anomaly_type = 'CAMERA_OFFLINE' THEN 0 ELSE 30 END,
    CASE WHEN s.anomaly_type = 'OCR_QUALITY_DEGRADATION' THEN 25 ELSE 2 END,
    CASE WHEN s.anomaly_type = 'OCR_QUALITY_DEGRADATION' THEN 0.830000 ELSE 0.060000 END,
    CASE WHEN s.anomaly_type = 'RESOURCE_SATURATION' THEN 93.0 ELSE 45.0 END,
    CASE WHEN s.anomaly_type = 'RESOURCE_SATURATION' THEN 91.0 ELSE 58.0 END,
    48.0,
    CASE WHEN s.anomaly_type = 'NETWORK_INSTABILITY' THEN 760 ELSE 42 END,
    CASE WHEN s.anomaly_type = 'CAMERA_OFFLINE'
         THEN NOW()::TIMESTAMP - INTERVAL '20 minutes'
         ELSE NOW()::TIMESTAMP - (n * INTERVAL '1 minute') - (s.camera_id * INTERVAL '1 second') - INTERVAL '2 seconds'
    END,
    'FAULT_INJECTED',
    CASE WHEN s.anomaly_type = 'CAMERA_OFFLINE' THEN 'INSUFFICIENT' ELSE 'COMPLETE' END,
    FALSE,
    FALSE,
    'commercial-fault-cam' || s.camera_id || '-' || s.anomaly_type || '-n' || n
FROM scenario s
CROSS JOIN generate_series(1, 6) AS n
ON CONFLICT (idempotency_key) DO NOTHING;

-- ============================================================
-- 4. 교통 맥락 sample: 20대 x 14일 x 4구간 = 1,120건
-- ============================================================
INSERT INTO traffic_context_samples
    (camera_id, zone_id, sampled_at, window_minutes,
     vehicle_count, avg_speed_kmh, speed_measurement_count, speed_violation_count,
     ocr_attempt_count, ocr_success_count, ocr_failure_count,
     in_count, out_count,
     data_source, quality_status, is_imputed, idempotency_key)
SELECT
    c.camera_id,
    c.zone_id,
    TIMESTAMP '2026-05-20 00:02:00'
        + (d || ' days')::INTERVAL
        + (slot * INTERVAL '360 minutes')
        + (c.camera_id * INTERVAL '1 second'),
    5,
    32 + (c.camera_id % 9) + (slot % 3),
    42.0 + (c.camera_id % 7) * 1.8,
    28 + (c.camera_id % 6),
    c.camera_id % 3,
    30 + (c.camera_id % 6),
    26 + (c.camera_id % 5),
    2 + (c.camera_id % 3),
    15 + (slot % 4),
    14 + (c.camera_id % 4),
    'SIMULATED',
    'COMPLETE',
    FALSE,
    'commercial-traffic-cam' || c.camera_id || '-day' || d || '-slot' || slot
FROM cameras c
CROSS JOIN generate_series(0, 13) AS d
CROSS JOIN generate_series(0, 3) AS slot
WHERE c.camera_id BETWEEN 1 AND 20
ON CONFLICT (idempotency_key) DO NOTHING;

-- ============================================================
-- 5. 발표용 이상 이벤트 18건
-- ============================================================
WITH scenario(
    scenario_key, camera_id, anomaly_type, severity, event_status,
    detection_method, anomaly_score, priority, ticket_status, assignee_role,
    age_minutes
) AS (
    VALUES
        ('C06-LAT', 6,  'LATENCY_DEGRADATION',      'WARNING',  'OPEN',         'RULE',             0.620000, 'P2', 'OPEN',        NULL,         22),
        ('C07-NET', 7,  'NETWORK_INSTABILITY',      'CRITICAL', 'ACKNOWLEDGED', 'RULE',             0.910000, 'P1', 'ASSIGNED',    'MAINTAINER', 38),
        ('C08-RES', 8,  'RESOURCE_SATURATION',      'WARNING',  'ACKNOWLEDGED', 'RULE',             0.680000, 'P2', 'IN_PROGRESS', 'MAINTAINER', 55),
        ('C09-BLR', 9,  'BLUR_DEGRADATION',         'WARNING',  'RESOLVED',     'RULE',             0.570000, 'P3', 'CLOSED',      'MAINTAINER', 180),
        ('C10-FPS', 10, 'FPS_DEGRADATION',          'CRITICAL', 'OPEN',         'TREND_PROJECTION', 0.940000, 'P1', 'OPEN',        NULL,         16),
        ('C11-DRP', 11, 'FRAME_DROP_DEGRADATION',   'CRITICAL', 'ACKNOWLEDGED', 'RULE',             0.890000, 'P1', 'ASSIGNED',    'MAINTAINER', 42),
        ('C12-OCR', 12, 'OCR_QUALITY_DEGRADATION',  'WARNING',  'OPEN',         'RULE',             0.610000, 'P2', 'OPEN',        NULL,         28),
        ('C13-OFF', 13, 'CAMERA_OFFLINE',           'CRITICAL', 'ACKNOWLEDGED', 'RULE',             0.990000, 'P1', 'IN_PROGRESS', 'MAINTAINER', 64),
        ('C14-LAT', 14, 'LATENCY_DEGRADATION',      'CRITICAL', 'OPEN',         'RULE',             0.880000, 'P1', 'OPEN',        NULL,         12),
        ('C15-NET', 15, 'NETWORK_INSTABILITY',      'WARNING',  'RESOLVED',     'RULE',             0.560000, 'P3', 'CLOSED',      'MAINTAINER', 220),
        ('C16-RES', 16, 'RESOURCE_SATURATION',      'CRITICAL', 'ACKNOWLEDGED', 'RULE',             0.930000, 'P1', 'ASSIGNED',    'MAINTAINER', 35),
        ('C17-BLR', 17, 'BLUR_DEGRADATION',         'CRITICAL', 'OPEN',         'RULE',             0.920000, 'P1', 'OPEN',        NULL,         18),
        ('C18-FPS', 18, 'FPS_DEGRADATION',          'WARNING',  'ACKNOWLEDGED', 'ROBUST_Z_SCORE',   0.670000, 'P2', 'IN_PROGRESS', 'MAINTAINER', 72),
        ('C19-DRP', 19, 'FRAME_DROP_DEGRADATION',   'WARNING',  'RESOLVED',     'RULE',             0.580000, 'P3', 'RESOLVED',    'MAINTAINER', 145),
        ('C20-OCR', 20, 'OCR_QUALITY_DEGRADATION',  'CRITICAL', 'OPEN',         'RULE',             0.960000, 'P1', 'OPEN',        NULL,         20),
        ('C06-NET', 6,  'NETWORK_INSTABILITY',      'WARNING',  'RESOLVED',     'RULE',             0.550000, 'P3', 'CLOSED',      'MAINTAINER', 260),
        ('C12-BLR', 12, 'BLUR_DEGRADATION',         'WARNING',  'DISMISSED',    'RULE',             0.510000, 'P3', 'CLOSED',      'OPERATOR',   310),
        ('C18-LAT', 18, 'LATENCY_DEGRADATION',      'WARNING',  'RESOLVED',     'RULE',             0.590000, 'P3', 'CLOSED',      'MAINTAINER', 330)
)
INSERT INTO anomaly_events
    (target_type, target_camera_id, anomaly_type, severity, status,
     detection_method, data_source, policy_id, detector_version_id,
     anomaly_score, baseline_source, baseline_from, baseline_to, baseline_sample_count,
     trend_slope, trend_confidence, prediction_horizon_minutes,
     projected_threshold_crossing_at,
     suspected_causes_json, confirmed_cause, resolution_note, recurrence_count,
     first_detected_at, last_detected_at, acknowledged_at, acknowledged_by,
     resolved_at, resolved_by, created_at, updated_at)
SELECT
    'CAMERA',
    s.camera_id,
    s.anomaly_type,
    s.severity,
    s.event_status,
    s.detection_method,
    'FAULT_INJECTED',
    CASE s.anomaly_type
        WHEN 'CAMERA_OFFLINE' THEN (SELECT id FROM anomaly_policies WHERE policy_code = 'CAMERA_OFFLINE_RULE_V1')
        WHEN 'FPS_DEGRADATION' THEN (SELECT id FROM anomaly_policies WHERE policy_code = 'FPS_DEGRADATION_RULE_V1')
        WHEN 'FRAME_DROP_DEGRADATION' THEN (SELECT id FROM anomaly_policies WHERE policy_code = 'FRAME_DROP_DEGRADATION_RULE_V1')
        WHEN 'LATENCY_DEGRADATION' THEN (SELECT id FROM anomaly_policies WHERE policy_code = 'LATENCY_DEGRADATION_RULE_V1')
        WHEN 'BLUR_DEGRADATION' THEN (SELECT id FROM anomaly_policies WHERE policy_code = 'BLUR_DEGRADATION_RULE_V1')
        WHEN 'OCR_QUALITY_DEGRADATION' THEN (SELECT id FROM anomaly_policies WHERE policy_code = 'OCR_QUALITY_DEGRADATION_RULE_V1')
        WHEN 'RESOURCE_SATURATION' THEN (SELECT id FROM anomaly_policies WHERE policy_code = 'RESOURCE_SATURATION_RULE_V1')
        WHEN 'NETWORK_INSTABILITY' THEN (SELECT id FROM anomaly_policies WHERE policy_code = 'NETWORK_INSTABILITY_RULE_V1')
    END,
    CASE s.detection_method
        WHEN 'TREND_PROJECTION' THEN (SELECT id FROM detector_versions WHERE detector_name = 'camera-trend-projection' LIMIT 1)
        WHEN 'ROBUST_Z_SCORE' THEN (SELECT id FROM detector_versions WHERE detector_name = 'camera-robust-zscore' LIMIT 1)
        ELSE (SELECT id FROM detector_versions WHERE detector_name = 'camera-rule' LIMIT 1)
    END,
    s.anomaly_score,
    'CAMERA_30_MINUTE_BUCKET_14D',
    (NOW() - INTERVAL '14 days')::TIMESTAMP,
    NOW()::TIMESTAMP,
    112,
    CASE WHEN s.anomaly_type = 'FPS_DEGRADATION' THEN -0.270000 ELSE NULL END,
    CASE WHEN s.detection_method IN ('TREND_PROJECTION','ROBUST_Z_SCORE') THEN 0.780000 ELSE NULL END,
    CASE WHEN s.detection_method = 'TREND_PROJECTION' THEN 10 ELSE NULL END,
    CASE WHEN s.detection_method = 'TREND_PROJECTION' THEN (NOW() + INTERVAL '7 minutes')::TIMESTAMP ELSE NULL END,
    CASE s.anomaly_type
        WHEN 'NETWORK_INSTABILITY' THEN '[{"cause":"NETWORK_CONGESTION","score":0.81},{"cause":"UNKNOWN","score":0.19}]'::jsonb
        WHEN 'RESOURCE_SATURATION' THEN '[{"cause":"AI_PROCESSING_OVERLOAD","score":0.76},{"cause":"UNKNOWN","score":0.24}]'::jsonb
        WHEN 'BLUR_DEGRADATION' THEN '[{"cause":"CAMERA_LENS_OR_FOCUS","score":0.84},{"cause":"LOW_ILLUMINATION","score":0.16}]'::jsonb
        WHEN 'CAMERA_OFFLINE' THEN '[{"cause":"CAMERA_POWER_OR_NETWORK","score":0.90},{"cause":"UNKNOWN","score":0.10}]'::jsonb
        WHEN 'OCR_QUALITY_DEGRADATION' THEN '[{"cause":"OCR_PIPELINE_DEGRADATION","score":0.64},{"cause":"CAMERA_LENS_OR_FOCUS","score":0.36}]'::jsonb
        ELSE '[{"cause":"AI_PROCESSING_OVERLOAD","score":0.65},{"cause":"UNKNOWN","score":0.35}]'::jsonb
    END,
    CASE WHEN s.event_status IN ('RESOLVED','DISMISSED') THEN 'UNKNOWN' ELSE NULL END,
    CASE WHEN s.event_status = 'RESOLVED' THEN '현장 확인 및 조치 후 정상 범위 회복 확인.'
         WHEN s.event_status = 'DISMISSED' THEN '인접 카메라 비교 결과 일시적 외부 요인으로 판단.'
         ELSE NULL
    END,
    CASE WHEN s.event_status IN ('RESOLVED','DISMISSED') THEN 1 ELSE 0 END,
    (NOW() - (s.age_minutes || ' minutes')::INTERVAL)::TIMESTAMP,
    (NOW() - INTERVAL '2 minutes')::TIMESTAMP,
    CASE WHEN s.event_status IN ('ACKNOWLEDGED','RECOVERED','RESOLVED','DISMISSED')
         THEN (NOW() - ((s.age_minutes - 5) || ' minutes')::INTERVAL)::TIMESTAMP
         ELSE NULL
    END,
    CASE WHEN s.event_status IN ('ACKNOWLEDGED','RECOVERED','RESOLVED','DISMISSED')
         THEN (SELECT member_id FROM members WHERE role = 'OPERATOR' LIMIT 1)
         ELSE NULL
    END,
    CASE WHEN s.event_status IN ('RESOLVED','DISMISSED')
         THEN (NOW() - INTERVAL '30 minutes')::TIMESTAMP
         ELSE NULL
    END,
    CASE WHEN s.event_status IN ('RESOLVED','DISMISSED')
         THEN (SELECT member_id FROM members WHERE role IN ('MAINTAINER','OPERATOR') ORDER BY role LIMIT 1)
         ELSE NULL
    END,
    (NOW() - (s.age_minutes || ' minutes')::INTERVAL)::TIMESTAMP,
    NOW()::TIMESTAMP
FROM scenario s
WHERE NOT EXISTS (
    SELECT 1
    FROM anomaly_events e
    WHERE e.target_camera_id = s.camera_id
      AND e.anomaly_type = s.anomaly_type
      AND e.status = s.event_status
      AND e.data_source = 'FAULT_INJECTED'
);

-- ============================================================
-- 6. 이상 판단 근거 evidence
-- ============================================================
WITH scenario(scenario_key, camera_id, anomaly_type, metric_name, observed_value, baseline_value, threshold_value, unit) AS (
    VALUES
        ('C06-LAT', 6,  'LATENCY_DEGRADATION',     'latency_p95_ms',         4200.0, 150.0, 2000.0, 'ms'),
        ('C07-NET', 7,  'NETWORK_INSTABILITY',     'network_rtt_ms',          760.0,  42.0,  500.0, 'ms'),
        ('C08-RES', 8,  'RESOURCE_SATURATION',     'cpu_usage_pct',            93.0,  42.0,   85.0, 'pct'),
        ('C09-BLR', 9,  'BLUR_DEGRADATION',        'blur_score_avg',            0.88,   0.08,   0.75, 'score'),
        ('C10-FPS', 10, 'FPS_DEGRADATION',         'fps_avg',                   6.0,   28.5,   10.0, 'fps'),
        ('C11-DRP', 11, 'FRAME_DROP_DEGRADATION',  'frame_drop_rate',           0.68,   0.02,   0.60, 'rate'),
        ('C12-OCR', 12, 'OCR_QUALITY_DEGRADATION', 'ocr_fail_rate',             0.83,   0.06,   0.70, 'rate'),
        ('C13-OFF', 13, 'CAMERA_OFFLINE',          'last_frame_seconds_ago', 1200.0,  NULL,    60.0, 'seconds'),
        ('C14-LAT', 14, 'LATENCY_DEGRADATION',     'latency_p95_ms',         5400.0, 170.0, 5000.0, 'ms'),
        ('C15-NET', 15, 'NETWORK_INSTABILITY',     'network_rtt_ms',          640.0,  38.0,  500.0, 'ms'),
        ('C16-RES', 16, 'RESOURCE_SATURATION',     'memory_usage_pct',          91.0,  55.0,   85.0, 'pct'),
        ('C17-BLR', 17, 'BLUR_DEGRADATION',        'blur_score_avg',            0.92,   0.09,   0.90, 'score'),
        ('C18-FPS', 18, 'FPS_DEGRADATION',         'fps_avg',                   8.8,   28.8,   10.0, 'fps'),
        ('C19-DRP', 19, 'FRAME_DROP_DEGRADATION',  'frame_drop_rate',           0.42,   0.02,   0.30, 'rate'),
        ('C20-OCR', 20, 'OCR_QUALITY_DEGRADATION', 'ocr_fail_rate',             0.94,   0.05,   0.90, 'rate'),
        ('C06-NET', 6,  'NETWORK_INSTABILITY',     'network_rtt_ms',          590.0,  42.0,  500.0, 'ms'),
        ('C12-BLR', 12, 'BLUR_DEGRADATION',        'blur_score_avg',            0.78,   0.08,   0.75, 'score'),
        ('C18-LAT', 18, 'LATENCY_DEGRADATION',     'latency_p95_ms',         2600.0, 160.0, 2000.0, 'ms')
)
INSERT INTO anomaly_event_evidence
    (anomaly_event_id, metric_name, observed_value, baseline_value, threshold_value,
     metric_score, unit, sampled_at, context_json)
SELECT
    e.id,
    s.metric_name,
    s.observed_value,
    s.baseline_value,
    s.threshold_value,
    CASE
        WHEN s.baseline_value IS NULL THEN 0.950000
        WHEN s.unit = 'fps' THEN LEAST(1.0, ABS(s.observed_value - s.threshold_value) / 10.0)
        ELSE LEAST(1.0, ABS(s.observed_value - s.threshold_value) / NULLIF(s.threshold_value, 0))
    END,
    s.unit,
    e.last_detected_at,
    ('{"direction":"AUTO","source":"commercial_demo_seed","scenarioKey":"' || s.scenario_key || '"}')::jsonb
FROM scenario s
JOIN anomaly_events e
  ON e.target_camera_id = s.camera_id
 AND e.anomaly_type = s.anomaly_type
 AND e.data_source = 'FAULT_INJECTED'
WHERE NOT EXISTS (
    SELECT 1
    FROM anomaly_event_evidence ev
    WHERE ev.anomaly_event_id = e.id
      AND ev.metric_name = s.metric_name
);

-- ============================================================
-- 7. 정비 티켓과 처리 상태 분포
-- ============================================================
WITH scenario(scenario_key, camera_id, anomaly_type, priority, ticket_status, assignee_role, age_minutes) AS (
    VALUES
        ('C06-LAT', 6,  'LATENCY_DEGRADATION',     'P2', 'OPEN',        NULL,         22),
        ('C07-NET', 7,  'NETWORK_INSTABILITY',     'P1', 'ASSIGNED',    'MAINTAINER', 38),
        ('C08-RES', 8,  'RESOURCE_SATURATION',     'P2', 'IN_PROGRESS', 'MAINTAINER', 55),
        ('C09-BLR', 9,  'BLUR_DEGRADATION',        'P3', 'CLOSED',      'MAINTAINER', 180),
        ('C10-FPS', 10, 'FPS_DEGRADATION',         'P1', 'OPEN',        NULL,         16),
        ('C11-DRP', 11, 'FRAME_DROP_DEGRADATION',  'P1', 'ASSIGNED',    'MAINTAINER', 42),
        ('C12-OCR', 12, 'OCR_QUALITY_DEGRADATION', 'P2', 'OPEN',        NULL,         28),
        ('C13-OFF', 13, 'CAMERA_OFFLINE',          'P1', 'IN_PROGRESS', 'MAINTAINER', 64),
        ('C14-LAT', 14, 'LATENCY_DEGRADATION',     'P1', 'OPEN',        NULL,         12),
        ('C15-NET', 15, 'NETWORK_INSTABILITY',     'P3', 'CLOSED',      'MAINTAINER', 220),
        ('C16-RES', 16, 'RESOURCE_SATURATION',     'P1', 'ASSIGNED',    'MAINTAINER', 35),
        ('C17-BLR', 17, 'BLUR_DEGRADATION',        'P1', 'OPEN',        NULL,         18),
        ('C18-FPS', 18, 'FPS_DEGRADATION',         'P2', 'IN_PROGRESS', 'MAINTAINER', 72),
        ('C19-DRP', 19, 'FRAME_DROP_DEGRADATION',  'P3', 'RESOLVED',    'MAINTAINER', 145),
        ('C20-OCR', 20, 'OCR_QUALITY_DEGRADATION', 'P1', 'OPEN',        NULL,         20),
        ('C06-NET', 6,  'NETWORK_INSTABILITY',     'P3', 'CLOSED',      'MAINTAINER', 260),
        ('C12-BLR', 12, 'BLUR_DEGRADATION',        'P3', 'CLOSED',      'OPERATOR',   310),
        ('C18-LAT', 18, 'LATENCY_DEGRADATION',     'P3', 'CLOSED',      'MAINTAINER', 330)
)
INSERT INTO maintenance_tickets
    (anomaly_event_id, ticket_number, priority, status,
     assignee_id, due_ack_at, due_start_at,
     acknowledged_at, started_at, resolved_at, closed_at,
     action_note, created_by, created_at, updated_at)
SELECT
    e.id,
    'MNT-D-' || s.scenario_key,
    s.priority,
    s.ticket_status,
    CASE WHEN s.assignee_role IS NULL THEN NULL
         ELSE (SELECT member_id FROM members WHERE role = s.assignee_role LIMIT 1)
    END,
    (NOW() - (s.age_minutes || ' minutes')::INTERVAL + CASE s.priority WHEN 'P1' THEN INTERVAL '10 minutes' WHEN 'P2' THEN INTERVAL '30 minutes' ELSE INTERVAL '4 hours' END)::TIMESTAMP,
    (NOW() - (s.age_minutes || ' minutes')::INTERVAL + CASE s.priority WHEN 'P1' THEN INTERVAL '30 minutes' WHEN 'P2' THEN INTERVAL '2 hours' ELSE INTERVAL '8 hours' END)::TIMESTAMP,
    CASE WHEN s.ticket_status IN ('ASSIGNED','IN_PROGRESS','RESOLVED','CLOSED')
         THEN (NOW() - ((s.age_minutes - 5) || ' minutes')::INTERVAL)::TIMESTAMP
         ELSE NULL
    END,
    CASE WHEN s.ticket_status IN ('IN_PROGRESS','RESOLVED','CLOSED')
         THEN (NOW() - ((s.age_minutes - 15) || ' minutes')::INTERVAL)::TIMESTAMP
         ELSE NULL
    END,
    CASE WHEN s.ticket_status IN ('RESOLVED','CLOSED')
         THEN (NOW() - INTERVAL '35 minutes')::TIMESTAMP
         ELSE NULL
    END,
    CASE WHEN s.ticket_status = 'CLOSED'
         THEN (NOW() - INTERVAL '20 minutes')::TIMESTAMP
         ELSE NULL
    END,
    CASE WHEN s.ticket_status IN ('RESOLVED','CLOSED') THEN '조치 완료 및 정상화 확인.'
         WHEN s.ticket_status = 'IN_PROGRESS' THEN '현장 점검 진행 중.'
         WHEN s.ticket_status = 'ASSIGNED' THEN '담당자 배정 완료.'
         ELSE NULL
    END,
    (SELECT member_id FROM members WHERE role = 'OPERATOR' LIMIT 1),
    (NOW() - (s.age_minutes || ' minutes')::INTERVAL)::TIMESTAMP,
    NOW()::TIMESTAMP
FROM scenario s
JOIN anomaly_events e
  ON e.target_camera_id = s.camera_id
 AND e.anomaly_type = s.anomaly_type
 AND e.data_source = 'FAULT_INJECTED'
WHERE NOT EXISTS (
    SELECT 1
    FROM maintenance_tickets mt
    WHERE mt.ticket_number = 'MNT-D-' || s.scenario_key
);

-- ============================================================
-- 8. 정비 timeline 이력
-- ============================================================
WITH ticket_scope AS (
    SELECT
        mt.id AS ticket_id,
        mt.status,
        mt.created_at,
        mt.ticket_number
    FROM maintenance_tickets mt
    WHERE mt.ticket_number LIKE 'MNT-D-%'
),
history_rows AS (
    SELECT ticket_id, NULL::VARCHAR AS from_status, 'OPEN'::VARCHAR AS to_status,
           '티켓 자동 생성' AS note, created_at AS changed_at
    FROM ticket_scope
    UNION ALL
    SELECT ticket_id, 'OPEN', 'ASSIGNED', '담당자 배정', created_at + INTERVAL '5 minutes'
    FROM ticket_scope
    WHERE status IN ('ASSIGNED','IN_PROGRESS','RESOLVED','CLOSED')
    UNION ALL
    SELECT ticket_id, 'ASSIGNED', 'IN_PROGRESS', '현장 점검 시작', created_at + INTERVAL '15 minutes'
    FROM ticket_scope
    WHERE status IN ('IN_PROGRESS','RESOLVED','CLOSED')
    UNION ALL
    SELECT ticket_id, 'IN_PROGRESS', 'RESOLVED', '원인 조치 및 정상화 확인', created_at + INTERVAL '1 hour'
    FROM ticket_scope
    WHERE status IN ('RESOLVED','CLOSED')
    UNION ALL
    SELECT ticket_id, 'RESOLVED', 'CLOSED', '운영자 검토 후 종결', created_at + INTERVAL '1 hour 20 minutes'
    FROM ticket_scope
    WHERE status = 'CLOSED'
)
INSERT INTO maintenance_ticket_histories
    (maintenance_ticket_id, from_status, to_status, changed_by, note, changed_at)
SELECT
    h.ticket_id,
    h.from_status,
    h.to_status,
    CASE WHEN h.to_status IN ('IN_PROGRESS','RESOLVED')
         THEN (SELECT member_id FROM members WHERE role = 'MAINTAINER' LIMIT 1)
         ELSE (SELECT member_id FROM members WHERE role = 'OPERATOR' LIMIT 1)
    END,
    h.note,
    h.changed_at
FROM history_rows h
WHERE NOT EXISTS (
    SELECT 1
    FROM maintenance_ticket_histories existing
    WHERE existing.maintenance_ticket_id = h.ticket_id
      AND COALESCE(existing.from_status, '') = COALESCE(h.from_status, '')
      AND existing.to_status = h.to_status
      AND existing.note = h.note
);

-- ============================================================
-- 9. LSTM shadow prediction log: 20대 x 12회 = 240건
-- ============================================================
INSERT INTO model_prediction_logs
    (camera_id, detector_version_id, evaluated_at,
     input_window_from, input_window_to,
     anomaly_score, warning_threshold, critical_threshold,
     predicted_anomaly, predicted_severity,
     data_source, quality_status, feature_schema_version, top_features_json)
SELECT
    c.camera_id,
    (SELECT id FROM detector_versions WHERE detector_name = 'camera-lstm-autoencoder' LIMIT 1),
    TIMESTAMP '2026-06-03 00:00:00' + (slot * INTERVAL '2 hours') + (c.camera_id * INTERVAL '1 second'),
    TIMESTAMP '2026-06-03 00:00:00' + (slot * INTERVAL '2 hours') - INTERVAL '30 minutes',
    TIMESTAMP '2026-06-03 00:00:00' + (slot * INTERVAL '2 hours'),
    CASE WHEN c.camera_id IN (7, 10, 13, 16, 20) AND slot >= 8 THEN 0.820000 ELSE 0.180000 + (c.camera_id % 5) * 0.030000 END,
    0.650000,
    0.800000,
    CASE WHEN c.camera_id IN (7, 10, 13, 16, 20) AND slot >= 8 THEN TRUE ELSE FALSE END,
    CASE WHEN c.camera_id IN (7, 10, 13, 16, 20) AND slot >= 8 THEN 'CRITICAL' ELSE NULL END,
    'SIMULATED',
    'COMPLETE',
    'camera-health-sequence-v1',
    '[{"feature":"latency_p95_ms","contribution":0.31},{"feature":"network_rtt_ms","contribution":0.24},{"feature":"fps_avg","contribution":0.18}]'::jsonb
FROM cameras c
CROSS JOIN generate_series(0, 11) AS slot
WHERE c.camera_id BETWEEN 1 AND 20
ON CONFLICT (camera_id, detector_version_id, evaluated_at) DO NOTHING;

ANALYZE camera_health_samples;
ANALYZE traffic_context_samples;
ANALYZE anomaly_events;
ANALYZE anomaly_event_evidence;
ANALYZE model_prediction_logs;
ANALYZE maintenance_tickets;
ANALYZE maintenance_ticket_histories;

COMMIT;

SELECT '=== commercial demo seed 적용 결과 ===' AS summary;

SELECT 'zones' AS table_name, COUNT(*) AS row_count FROM zones
UNION ALL
SELECT 'cameras', COUNT(*) FROM cameras
UNION ALL
SELECT 'camera_health_samples', COUNT(*) FROM camera_health_samples
UNION ALL
SELECT 'traffic_context_samples', COUNT(*) FROM traffic_context_samples
UNION ALL
SELECT 'anomaly_events', COUNT(*) FROM anomaly_events
UNION ALL
SELECT 'anomaly_event_evidence', COUNT(*) FROM anomaly_event_evidence
UNION ALL
SELECT 'model_prediction_logs', COUNT(*) FROM model_prediction_logs
UNION ALL
SELECT 'maintenance_tickets', COUNT(*) FROM maintenance_tickets
UNION ALL
SELECT 'maintenance_ticket_histories', COUNT(*) FROM maintenance_ticket_histories;
