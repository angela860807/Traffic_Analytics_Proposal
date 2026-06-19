-- ============================================================
-- 008_predictive_seed_policies.sql
-- 초기 detector_versions & anomaly_policies 시드 데이터
-- ON CONFLICT DO NOTHING: 재실행 안전
-- 기준: 01_요구사항_정의서 6-2절
-- ============================================================

-- ------------------------------------------------------------
-- detector_versions 초기 등록
-- 비학습 detector(RULE 등): 학습 관련 컬럼 NULL
-- LSTM AE: 학습 완료 전이므로 EXPERIMENTAL
-- ------------------------------------------------------------
INSERT INTO detector_versions
    (detector_name, version, detection_method, operating_mode, active, created_at)
VALUES
    ('camera-rule',                    '1.1.0', 'RULE',             'ACTIVE',       TRUE,  NOW()),
    ('camera-robust-zscore',           '1.0.0', 'ROBUST_Z_SCORE',   'ACTIVE',       TRUE,  NOW()),
    ('camera-trend-projection',        '1.0.0', 'TREND_PROJECTION', 'ACTIVE',       TRUE,  NOW()),
    ('camera-context-cross-validator', '1.0.0', 'CROSS_VALIDATION', 'ACTIVE',       TRUE,  NOW()),
    ('camera-lstm-autoencoder',        '1.0.0', 'LSTM_AUTOENCODER', 'EXPERIMENTAL', FALSE, NOW())
ON CONFLICT (detector_name, version) DO NOTHING;

-- ------------------------------------------------------------
-- anomaly_policies 초기 등록
-- 컬럼 순서:
--   policy_code, anomaly_type, detection_method,
--   warning_threshold, critical_threshold, threshold_direction,
--   warning_consecutive_windows, critical_consecutive_windows,
--   minimum_sample_count, cooldown_minutes, config_json, enabled
-- ------------------------------------------------------------

-- [RULE] 카메라 오프라인
-- 마지막 프레임 60초 초과 시 즉시 이벤트
-- threshold 없음 (ON/OFF 이진 판단)
-- config_json: offlineThresholdSeconds 기준 명시
INSERT INTO anomaly_policies
    (policy_code, anomaly_type, detection_method,
     warning_threshold, critical_threshold, threshold_direction,
     warning_consecutive_windows, critical_consecutive_windows,
     minimum_sample_count, cooldown_minutes, config_json, enabled)
VALUES
    ('CAMERA_OFFLINE_RULE_V1', 'CAMERA_OFFLINE', 'RULE',
     NULL, NULL, 'HIGHER_IS_WORSE',
     1, 1,
     1, 5,
     '{"offlineThresholdSeconds": 60}'::jsonb,
     TRUE)
ON CONFLICT (policy_code) DO NOTHING;

-- [RULE] FPS 저하
-- FPS 낮을수록 위험 → LOWER_IS_WORSE
-- WARNING: 10fps 미만 3분 / CRITICAL: 5fps 미만 3분
INSERT INTO anomaly_policies
    (policy_code, anomaly_type, detection_method,
     warning_threshold, critical_threshold, threshold_direction,
     warning_consecutive_windows, critical_consecutive_windows,
     minimum_sample_count, cooldown_minutes, enabled)
VALUES
    ('FPS_DEGRADATION_RULE_V1', 'FPS_DEGRADATION', 'RULE',
     10.0, 5.0, 'LOWER_IS_WORSE',
     3, 3,
     3, 10, TRUE)
ON CONFLICT (policy_code) DO NOTHING;

-- [RULE] Frame Drop 저하
-- 비율 높을수록 위험 → HIGHER_IS_WORSE
-- WARNING: 0.30 초과 3분 / CRITICAL: 0.60 초과 3분
INSERT INTO anomaly_policies
    (policy_code, anomaly_type, detection_method,
     warning_threshold, critical_threshold, threshold_direction,
     warning_consecutive_windows, critical_consecutive_windows,
     minimum_sample_count, cooldown_minutes, enabled)
VALUES
    ('FRAME_DROP_DEGRADATION_RULE_V1', 'FRAME_DROP_DEGRADATION', 'RULE',
     0.30, 0.60, 'HIGHER_IS_WORSE',
     3, 3,
     3, 10, TRUE)
ON CONFLICT (policy_code) DO NOTHING;

-- [RULE] Latency 저하
-- 지연 높을수록 위험 → HIGHER_IS_WORSE
-- WARNING: p95 2,000ms 초과 3분 / CRITICAL: p95 5,000ms 초과 3분
INSERT INTO anomaly_policies
    (policy_code, anomaly_type, detection_method,
     warning_threshold, critical_threshold, threshold_direction,
     warning_consecutive_windows, critical_consecutive_windows,
     minimum_sample_count, cooldown_minutes, enabled)
VALUES
    ('LATENCY_DEGRADATION_RULE_V1', 'LATENCY_DEGRADATION', 'RULE',
     2000.0, 5000.0, 'HIGHER_IS_WORSE',
     3, 3,
     3, 10, TRUE)
ON CONFLICT (policy_code) DO NOTHING;

-- [RULE] Blur 저하
-- blur_score_avg: 높을수록 흐림 → HIGHER_IS_WORSE
-- WARNING: 0.75 초과 2분 / CRITICAL: 0.90 초과 2분
INSERT INTO anomaly_policies
    (policy_code, anomaly_type, detection_method,
     warning_threshold, critical_threshold, threshold_direction,
     warning_consecutive_windows, critical_consecutive_windows,
     minimum_sample_count, cooldown_minutes, enabled)
VALUES
    ('BLUR_DEGRADATION_RULE_V1', 'BLUR_DEGRADATION', 'RULE',
     0.75, 0.90, 'HIGHER_IS_WORSE',
     2, 2,
     2, 10, TRUE)
ON CONFLICT (policy_code) DO NOTHING;

-- [RULE] OCR 품질 저하
-- 실패율 높을수록 위험 → HIGHER_IS_WORSE
-- WARNING: 실패율 0.70 초과 2구간 / CRITICAL: 0.90 초과 2구간
-- minimum_sample_count=20: OCR 시도 20건 이상일 때만 판단 (요구사항 명시)
INSERT INTO anomaly_policies
    (policy_code, anomaly_type, detection_method,
     warning_threshold, critical_threshold, threshold_direction,
     warning_consecutive_windows, critical_consecutive_windows,
     minimum_sample_count, cooldown_minutes, enabled)
VALUES
    ('OCR_QUALITY_DEGRADATION_RULE_V1', 'OCR_QUALITY_DEGRADATION', 'RULE',
     0.70, 0.90, 'HIGHER_IS_WORSE',
     2, 2,
     20, 10, TRUE)
ON CONFLICT (policy_code) DO NOTHING;

-- [RULE] 자원 포화
-- 사용률 높을수록 위험 → HIGHER_IS_WORSE
-- WARNING: 85% 초과 5분 / CRITICAL: 95% 초과 3분
-- ※ warning/critical consecutive가 다름 (요구사항 명시)
INSERT INTO anomaly_policies
    (policy_code, anomaly_type, detection_method,
     warning_threshold, critical_threshold, threshold_direction,
     warning_consecutive_windows, critical_consecutive_windows,
     minimum_sample_count, cooldown_minutes, enabled)
VALUES
    ('RESOURCE_SATURATION_RULE_V1', 'RESOURCE_SATURATION', 'RULE',
     85.0, 95.0, 'HIGHER_IS_WORSE',
     5, 3,
     3, 10, TRUE)
ON CONFLICT (policy_code) DO NOTHING;

-- [RULE] 네트워크 불안정
-- RTT 높을수록 위험 → HIGHER_IS_WORSE
-- WARNING: RTT 500ms 초과 3분 / CRITICAL: RTT 1,000ms 초과 또는 프레임 단절
-- config_json: frameDisconnectAlsoCritical — 프레임 단절도 CRITICAL 처리
INSERT INTO anomaly_policies
    (policy_code, anomaly_type, detection_method,
     warning_threshold, critical_threshold, threshold_direction,
     warning_consecutive_windows, critical_consecutive_windows,
     minimum_sample_count, cooldown_minutes, config_json, enabled)
VALUES
    ('NETWORK_INSTABILITY_RULE_V1', 'NETWORK_INSTABILITY', 'RULE',
     500.0, 1000.0, 'HIGHER_IS_WORSE',
     3, 1,
     3, 10,
     '{"frameDisconnectAlsoCritical": true}'::jsonb,
     TRUE)
ON CONFLICT (policy_code) DO NOTHING;

-- [ROBUST_Z_SCORE] 카메라 통계 기준선 이상탐지
-- Z-score 높을수록 기준선에서 벗어남 → HIGHER_IS_WORSE
-- 기준선: 최근 14일, 30분 시간대 단위
-- consecutive 없음: 단일 평가로 판단
INSERT INTO anomaly_policies
    (policy_code, anomaly_type, detection_method,
     warning_threshold, critical_threshold, threshold_direction,
     minimum_sample_count, cooldown_minutes, config_json, enabled)
VALUES
    ('CAMERA_ROBUST_ZSCORE_V1', 'FPS_DEGRADATION', 'ROBUST_Z_SCORE',
     3.5, 5.0, 'HIGHER_IS_WORSE',
     30, 15,
     '{"baselineWindowDays": 14, "baselineBucketMinutes": 30}'::jsonb,
     TRUE)
ON CONFLICT (policy_code) DO NOTHING;

-- [TREND_PROJECTION] 추세 예측 이상탐지
-- FPS 추세 기준: 낮아지는 방향이 위험 → LOWER_IS_WORSE
-- 최근 15분 EWMA 추세로 향후 10분 임계치 도달 예측
-- consecutive 없음: 추세 계산 자체가 시간 구간 포함
INSERT INTO anomaly_policies
    (policy_code, anomaly_type, detection_method,
     warning_threshold, critical_threshold, threshold_direction,
     minimum_sample_count, prediction_horizon_minutes,
     cooldown_minutes, config_json, enabled)
VALUES
    ('CAMERA_TREND_PROJECTION_V1', 'FPS_DEGRADATION', 'TREND_PROJECTION',
     10.0, 5.0, 'LOWER_IS_WORSE',
     12, 10, 15,
     '{"windowMinutes": 15, "minimumValidSamples": 12, "ewmaAlpha": 0.3,
       "minimumTrendConfidence": 0.6, "predictionHorizonMinutes": 10}'::jsonb,
     TRUE)
ON CONFLICT (policy_code) DO NOTHING;

-- [CROSS_VALIDATION] 교통 맥락 교차검증
-- 임계값 없음: 인접 카메라와 비교하는 방식
-- consecutive 없음: 단일 구간 비교
INSERT INTO anomaly_policies
    (policy_code, anomaly_type, detection_method,
     cooldown_minutes, config_json, enabled)
VALUES
    ('TRAFFIC_CONTEXT_VALIDATION_V1', 'FPS_DEGRADATION', 'CROSS_VALIDATION',
     5,
     '{"adjacentCameraMinCount": 1, "flowDropThresholdPct": 0.5}'::jsonb,
     TRUE)
ON CONFLICT (policy_code) DO NOTHING;
