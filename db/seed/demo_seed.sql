-- ============================================================
-- demo_seed.sql
-- TAS-PM 시연용 데모 데이터 (최종)
-- 기준: 01_요구사항_정의서 v1.6, 02_ERD_설계서_revised,
--       03_API_계약서_ver2, 08_DB_작업_TODO 섹션 7
--
-- 전제조건 (실행 전 확인):
--   - 007 / 008 migration 완료
--   - cameras: camera_id 1~5 존재
--   - zones:   zone_id 1 존재
--
-- 출처 정책 (요구사항 5-3절):
--   - 정상 기준선: SIMULATED (데모 예외 허용)
--   - 장애 구간:   FAULT_INJECTED
--   - REAL 데이터와 혼합 금지
--
-- 티켓 SLA (요구사항 7-2절):
--   P1: 확인 10분, 작업 시작 30분
--   P2: 확인 30분, 작업 시작 2시간
--   P3: 확인 4시간, 작업 시작 1영업일(8시간)
--
-- 재실행 안전: ON CONFLICT DO NOTHING / 고정 idempotency_key
-- ============================================================

BEGIN;

-- ============================================================
-- 0. 시연용 기본 zone/camera 보강
--    demo_seed는 camera_id 1~5, zone_id 1을 전제로 하므로
--    깨끗한 로컬 DB에서도 재현 가능하도록 최소 기준 데이터를 보강한다.
-- ============================================================
INSERT INTO zones (zone_id, zone_code, zone_name, zone_type, is_active, created_at)
VALUES (1, 'ZONE_001', 'Main Entry Zone', 'ENTRY', TRUE, NOW())
ON CONFLICT (zone_code) DO NOTHING;

INSERT INTO cameras (camera_id, zone_id, camera_code, camera_name, stream_url, direction_type, is_active, created_at)
VALUES
    (1, 1, 'CAM_001', 'Entry Camera 1', NULL, 'IN', TRUE, NOW()),
    (2, 1, 'CAM_002', 'Predictive Demo Camera 2', NULL, 'IN', TRUE, NOW()),
    (3, 1, 'CAM_003', 'Predictive Demo Camera 3', NULL, 'OUT', TRUE, NOW()),
    (4, 1, 'CAM_004', 'Predictive Demo Camera 4', NULL, 'IN', TRUE, NOW()),
    (5, 1, 'CAM_005', 'Predictive Demo Camera 5', NULL, 'OUT', TRUE, NOW())
ON CONFLICT (camera_code) DO NOTHING;

SELECT setval(pg_get_serial_sequence('zones', 'zone_id'), GREATEST((SELECT MAX(zone_id) FROM zones), 1));
SELECT setval(pg_get_serial_sequence('cameras', 'camera_id'), GREATEST((SELECT MAX(camera_id) FROM cameras), 5));

-- ============================================================
-- 0. 시연용 members 추가
--    기존 members 테이블(1차 TAS)에 OPERATOR·MAINTAINER 역할 추가
--    비밀번호: BCrypt('tas1234')
-- ============================================================
INSERT INTO members (name, email, phone, password, role, status, created_at)
VALUES
    ('운영자', 'operator@tas.com', '010-1111-2222',
     '$2a$10$ycTu6wBS5/pbCrL23CJlbuAMZluVx9jSoqS0Z9TB3e10q5r6lvE6K',
     'OPERATOR', 'ACTIVE', NOW()),
    ('정비사', 'maintainer@tas.com', '010-3333-4444',
     '$2a$10$ycTu6wBS5/pbCrL23CJlbuAMZluVx9jSoqS0Z9TB3e10q5r6lvE6K',
     'MAINTAINER', 'ACTIVE', NOW())
ON CONFLICT (email) DO NOTHING;

-- ============================================================
-- 1. SIMULATED 정상 기준선 샘플
--    요구사항 5-6절: 카메라별, 30분 시간대별, 최소 30개
--    요구사항 5-3절: 데모용 SIMULATED 기준선 허용
--    카메라 1~4: 3개 30분 bucket × 14일 × bucket당 3개 = bucket별 42개
--    카메라 5: 5개 (기준선 학습 중 시나리오)
-- ============================================================

-- 카메라 1: 정상 운영 기준선
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
    1, 'proc-cam1',
    TIMESTAMP '2026-06-02 04:45:00' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    60,
    28.5 + (n % 3) * 0.4,  0.010 + (n % 4) * 0.003,  132 + (n % 6) * 7,
    0.06 + (n % 3) * 0.01,  0.83,
    45 + (n % 8),  42 + (n % 6),  3 + (n % 2),  0.070 + (n % 3) * 0.005,
    34.0 + (n % 5) * 1.8,  57.5 + (n % 3) * 0.5,  42.0,  25 + (n % 5) * 2,
    TIMESTAMP '2026-06-02 04:44:58' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    'SIMULATED', 'COMPLETE', FALSE, FALSE,
    'demo-bl-cam1-0445-day' || n || '-slot' || m
FROM generate_series(0, 13) AS n
CROSS JOIN generate_series(0, 2) AS m
ON CONFLICT (idempotency_key) DO NOTHING;

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
    1, 'proc-cam1',
    TIMESTAMP '2026-06-02 04:15:00' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    60,
    29.0 + (n % 2) * 0.3,  0.009 + (n % 3) * 0.002,  128 + (n % 5) * 6,
    0.05 + (n % 4) * 0.01,  0.85,
    47 + (n % 7),  44 + (n % 5),  2 + (n % 3),  0.065 + (n % 3) * 0.005,
    33.0 + (n % 4) * 1.5,  56.0 + (n % 3) * 0.8,  41.5,  23 + (n % 4) * 2,
    TIMESTAMP '2026-06-02 04:14:58' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    'SIMULATED', 'COMPLETE', FALSE, FALSE,
    'demo-bl-cam1-0415-day' || n || '-slot' || m
FROM generate_series(0, 13) AS n
CROSS JOIN generate_series(0, 2) AS m
ON CONFLICT (idempotency_key) DO NOTHING;

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
    1, 'proc-cam1',
    TIMESTAMP '2026-06-02 05:45:00' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    60,
    28.0 + (n % 3) * 0.5,  0.011 + (n % 4) * 0.003,  135 + (n % 7) * 6,
    0.07 + (n % 3) * 0.01,  0.82,
    44 + (n % 6),  41 + (n % 5),  3 + (n % 2),  0.072 + (n % 3) * 0.005,
    35.5 + (n % 5) * 1.5,  58.0 + (n % 3) * 0.5,  42.5,  26 + (n % 4) * 2,
    TIMESTAMP '2026-06-02 05:44:58' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    'SIMULATED', 'COMPLETE', FALSE, FALSE,
    'demo-bl-cam1-0545-day' || n || '-slot' || m
FROM generate_series(0, 13) AS n
CROSS JOIN generate_series(0, 2) AS m
ON CONFLICT (idempotency_key) DO NOTHING;

-- 카메라 2: FPS 악화 추세 시나리오용 기준선
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
    2, 'proc-cam2',
    TIMESTAMP '2026-06-02 04:45:00' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    60,
    29.2 + (n % 2) * 0.4,  0.008 + (n % 3) * 0.002,  124 + (n % 5) * 6,
    0.05 + (n % 3) * 0.01,  0.86,
    48 + (n % 7),  45 + (n % 5),  2 + (n % 2),  0.055 + (n % 3) * 0.005,
    32.0 + (n % 4) * 1.5,  55.0 + (n % 3) * 0.8,  40.0,  21 + (n % 4) * 2,
    TIMESTAMP '2026-06-02 04:44:58' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    'SIMULATED', 'COMPLETE', FALSE, FALSE,
    'demo-bl-cam2-0445-day' || n || '-slot' || m
FROM generate_series(0, 13) AS n
CROSS JOIN generate_series(0, 2) AS m
ON CONFLICT (idempotency_key) DO NOTHING;

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
    2, 'proc-cam2',
    TIMESTAMP '2026-06-02 04:15:00' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    60,
    29.5 + (n % 2) * 0.3,  0.007 + (n % 3) * 0.002,  120 + (n % 5) * 5,
    0.04 + (n % 3) * 0.01,  0.87,
    49 + (n % 6),  46 + (n % 4),  2 + (n % 2),  0.050 + (n % 3) * 0.004,
    31.0 + (n % 4) * 1.5,  54.5 + (n % 3) * 0.5,  39.5,  20 + (n % 4) * 2,
    TIMESTAMP '2026-06-02 04:14:58' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    'SIMULATED', 'COMPLETE', FALSE, FALSE,
    'demo-bl-cam2-0415-day' || n || '-slot' || m
FROM generate_series(0, 13) AS n
CROSS JOIN generate_series(0, 2) AS m
ON CONFLICT (idempotency_key) DO NOTHING;

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
    2, 'proc-cam2',
    TIMESTAMP '2026-06-02 05:45:00' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    60,
    28.8 + (n % 3) * 0.4,  0.009 + (n % 3) * 0.002,  126 + (n % 5) * 6,
    0.06 + (n % 3) * 0.01,  0.85,
    47 + (n % 6),  44 + (n % 4),  2 + (n % 2),  0.058 + (n % 3) * 0.004,
    33.0 + (n % 4) * 1.5,  55.5 + (n % 3) * 0.5,  40.2,  22 + (n % 4) * 2,
    TIMESTAMP '2026-06-02 05:44:58' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    'SIMULATED', 'COMPLETE', FALSE, FALSE,
    'demo-bl-cam2-0545-day' || n || '-slot' || m
FROM generate_series(0, 13) AS n
CROSS JOIN generate_series(0, 2) AS m
ON CONFLICT (idempotency_key) DO NOTHING;

-- 카메라 3: 오프라인 시나리오용 기준선
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
    3, 'proc-cam3',
    TIMESTAMP '2026-06-02 04:45:00' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    60,
    27.8 + (n % 3) * 0.5,  0.012 + (n % 4) * 0.003,  142 + (n % 6) * 8,
    0.07 + (n % 4) * 0.01,  0.80,
    41 + (n % 7),  38 + (n % 5),  4 + (n % 2),  0.090 + (n % 4) * 0.005,
    38.0 + (n % 5) * 2.0,  60.5 + (n % 3) * 0.5,  43.0,  28 + (n % 5) * 3,
    TIMESTAMP '2026-06-02 04:44:58' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    'SIMULATED', 'COMPLETE', FALSE, FALSE,
    'demo-bl-cam3-0445-day' || n || '-slot' || m
FROM generate_series(0, 13) AS n
CROSS JOIN generate_series(0, 2) AS m
ON CONFLICT (idempotency_key) DO NOTHING;

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
    3, 'proc-cam3',
    TIMESTAMP '2026-06-02 04:15:00' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    60,
    28.2 + (n % 3) * 0.4,  0.011 + (n % 3) * 0.003,  138 + (n % 5) * 7,
    0.06 + (n % 4) * 0.01,  0.82,
    43 + (n % 7),  40 + (n % 5),  3 + (n % 2),  0.085 + (n % 4) * 0.005,
    37.0 + (n % 5) * 1.8,  59.5 + (n % 3) * 0.5,  42.5,  27 + (n % 5) * 3,
    TIMESTAMP '2026-06-02 04:14:58' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    'SIMULATED', 'COMPLETE', FALSE, FALSE,
    'demo-bl-cam3-0415-day' || n || '-slot' || m
FROM generate_series(0, 13) AS n
CROSS JOIN generate_series(0, 2) AS m
ON CONFLICT (idempotency_key) DO NOTHING;

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
    3, 'proc-cam3',
    TIMESTAMP '2026-06-02 05:45:00' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    60,
    27.5 + (n % 3) * 0.5,  0.013 + (n % 4) * 0.003,  145 + (n % 6) * 8,
    0.08 + (n % 4) * 0.01,  0.79,
    40 + (n % 7),  37 + (n % 5),  4 + (n % 2),  0.092 + (n % 4) * 0.005,
    39.0 + (n % 5) * 2.0,  61.0 + (n % 3) * 0.5,  43.5,  29 + (n % 5) * 3,
    TIMESTAMP '2026-06-02 05:44:58' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    'SIMULATED', 'COMPLETE', FALSE, FALSE,
    'demo-bl-cam3-0545-day' || n || '-slot' || m
FROM generate_series(0, 13) AS n
CROSS JOIN generate_series(0, 2) AS m
ON CONFLICT (idempotency_key) DO NOTHING;

-- 카메라 4: OCR 품질 저하 시나리오용 기준선
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
    4, 'proc-cam4',
    TIMESTAMP '2026-06-02 04:45:00' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    60,
    28.9 + (n % 3) * 0.3,  0.010 + (n % 3) * 0.002,  130 + (n % 5) * 6,
    0.06 + (n % 3) * 0.01,  0.84,
    44 + (n % 6),  41 + (n % 5),  3 + (n % 2),  0.068 + (n % 3) * 0.005,
    35.0 + (n % 4) * 1.5,  57.0 + (n % 3) * 0.5,  41.5,  25 + (n % 4) * 2,
    TIMESTAMP '2026-06-02 04:44:58' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    'SIMULATED', 'COMPLETE', FALSE, FALSE,
    'demo-bl-cam4-0445-day' || n || '-slot' || m
FROM generate_series(0, 13) AS n
CROSS JOIN generate_series(0, 2) AS m
ON CONFLICT (idempotency_key) DO NOTHING;

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
    4, 'proc-cam4',
    TIMESTAMP '2026-06-02 04:15:00' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    60,
    29.2 + (n % 2) * 0.3,  0.009 + (n % 3) * 0.002,  126 + (n % 5) * 5,
    0.05 + (n % 3) * 0.01,  0.86,
    46 + (n % 6),  43 + (n % 4),  2 + (n % 2),  0.062 + (n % 3) * 0.005,
    34.0 + (n % 4) * 1.5,  56.5 + (n % 3) * 0.5,  41.0,  24 + (n % 4) * 2,
    TIMESTAMP '2026-06-02 04:14:58' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    'SIMULATED', 'COMPLETE', FALSE, FALSE,
    'demo-bl-cam4-0415-day' || n || '-slot' || m
FROM generate_series(0, 13) AS n
CROSS JOIN generate_series(0, 2) AS m
ON CONFLICT (idempotency_key) DO NOTHING;

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
    4, 'proc-cam4',
    TIMESTAMP '2026-06-02 05:45:00' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    60,
    28.6 + (n % 3) * 0.4,  0.011 + (n % 3) * 0.002,  133 + (n % 5) * 6,
    0.07 + (n % 3) * 0.01,  0.83,
    43 + (n % 6),  40 + (n % 4),  3 + (n % 2),  0.070 + (n % 3) * 0.005,
    36.0 + (n % 4) * 1.5,  57.5 + (n % 3) * 0.5,  42.0,  26 + (n % 4) * 2,
    TIMESTAMP '2026-06-02 05:44:58' + (n || ' days')::INTERVAL + (m * INTERVAL '5 minutes'),
    'SIMULATED', 'COMPLETE', FALSE, FALSE,
    'demo-bl-cam4-0545-day' || n || '-slot' || m
FROM generate_series(0, 13) AS n
CROSS JOIN generate_series(0, 2) AS m
ON CONFLICT (idempotency_key) DO NOTHING;

-- ============================================================
-- 2. 시연 시각 기준 최근 60분 샘플
-- ============================================================

-- 시나리오 A: 카메라 1 — 정상 운영
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
    1, 'proc-cam1',
    (NOW() - ((60 - n) || ' minutes')::INTERVAL)::TIMESTAMP,
    60,
    29.0 + (n % 3) * 0.3,  0.010 + (n % 3) * 0.002,  130 + (n % 5) * 5,
    0.06 + (n % 3) * 0.01,  0.84,
    46 + (n % 6),  43 + (n % 4),  3 + (n % 2),  0.068,
    34.0 + (n % 4) * 1.5,  57.0,  42.0,  24 + (n % 4) * 2,
    (NOW() - ((60 - n) || ' minutes')::INTERVAL - '2 seconds'::INTERVAL)::TIMESTAMP,
    'SIMULATED', 'COMPLETE', FALSE, FALSE,
    'demo-cam1-normal-min' || n
FROM generate_series(1, 60) AS n
ON CONFLICT (idempotency_key) DO NOTHING;

-- 시나리오 B: 카메라 2 — FPS 악화 추세 (28fps → 8fps)
--   P2 조건: 10분 내 CRITICAL(5fps) 도달 예측
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
    2, 'proc-cam2',
    (NOW() - ((60 - n) || ' minutes')::INTERVAL)::TIMESTAMP,
    60,
    GREATEST(28.0 - (n * 0.33), 8.0),
    LEAST(n * 0.004, 0.25),
    120 + n * 8,
    0.06,  0.85,
    GREATEST(8, 48 - (n * 0.4)::INT),
    GREATEST(7, 45 - (n * 0.3)::INT),
    LEAST(14, 2 + (n * 0.2)::INT),
    LEAST(0.82, 0.054 + n * 0.013),
    LEAST(78.0, 32.0 + n * 0.77),  55.5,  40.0,
    20 + n * 2,
    (NOW() - ((60 - n) || ' minutes')::INTERVAL - '2 seconds'::INTERVAL)::TIMESTAMP,
    CASE WHEN n <= 30 THEN 'SIMULATED' ELSE 'FAULT_INJECTED' END,
    'COMPLETE', FALSE, FALSE,
    'demo-cam2-fps-trend-min' || n
FROM generate_series(1, 60) AS n
ON CONFLICT (idempotency_key) DO NOTHING;

-- 시나리오 C: 카메라 3 — 오프라인 (15분 전부터)
--   정상 45분 → 오프라인 15분
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
    3, 'proc-cam3',
    (NOW() - ((60 - n) || ' minutes')::INTERVAL)::TIMESTAMP,
    60,
    27.8 + (n % 4) * 0.3,  0.012 + (n % 3) * 0.002,  143 + (n % 5) * 7,
    0.07 + (n % 3) * 0.01,  0.81,
    41 + (n % 6),  38 + (n % 4),  4 + (n % 2),  0.092,
    38.5 + (n % 4) * 1.8,  60.0,  43.0,  28 + (n % 4) * 2,
    (NOW() - ((60 - n) || ' minutes')::INTERVAL - '2 seconds'::INTERVAL)::TIMESTAMP,
    'SIMULATED', 'COMPLETE', FALSE, FALSE,
    'demo-cam3-pre-offline-min' || n
FROM generate_series(1, 45) AS n
ON CONFLICT (idempotency_key) DO NOTHING;

-- 오프라인 구간: fps=0, last_frame_at 고정
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
    3, 'proc-cam3',
    (NOW() - ((15 - n) || ' minutes')::INTERVAL)::TIMESTAMP,
    60,
    0.0,  1.0,  NULL,
    NULL,  NULL,
    0,  0,  0,  NULL,
    5.0,  55.0,  43.0,  NULL,
    (NOW() - '15 minutes'::INTERVAL - '30 seconds'::INTERVAL)::TIMESTAMP,
    'FAULT_INJECTED', 'COMPLETE', FALSE, FALSE,
    'demo-cam3-offline-min' || n
FROM generate_series(1, 15) AS n
ON CONFLICT (idempotency_key) DO NOTHING;

-- 시나리오 D: 카메라 4 — OCR 품질 저하 (최근 30분)
--   ocr_attempt_count >= 20 유지 (요구사항 6-2절)
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
    4, 'proc-cam4',
    (NOW() - ((60 - n) || ' minutes')::INTERVAL)::TIMESTAMP,
    60,
    29.0 + (n % 3) * 0.2,  0.010 + (n % 3) * 0.002,  129 + (n % 5) * 5,
    0.06 + CASE WHEN n > 30 THEN LEAST(0.55, (n-30) * 0.017) ELSE 0 END,
    CASE WHEN n > 30 THEN GREATEST(0.52, 0.85 - (n-30) * 0.011) ELSE 0.85 END,
    44 + (n % 5),
    40 + (n % 3),
    CASE WHEN n > 30 THEN LEAST(36, 3 + (n-30)) ELSE 3 + (n % 2) END,
    CASE WHEN n > 30 THEN LEAST(0.90, 0.068 + (n-30) * 0.028) ELSE 0.068 + (n % 3) * 0.004 END,
    35.0 + (n % 4) * 1.5,  57.0,  41.5,  25 + (n % 4) * 2,
    (NOW() - ((60 - n) || ' minutes')::INTERVAL - '2 seconds'::INTERVAL)::TIMESTAMP,
    CASE WHEN n > 30 THEN 'FAULT_INJECTED' ELSE 'SIMULATED' END,
    'COMPLETE', FALSE, FALSE,
    'demo-cam4-ocr-min' || n
FROM generate_series(1, 60) AS n
ON CONFLICT (idempotency_key) DO NOTHING;

-- 시나리오 E: 카메라 5 — 기준선 학습 중 (5개 = 30개 미만)
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
    5, 'proc-cam5',
    (NOW() - (n || ' days')::INTERVAL)::TIMESTAMP + '03:00:00'::INTERVAL,
    60,
    29.0 + (n % 2) * 0.4,  0.011,  133,  0.07,  0.82,
    43,  40,  3,  0.075,
    36.5,  58.5,  41.0,  26,
    (NOW() - (n || ' days')::INTERVAL)::TIMESTAMP + '02:59:58'::INTERVAL,
    'SIMULATED', 'COMPLETE', FALSE, FALSE,
    'demo-cam5-learning-day' || n
FROM generate_series(1, 5) AS n
ON CONFLICT (idempotency_key) DO NOTHING;

-- ============================================================
-- 3. traffic_context_samples
--    요구사항 6-5절: 교통 맥락 교차검증
-- ============================================================

-- 카메라 1: 정상 교통 흐름 (최근 60분, 5분 단위 12개)
INSERT INTO traffic_context_samples
    (camera_id, zone_id, sampled_at, window_minutes,
     vehicle_count, avg_speed_kmh,
     speed_measurement_count, speed_violation_count,
     ocr_attempt_count, ocr_success_count, ocr_failure_count,
     in_count, out_count,
     data_source, quality_status, is_imputed,
     idempotency_key)
SELECT
    1, 1,
    (NOW() - ((60 - n * 5) || ' minutes')::INTERVAL)::TIMESTAMP,
    5,
    43 + (n % 5) * 2,  49.0 + (n % 4) * 1.5,
    41 + (n % 4),  1 + (n % 3),
    39 + (n % 4),  36 + (n % 4),  2 + (n % 2),
    22 + (n % 4),  21 + (n % 4),
    'SIMULATED', 'COMPLETE', FALSE,
    'demo-tcs-cam1-zone1-bucket' || n
FROM generate_series(1, 12) AS n
ON CONFLICT (camera_id, zone_id, sampled_at) DO NOTHING;

-- 카메라 2: 교통량 정상 (FPS 악화가 장비 원인임을 교차검증으로 확인)
INSERT INTO traffic_context_samples
    (camera_id, zone_id, sampled_at, window_minutes,
     vehicle_count, avg_speed_kmh,
     speed_measurement_count, speed_violation_count,
     ocr_attempt_count, ocr_success_count, ocr_failure_count,
     in_count, out_count,
     data_source, quality_status, is_imputed,
     idempotency_key)
SELECT
    2, 1,
    (NOW() - ((60 - n * 5) || ' minutes')::INTERVAL)::TIMESTAMP,
    5,
    45 + (n % 4) * 2,  50.5 + (n % 3) * 1.5,
    43 + (n % 4),  1 + (n % 2),
    41 + (n % 3),  39 + (n % 3),  2,
    23 + (n % 3),  22 + (n % 3),
    'SIMULATED', 'COMPLETE', FALSE,
    'demo-tcs-cam2-zone1-bucket' || n
FROM generate_series(1, 12) AS n
ON CONFLICT (camera_id, zone_id, sampled_at) DO NOTHING;

-- 실제 교통 감소 시나리오 (카메라 1, 최근 30분 교통량 급감 — CCTV는 정상)
-- 요구사항 6-5절: 여러 카메라 교통량 함께 감소 + CCTV 정상 → 정비 이벤트 미생성
INSERT INTO traffic_context_samples
    (camera_id, zone_id, sampled_at, window_minutes,
     vehicle_count, avg_speed_kmh,
     speed_measurement_count, speed_violation_count,
     ocr_attempt_count, ocr_success_count, ocr_failure_count,
     in_count, out_count,
     data_source, quality_status, is_imputed,
     idempotency_key)
SELECT
    1, 1,
    (NOW() - ((30 - n * 5) || ' minutes')::INTERVAL)::TIMESTAMP,
    5,
    3 + (n % 3),  38.0 + (n % 3) * 2.0,
    3 + (n % 2),  0,
    3 + (n % 2),  3 + (n % 2),  0,
    2 + (n % 2),  2 + (n % 2),
    'SIMULATED', 'COMPLETE', FALSE,
    'demo-tcs-cam1-traffic-decrease' || n
FROM generate_series(1, 6) AS n
ON CONFLICT (camera_id, zone_id, sampled_at) DO NOTHING;

-- ============================================================
-- 4. camera_links (요구사항 6-5절: 인접 카메라 교차검증)
-- ============================================================
INSERT INTO camera_links
    (upstream_camera_id, downstream_camera_id, direction,
     expected_travel_time_seconds, expected_flow_ratio, tolerance_ratio,
     enabled)
VALUES
    (1, 2, 'DOWNSTREAM', 120, 0.950000, 0.200000, TRUE),
    (2, 1, 'UPSTREAM',   120, 1.050000, 0.200000, TRUE),
    (2, 3, 'DOWNSTREAM',  90, 0.900000, 0.250000, TRUE),
    (3, 2, 'UPSTREAM',    90, 1.100000, 0.250000, TRUE)
ON CONFLICT (upstream_camera_id, downstream_camera_id, direction) DO NOTHING;

-- ============================================================
-- 5. anomaly_events
--    DO $$ 블록으로 활성 이벤트 중복 방지 (partial unique index 보조)
-- ============================================================

-- 시나리오 B: 카메라 2 FPS 악화 추세 (TREND_PROJECTION, WARNING, OPEN)
--   P2 조건: 10분 내 CRITICAL 도달 예측 (요구사항 7-2절)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM anomaly_events
        WHERE target_camera_id = 2
          AND anomaly_type = 'FPS_DEGRADATION'
          AND status IN ('OPEN','ACKNOWLEDGED','RECOVERED')
    ) THEN
        INSERT INTO anomaly_events
            (target_type, target_camera_id, anomaly_type, severity, status,
             detection_method, data_source, policy_id, detector_version_id,
             anomaly_score,
             baseline_source, baseline_from, baseline_to, baseline_sample_count,
             trend_slope, trend_confidence, prediction_horizon_minutes,
             projected_threshold_crossing_at,
             suspected_causes_json, recurrence_count,
             first_detected_at, last_detected_at, created_at, updated_at)
        VALUES (
            'CAMERA', 2, 'FPS_DEGRADATION', 'WARNING', 'OPEN',
            'TREND_PROJECTION', 'FAULT_INJECTED',
            (SELECT id FROM anomaly_policies WHERE policy_code = 'CAMERA_TREND_PROJECTION_V1'),
            (SELECT id FROM detector_versions WHERE detector_name = 'camera-trend-projection'),
            0.860000,
            'CAMERA_30_MINUTE_BUCKET_14D',
            (NOW() - '14 days'::INTERVAL)::TIMESTAMP,
            NOW()::TIMESTAMP,
            42,
            -0.330000, 0.810000, 10,
            (NOW() + '8 minutes'::INTERVAL)::TIMESTAMP,
            '[{"cause":"AI_PROCESSING_OVERLOAD","score":0.72},{"cause":"UNKNOWN","score":0.28}]'::jsonb,
            0,
            (NOW() - '30 minutes'::INTERVAL)::TIMESTAMP,
            (NOW() - '1 minutes'::INTERVAL)::TIMESTAMP,
            (NOW() - '30 minutes'::INTERVAL)::TIMESTAMP,
            NOW()::TIMESTAMP
        );
    END IF;
END $$;

-- 시나리오 C: 카메라 3 오프라인 (RULE, CRITICAL, ACKNOWLEDGED)
--   P1 티켓 + 작업 시작 SLA 초과 시나리오 (확인은 됐으나 아직 ASSIGNED)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM anomaly_events
        WHERE target_camera_id = 3
          AND anomaly_type = 'CAMERA_OFFLINE'
          AND status IN ('OPEN','ACKNOWLEDGED','RECOVERED')
    ) THEN
        INSERT INTO anomaly_events
            (target_type, target_camera_id, anomaly_type, severity, status,
             detection_method, data_source, policy_id, detector_version_id,
             anomaly_score,
             suspected_causes_json, recurrence_count,
             first_detected_at, last_detected_at,
             acknowledged_at, acknowledged_by,
             created_at, updated_at)
        VALUES (
            'CAMERA', 3, 'CAMERA_OFFLINE', 'CRITICAL', 'ACKNOWLEDGED',
            'RULE', 'FAULT_INJECTED',
            (SELECT id FROM anomaly_policies WHERE policy_code = 'CAMERA_OFFLINE_RULE_V1'),
            (SELECT id FROM detector_versions WHERE detector_name = 'camera-rule'),
            0.980000,
            '[{"cause":"CAMERA_POWER_OR_NETWORK","score":0.85},{"cause":"UNKNOWN","score":0.15}]'::jsonb,
            0,
            (NOW() - '40 minutes'::INTERVAL)::TIMESTAMP,
            (NOW() - '2 minutes'::INTERVAL)::TIMESTAMP,
            (NOW() - '35 minutes'::INTERVAL)::TIMESTAMP,
            (SELECT member_id FROM members WHERE role = 'OPERATOR' LIMIT 1),
            (NOW() - '40 minutes'::INTERVAL)::TIMESTAMP,
            NOW()::TIMESTAMP
        );
    END IF;
END $$;

-- 시나리오 D: 카메라 4 OCR 품질 저하 (RULE, WARNING, ACKNOWLEDGED)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM anomaly_events
        WHERE target_camera_id = 4
          AND anomaly_type = 'OCR_QUALITY_DEGRADATION'
          AND status IN ('OPEN','ACKNOWLEDGED','RECOVERED')
    ) THEN
        INSERT INTO anomaly_events
            (target_type, target_camera_id, anomaly_type, severity, status,
             detection_method, data_source, policy_id, detector_version_id,
             anomaly_score,
             suspected_causes_json, recurrence_count,
             first_detected_at, last_detected_at,
             acknowledged_at, acknowledged_by,
             created_at, updated_at)
        VALUES (
            'CAMERA', 4, 'OCR_QUALITY_DEGRADATION', 'WARNING', 'ACKNOWLEDGED',
            'RULE', 'FAULT_INJECTED',
            (SELECT id FROM anomaly_policies WHERE policy_code = 'OCR_QUALITY_DEGRADATION_RULE_V1'),
            (SELECT id FROM detector_versions WHERE detector_name = 'camera-rule'),
            0.540000,
            '[{"cause":"LOW_ILLUMINATION","score":0.70},{"cause":"OCR_PIPELINE_DEGRADATION","score":0.30}]'::jsonb,
            0,
            (NOW() - '30 minutes'::INTERVAL)::TIMESTAMP,
            (NOW() - '2 minutes'::INTERVAL)::TIMESTAMP,
            (NOW() - '25 minutes'::INTERVAL)::TIMESTAMP,
            (SELECT member_id FROM members WHERE role = 'OPERATOR' LIMIT 1),
            (NOW() - '30 minutes'::INTERVAL)::TIMESTAMP,
            NOW()::TIMESTAMP
        );
    END IF;
END $$;

-- 시나리오 F: OCR 품질 RESOLVED 이벤트 (P3 완료 이력 시연용)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM anomaly_events
        WHERE target_camera_id = 4
          AND anomaly_type = 'OCR_QUALITY_DEGRADATION'
          AND status = 'RESOLVED'
    ) THEN
        INSERT INTO anomaly_events
            (target_type, target_camera_id, anomaly_type, severity, status,
             detection_method, data_source, policy_id, detector_version_id,
             suspected_causes_json, recurrence_count,
             confirmed_cause, resolution_note,
             first_detected_at, last_detected_at,
             resolved_at, resolved_by,
             created_at, updated_at)
        VALUES (
            'CAMERA', 4, 'OCR_QUALITY_DEGRADATION', 'WARNING', 'RESOLVED',
            'RULE', 'SIMULATED',
            (SELECT id FROM anomaly_policies WHERE policy_code = 'OCR_QUALITY_DEGRADATION_RULE_V1'),
            (SELECT id FROM detector_versions WHERE detector_name = 'camera-rule'),
            '[{"cause":"CAMERA_LENS_OR_FOCUS","score":0.90}]'::jsonb,
            0,
            'CAMERA_LENS_OR_FOCUS',
            '렌즈 청소 및 포커스 재조정 완료. OCR 실패율 정상화 확인.',
            (NOW() - '3 hours'::INTERVAL)::TIMESTAMP,
            (NOW() - '2 hours'::INTERVAL)::TIMESTAMP,
            (NOW() - '1 hour'::INTERVAL)::TIMESTAMP,
            (SELECT member_id FROM members WHERE role = 'OPERATOR' LIMIT 1),
            (NOW() - '3 hours'::INTERVAL)::TIMESTAMP,
            NOW()::TIMESTAMP
        );
    END IF;
END $$;

-- ============================================================
-- 6. anomaly_event_evidence
--    ERD 3-7절: context_json에 adjacentTrafficNormal, sourceCameraIds 포함
--    API 계약서 3-6절 구조 반영
-- ============================================================

-- 시나리오 B (FPS 악화 추세) evidence
INSERT INTO anomaly_event_evidence
    (anomaly_event_id, metric_name,
     observed_value, baseline_value, threshold_value, metric_score,
     unit, sampled_at, context_json)
SELECT
    e.id,
    'fps_avg',
    8.40, 29.20, 10.00, -4.800000,
    'fps',
    (NOW() - '1 minutes'::INTERVAL)::TIMESTAMP,
    '{"direction":"LOWER_IS_WORSE","trendSlope":-0.33,"trendConfidence":0.81,"adjacentTrafficNormal":true,"sourceCameraIds":[1,3]}'::jsonb
FROM anomaly_events e
WHERE e.target_camera_id = 2
  AND e.anomaly_type = 'FPS_DEGRADATION'
  AND e.status IN ('OPEN','ACKNOWLEDGED','RECOVERED')
LIMIT 1
ON CONFLICT DO NOTHING;

-- 시나리오 C (오프라인) evidence
INSERT INTO anomaly_event_evidence
    (anomaly_event_id, metric_name,
     observed_value, baseline_value, threshold_value, metric_score,
     unit, sampled_at, context_json)
SELECT
    e.id,
    'last_frame_seconds_ago',
    900.00, NULL, 60.00, 0.980000,
    'seconds',
    (NOW() - '2 minutes'::INTERVAL)::TIMESTAMP,
    '{"offlineThresholdSeconds":60,"adjacentTrafficNormal":true,"sourceCameraIds":[2]}'::jsonb
FROM anomaly_events e
WHERE e.target_camera_id = 3
  AND e.anomaly_type = 'CAMERA_OFFLINE'
  AND e.status IN ('OPEN','ACKNOWLEDGED','RECOVERED')
LIMIT 1
ON CONFLICT DO NOTHING;

-- 시나리오 D (OCR 품질) evidence
INSERT INTO anomaly_event_evidence
    (anomaly_event_id, metric_name,
     observed_value, baseline_value, threshold_value, metric_score,
     unit, sampled_at, context_json)
SELECT
    e.id,
    'ocr_fail_rate',
    0.890000, 0.068000, 0.700000, 0.540000,
    'rate',
    (NOW() - '2 minutes'::INTERVAL)::TIMESTAMP,
    '{"direction":"HIGHER_IS_WORSE","consecutiveWindows":2,"ocrAttemptCount":40,"adjacentTrafficNormal":true,"sourceCameraIds":[3]}'::jsonb
FROM anomaly_events e
WHERE e.target_camera_id = 4
  AND e.anomaly_type = 'OCR_QUALITY_DEGRADATION'
  AND e.status IN ('OPEN','ACKNOWLEDGED','RECOVERED')
LIMIT 1
ON CONFLICT DO NOTHING;

-- ============================================================
-- 7. model_prediction_logs (LSTM AE SHADOW 추론)
--    요건: SHADOW 결과만으로 이벤트·티켓 생성 금지 (FR-ML-003)
--    API 계약서 5-3절: featureName/featureValue 키, feature_schema_version
--    어제 파일 반영: 점수가 시간순으로 증가하는 패턴 (0.25 → 0.89)
-- ============================================================

-- 카메라 2: 최근 30분 5분 간격 6개 — 이상 점수 점진 증가
INSERT INTO model_prediction_logs
    (camera_id, detector_version_id, evaluated_at,
     input_window_from, input_window_to,
     anomaly_score, warning_threshold, critical_threshold,
     predicted_anomaly, predicted_severity,
     data_source, quality_status,
     feature_schema_version, top_features_json)
SELECT
    2,
    (SELECT id FROM detector_versions WHERE detector_name = 'camera-lstm-autoencoder'),
    (NOW() - ((30 - n * 5) || ' minutes')::INTERVAL)::TIMESTAMP,
    (NOW() - ((90 - n * 5) || ' minutes')::INTERVAL)::TIMESTAMP,
    (NOW() - ((30 - n * 5) || ' minutes')::INTERVAL)::TIMESTAMP,
    LEAST(0.25 + n * 0.11, 1.0),
    0.410734,  0.462065,
    CASE WHEN LEAST(0.25 + n * 0.11, 1.0) >= 0.410734 THEN TRUE ELSE FALSE END,
    CASE
        WHEN LEAST(0.25 + n * 0.11, 1.0) >= 0.462065 THEN 'CRITICAL'
        WHEN LEAST(0.25 + n * 0.11, 1.0) >= 0.410734 THEN 'WARNING'
        ELSE NULL
    END,
    CASE WHEN n <= 3 THEN 'SIMULATED' ELSE 'FAULT_INJECTED' END,
    'COMPLETE',
    'camera-health-sequence-v1',
    ('[{"featureName":"fps_avg","featureValue":' || ROUND((0.10 + n * 0.08)::NUMERIC, 2) ||
     '},{"featureName":"cpu_usage_pct","featureValue":' || ROUND((0.05 + n * 0.04)::NUMERIC, 2) ||
     '},{"featureName":"frame_drop_rate","featureValue":' || ROUND((0.03 + n * 0.03)::NUMERIC, 2) ||
     '}]')::jsonb
FROM generate_series(1, 6) AS n
WHERE EXISTS (
    SELECT 1 FROM detector_versions WHERE detector_name = 'camera-lstm-autoencoder'
)
ON CONFLICT (camera_id, detector_version_id, evaluated_at) DO NOTHING;

-- 카메라 1: 정상 예측 (단일 로그)
INSERT INTO model_prediction_logs
    (camera_id, detector_version_id, evaluated_at,
     input_window_from, input_window_to,
     anomaly_score, warning_threshold, critical_threshold,
     predicted_anomaly, predicted_severity,
     data_source, quality_status,
     feature_schema_version, top_features_json)
SELECT
    1,
    (SELECT id FROM detector_versions WHERE detector_name = 'camera-lstm-autoencoder'),
    NOW()::TIMESTAMP,
    (NOW() - '60 minutes'::INTERVAL)::TIMESTAMP,
    NOW()::TIMESTAMP,
    0.183000,  0.410734,  0.462065,
    FALSE,  NULL,
    'SIMULATED', 'COMPLETE',
    'camera-health-sequence-v1',
    '[]'::jsonb
WHERE EXISTS (
    SELECT 1 FROM detector_versions WHERE detector_name = 'camera-lstm-autoencoder'
)
ON CONFLICT (camera_id, detector_version_id, evaluated_at) DO NOTHING;

-- ============================================================
-- 8. maintenance_tickets
--    요구사항 7-2절 SLA 기준
--    어제 파일 반영: P1 SLA 초과 시나리오 (시연용)
-- ============================================================

-- P1: 카메라 3 오프라인 (이벤트 발생 40분 전)
--   SLA: 확인 10분, 작업 시작 30분
--   → 확인은 완료됐지만 작업 시작 SLA가 10분 초과된 상태로 시연 가능
INSERT INTO maintenance_tickets
    (anomaly_event_id, ticket_number, priority, status,
     assignee_id,
     due_ack_at, due_start_at,
     acknowledged_at, started_at,
     action_note,
     created_by, created_at, updated_at)
SELECT
    e.id,
    'MNT-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-0001',
    'P1', 'ASSIGNED',
    (SELECT member_id FROM members WHERE role = 'MAINTAINER' LIMIT 1),
    -- 이벤트 발생(40분 전) + 10분 = 30분 전
    (NOW() - '40 minutes'::INTERVAL + '10 minutes'::INTERVAL)::TIMESTAMP,
    -- 이벤트 발생(40분 전) + 30분 = 10분 전 (작업 시작 SLA 초과)
    (NOW() - '40 minutes'::INTERVAL + '30 minutes'::INTERVAL)::TIMESTAMP,
    (NOW() - '35 minutes'::INTERVAL)::TIMESTAMP,
    NULL,
    '정비사 배정 완료. 작업 시작 대기 중.',
    (SELECT member_id FROM members WHERE role = 'OPERATOR' LIMIT 1),
    (NOW() - '40 minutes'::INTERVAL)::TIMESTAMP,
    NOW()::TIMESTAMP
FROM anomaly_events e
WHERE e.target_camera_id = 3
  AND e.anomaly_type = 'CAMERA_OFFLINE'
  AND e.status IN ('OPEN','ACKNOWLEDGED','RECOVERED')
LIMIT 1
ON CONFLICT (anomaly_event_id) DO NOTHING;

-- P2: 카메라 2 FPS 악화 추세 (이벤트 발생 30분 전)
--   SLA: 확인 30분(딱 마감), 작업 시작 2시간
INSERT INTO maintenance_tickets
    (anomaly_event_id, ticket_number, priority, status,
     due_ack_at, due_start_at,
     created_by, created_at, updated_at)
SELECT
    e.id,
    'MNT-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-0002',
    'P2', 'OPEN',
    (NOW() - '30 minutes'::INTERVAL + '30 minutes'::INTERVAL)::TIMESTAMP,
    (NOW() - '30 minutes'::INTERVAL + '2 hours'::INTERVAL)::TIMESTAMP,
    (SELECT member_id FROM members WHERE role = 'OPERATOR' LIMIT 1),
    (NOW() - '30 minutes'::INTERVAL)::TIMESTAMP,
    NOW()::TIMESTAMP
FROM anomaly_events e
WHERE e.target_camera_id = 2
  AND e.anomaly_type = 'FPS_DEGRADATION'
  AND e.status IN ('OPEN','ACKNOWLEDGED','RECOVERED')
LIMIT 1
ON CONFLICT (anomaly_event_id) DO NOTHING;

-- P3: OCR 품질 RESOLVED 이벤트 (완료 이력 시연용)
--   SLA: 확인 4시간, 작업 시작 8시간(1영업일)
INSERT INTO maintenance_tickets
    (anomaly_event_id, ticket_number, priority, status,
     assignee_id,
     due_ack_at, due_start_at,
     acknowledged_at, started_at, resolved_at,
     action_note,
     created_by, created_at, updated_at)
SELECT
    e.id,
    'MNT-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-0003',
    'P3', 'RESOLVED',
    (SELECT member_id FROM members WHERE role = 'MAINTAINER' LIMIT 1),
    (NOW() - '3 hours'::INTERVAL + '4 hours'::INTERVAL)::TIMESTAMP,
    (NOW() - '3 hours'::INTERVAL + '8 hours'::INTERVAL)::TIMESTAMP,
    (NOW() - '2 hours 50 minutes'::INTERVAL)::TIMESTAMP,
    (NOW() - '2 hours 30 minutes'::INTERVAL)::TIMESTAMP,
    (NOW() - '1 hour'::INTERVAL)::TIMESTAMP,
    '렌즈 청소 및 포커스 재조정 완료. OCR 실패율 정상 확인.',
    (SELECT member_id FROM members WHERE role = 'OPERATOR' LIMIT 1),
    (NOW() - '3 hours'::INTERVAL)::TIMESTAMP,
    NOW()::TIMESTAMP
FROM anomaly_events e
WHERE e.target_camera_id = 4
  AND e.anomaly_type = 'OCR_QUALITY_DEGRADATION'
  AND e.status = 'RESOLVED'
LIMIT 1
ON CONFLICT (anomaly_event_id) DO NOTHING;

-- ============================================================
-- 9. maintenance_ticket_histories (append-only)
--    요구사항 7-2절: 모든 상태 변경 이력 기록
--    API 계약서 3-13절: 상태 전이 권한 반영
-- ============================================================

-- P1 티켓: OPEN → ASSIGNED
INSERT INTO maintenance_ticket_histories
    (maintenance_ticket_id, from_status, to_status, changed_by, note, changed_at)
SELECT mt.id, NULL, 'OPEN',
    (SELECT member_id FROM members WHERE role = 'OPERATOR' LIMIT 1),
    '티켓 자동 생성 (CRITICAL — 카메라 3 오프라인)',
    (NOW() - '40 minutes'::INTERVAL)::TIMESTAMP
FROM maintenance_tickets mt WHERE mt.ticket_number LIKE '%-0001'
ON CONFLICT DO NOTHING;

INSERT INTO maintenance_ticket_histories
    (maintenance_ticket_id, from_status, to_status, changed_by, note, changed_at)
SELECT mt.id, 'OPEN', 'ASSIGNED',
    (SELECT member_id FROM members WHERE role = 'OPERATOR' LIMIT 1),
    '정비사 배정 완료',
    (NOW() - '35 minutes'::INTERVAL)::TIMESTAMP
FROM maintenance_tickets mt WHERE mt.ticket_number LIKE '%-0001'
ON CONFLICT DO NOTHING;

-- P2 티켓: OPEN
INSERT INTO maintenance_ticket_histories
    (maintenance_ticket_id, from_status, to_status, changed_by, note, changed_at)
SELECT mt.id, NULL, 'OPEN',
    (SELECT member_id FROM members WHERE role = 'OPERATOR' LIMIT 1),
    '티켓 자동 생성 (WARNING — 10분 내 CRITICAL 도달 예측)',
    (NOW() - '30 minutes'::INTERVAL)::TIMESTAMP
FROM maintenance_tickets mt WHERE mt.ticket_number LIKE '%-0002'
ON CONFLICT DO NOTHING;

-- P3 티켓: OPEN → ASSIGNED → IN_PROGRESS → RESOLVED
INSERT INTO maintenance_ticket_histories
    (maintenance_ticket_id, from_status, to_status, changed_by, note, changed_at)
SELECT mt.id, NULL, 'OPEN',
    (SELECT member_id FROM members WHERE role = 'OPERATOR' LIMIT 1),
    '수동 티켓 생성 (예방 점검 — 렌즈 청소 및 포커스 조정)',
    (NOW() - '3 hours'::INTERVAL)::TIMESTAMP
FROM maintenance_tickets mt WHERE mt.ticket_number LIKE '%-0003'
ON CONFLICT DO NOTHING;

INSERT INTO maintenance_ticket_histories
    (maintenance_ticket_id, from_status, to_status, changed_by, note, changed_at)
SELECT mt.id, 'OPEN', 'ASSIGNED',
    (SELECT member_id FROM members WHERE role = 'OPERATOR' LIMIT 1),
    '정비사 배정',
    (NOW() - '2 hours 50 minutes'::INTERVAL)::TIMESTAMP
FROM maintenance_tickets mt WHERE mt.ticket_number LIKE '%-0003'
ON CONFLICT DO NOTHING;

INSERT INTO maintenance_ticket_histories
    (maintenance_ticket_id, from_status, to_status, changed_by, note, changed_at)
SELECT mt.id, 'ASSIGNED', 'IN_PROGRESS',
    (SELECT member_id FROM members WHERE role = 'MAINTAINER' LIMIT 1),
    '현장 도착. 렌즈 청소 시작.',
    (NOW() - '2 hours 30 minutes'::INTERVAL)::TIMESTAMP
FROM maintenance_tickets mt WHERE mt.ticket_number LIKE '%-0003'
ON CONFLICT DO NOTHING;

INSERT INTO maintenance_ticket_histories
    (maintenance_ticket_id, from_status, to_status, changed_by, note, changed_at)
SELECT mt.id, 'IN_PROGRESS', 'RESOLVED',
    (SELECT member_id FROM members WHERE role = 'MAINTAINER' LIMIT 1),
    '렌즈 청소 및 포커스 재조정 완료. OCR 실패율 정상 확인.',
    (NOW() - '1 hour'::INTERVAL)::TIMESTAMP
FROM maintenance_tickets mt WHERE mt.ticket_number LIKE '%-0003'
ON CONFLICT DO NOTHING;

-- ============================================================
-- 10. ANALYZE (플래너 통계 갱신)
-- ============================================================
ANALYZE camera_health_samples;
ANALYZE traffic_context_samples;
ANALYZE anomaly_events;

COMMIT;

-- ============================================================
-- 11. 삽입 결과 확인 (어제 파일 반영)
-- ============================================================
SELECT '=== demo seed 적용 결과 ===' AS summary;

SELECT 'members (전체)'                        AS table_name, COUNT(*) AS row_count FROM members
UNION ALL
SELECT 'camera_health_samples (SIMULATED)',     COUNT(*) FROM camera_health_samples WHERE data_source = 'SIMULATED'
UNION ALL
SELECT 'camera_health_samples (FAULT_INJECTED)',COUNT(*) FROM camera_health_samples WHERE data_source = 'FAULT_INJECTED'
UNION ALL
SELECT 'traffic_context_samples',              COUNT(*) FROM traffic_context_samples
UNION ALL
SELECT 'camera_links',                         COUNT(*) FROM camera_links
UNION ALL
SELECT 'anomaly_events (SIMULATED)',           COUNT(*) FROM anomaly_events WHERE data_source = 'SIMULATED'
UNION ALL
SELECT 'anomaly_events (FAULT_INJECTED)',      COUNT(*) FROM anomaly_events WHERE data_source = 'FAULT_INJECTED'
UNION ALL
SELECT 'anomaly_event_evidence',               COUNT(*) FROM anomaly_event_evidence
UNION ALL
SELECT 'model_prediction_logs',                COUNT(*) FROM model_prediction_logs
UNION ALL
SELECT 'maintenance_tickets',                  COUNT(*) FROM maintenance_tickets
UNION ALL
SELECT 'maintenance_ticket_histories',         COUNT(*) FROM maintenance_ticket_histories;

