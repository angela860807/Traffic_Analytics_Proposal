-- ============================================================
-- 007_predictive_maintenance_schema.sql
-- 2차 TAS-PM 예지보전 신규 테이블
-- 기준: 01_요구사항_정의서, 02_ERD_설계서, 08_DB_작업_TODO
-- PostgreSQL 16 / 기존 001~006 마이그레이션 스타일 준수
-- ============================================================

-- ------------------------------------------------------------
-- camera_health_samples
-- 카메라·AI 처리 파이프라인의 1분 상태 스냅샷
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS camera_health_samples (
    id                      BIGSERIAL       PRIMARY KEY,
    camera_id               BIGINT          NOT NULL REFERENCES cameras(camera_id),
    processor_code          VARCHAR(50),
    sampled_at              TIMESTAMP       NOT NULL,
    sample_window_seconds   INTEGER         NOT NULL DEFAULT 60,

    fps_avg                 NUMERIC(7,2)    CHECK (fps_avg >= 0),
    frame_drop_rate         NUMERIC(7,6)    CHECK (frame_drop_rate BETWEEN 0 AND 1),
    latency_p95_ms          INTEGER,
    blur_score_avg          NUMERIC(7,6)    CHECK (blur_score_avg BETWEEN 0 AND 1),
    brightness_score_avg    NUMERIC(7,6)    CHECK (brightness_score_avg BETWEEN 0 AND 1),
    detection_count         INTEGER         CHECK (detection_count >= 0),
    ocr_attempt_count       INTEGER         CHECK (ocr_attempt_count >= 0),
    ocr_failure_count       INTEGER         CHECK (ocr_failure_count >= 0),
    ocr_fail_rate           NUMERIC(7,6)    CHECK (ocr_fail_rate BETWEEN 0 AND 1),
    cpu_usage_pct           NUMERIC(5,2)    CHECK (cpu_usage_pct BETWEEN 0 AND 100),
    memory_usage_pct        NUMERIC(5,2)    CHECK (memory_usage_pct BETWEEN 0 AND 100),
    disk_usage_pct          NUMERIC(5,2)    CHECK (disk_usage_pct BETWEEN 0 AND 100),
    network_rtt_ms          INTEGER,
    last_frame_at           TIMESTAMP,

    data_source             VARCHAR(50)     NOT NULL DEFAULT 'REAL'
                                CHECK (data_source IN ('REAL','OPEN_DATA','SIMULATED','FAULT_INJECTED','MOCK')),
    quality_status          VARCHAR(50)     NOT NULL DEFAULT 'COMPLETE'
                                CHECK (quality_status IN ('COMPLETE','PARTIAL','INSUFFICIENT')),
    is_imputed              BOOLEAN         NOT NULL DEFAULT FALSE,
    -- 10분 초과 지연 샘플: 저장하되 실시간 탐지에서는 제외 (요구사항 5-2)
    is_late_sample          BOOLEAN         NOT NULL DEFAULT FALSE,
    idempotency_key         VARCHAR(100)    NOT NULL,
    created_at              TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_camera_health_samples_camera_sampled UNIQUE (camera_id, sampled_at),
    CONSTRAINT uq_camera_health_samples_idempotency    UNIQUE (idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_camera_health_samples_camera_sampled
    ON camera_health_samples (camera_id, sampled_at DESC);
CREATE INDEX IF NOT EXISTS idx_camera_health_samples_quality_sampled
    ON camera_health_samples (quality_status, sampled_at DESC);
CREATE INDEX IF NOT EXISTS idx_camera_health_samples_datasource_sampled
    ON camera_health_samples (data_source, sampled_at DESC);

-- ------------------------------------------------------------
-- traffic_context_samples
-- 5분 단위 교통 흐름 집계 (CCTV 이상 교차검증용)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS traffic_context_samples (
    id                          BIGSERIAL       PRIMARY KEY,
    camera_id                   BIGINT          NOT NULL REFERENCES cameras(camera_id),
    zone_id                     BIGINT          NOT NULL REFERENCES zones(zone_id),
    sampled_at                  TIMESTAMP       NOT NULL,
    window_minutes              INTEGER         NOT NULL DEFAULT 5
                                    CHECK (window_minutes = 5),
    vehicle_count               INTEGER         CHECK (vehicle_count >= 0),
    avg_speed_kmh               NUMERIC(7,2),
    speed_measurement_count     INTEGER         CHECK (speed_measurement_count >= 0),
    speed_violation_count       INTEGER         CHECK (speed_violation_count >= 0),
    ocr_attempt_count           INTEGER         CHECK (ocr_attempt_count >= 0),
    ocr_success_count           INTEGER         CHECK (ocr_success_count >= 0),
    ocr_failure_count           INTEGER         CHECK (ocr_failure_count >= 0),
    in_count                    INTEGER         CHECK (in_count >= 0),
    out_count                   INTEGER         CHECK (out_count >= 0),

    data_source                 VARCHAR(50)     NOT NULL DEFAULT 'REAL'
                                    CHECK (data_source IN ('REAL','OPEN_DATA','SIMULATED','FAULT_INJECTED','MOCK')),
    quality_status              VARCHAR(50)     NOT NULL DEFAULT 'COMPLETE'
                                    CHECK (quality_status IN ('COMPLETE','PARTIAL','INSUFFICIENT')),
    is_imputed                  BOOLEAN         NOT NULL DEFAULT FALSE,
    source_from_flow_event_id   BIGINT          REFERENCES vehicle_flow_events(flow_event_id),
    source_to_flow_event_id     BIGINT          REFERENCES vehicle_flow_events(flow_event_id),
    idempotency_key             VARCHAR(100)    NOT NULL,
    created_at                  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_traffic_context_camera_zone_sampled
        UNIQUE (camera_id, zone_id, sampled_at),
    CONSTRAINT uq_traffic_context_idempotency
        UNIQUE (idempotency_key),
    CONSTRAINT chk_traffic_context_ocr_counts
        CHECK (ocr_success_count + ocr_failure_count <= ocr_attempt_count)
);

CREATE INDEX IF NOT EXISTS idx_traffic_context_samples_camera_sampled
    ON traffic_context_samples (camera_id, sampled_at DESC);
CREATE INDEX IF NOT EXISTS idx_traffic_context_samples_zone_sampled
    ON traffic_context_samples (zone_id, sampled_at DESC);
CREATE INDEX IF NOT EXISTS idx_traffic_context_samples_datasource_sampled
    ON traffic_context_samples (data_source, sampled_at DESC);

-- ------------------------------------------------------------
-- camera_links
-- 인접 카메라 방향·예상 이동 시간·정상 흐름 비율
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS camera_links (
    id                           BIGSERIAL       PRIMARY KEY,
    upstream_camera_id           BIGINT          NOT NULL REFERENCES cameras(camera_id),
    downstream_camera_id         BIGINT          NOT NULL REFERENCES cameras(camera_id),
    direction                    VARCHAR(50)     NOT NULL,
    expected_travel_time_seconds INTEGER         NOT NULL CHECK (expected_travel_time_seconds > 0),
    expected_flow_ratio          NUMERIC(7,6)    CHECK (expected_flow_ratio BETWEEN 0 AND 2),
    tolerance_ratio              NUMERIC(7,6)    CHECK (tolerance_ratio BETWEEN 0 AND 1),
    enabled                      BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at                   TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                   TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_camera_links_upstream_downstream_direction
        UNIQUE (upstream_camera_id, downstream_camera_id, direction),
    CONSTRAINT chk_camera_links_no_self_loop
        CHECK (upstream_camera_id <> downstream_camera_id)
);

-- ------------------------------------------------------------
-- anomaly_policies
-- 이상탐지 정책 정의
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS anomaly_policies (
    id                          BIGSERIAL       PRIMARY KEY,
    policy_code                 VARCHAR(100)    NOT NULL,
    anomaly_type                VARCHAR(100)    NOT NULL
                                    CHECK (anomaly_type IN (
                                        'CAMERA_OFFLINE','FPS_DEGRADATION','FRAME_DROP_DEGRADATION',
                                        'LATENCY_DEGRADATION','BLUR_DEGRADATION',
                                        'OCR_QUALITY_DEGRADATION','RESOURCE_SATURATION',
                                        'NETWORK_INSTABILITY')),
    detection_method            VARCHAR(50)     NOT NULL
                                    CHECK (detection_method IN (
                                        'RULE','ROBUST_Z_SCORE','TREND_PROJECTION',
                                        'CROSS_VALIDATION','LSTM_AUTOENCODER')),
    warning_threshold           NUMERIC(12,6),
    critical_threshold          NUMERIC(12,6),
    -- 임계값 방향: 값이 높을수록 위험(HIGHER_IS_WORSE) / 낮을수록 위험(LOWER_IS_WORSE)
    threshold_direction         VARCHAR(20)     NOT NULL DEFAULT 'HIGHER_IS_WORSE'
                                    CHECK (threshold_direction IN ('HIGHER_IS_WORSE','LOWER_IS_WORSE')),
    -- WARNING/CRITICAL 연속 위반 횟수 분리 (RESOURCE_SATURATION처럼 다를 수 있음)
    warning_consecutive_windows  INTEGER,  -- WARNING 발동 연속 위반 횟수
    critical_consecutive_windows INTEGER,  -- CRITICAL 발동 연속 위반 횟수
    minimum_sample_count         INTEGER,
    prediction_horizon_minutes  INTEGER         CHECK (prediction_horizon_minutes > 0),
    cooldown_minutes            INTEGER,
    config_json                 JSONB           NOT NULL DEFAULT '{}',
    enabled                     BOOLEAN         NOT NULL DEFAULT TRUE,
    updated_by                  BIGINT          REFERENCES members(member_id),
    created_at                  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_anomaly_policies_policy_code
        UNIQUE (policy_code),
    CONSTRAINT chk_anomaly_policies_threshold_order
        CHECK (
            warning_threshold IS NULL
            OR critical_threshold IS NULL
            OR (threshold_direction = 'HIGHER_IS_WORSE' AND warning_threshold < critical_threshold)
            OR (threshold_direction = 'LOWER_IS_WORSE'  AND warning_threshold > critical_threshold)
        )
);

-- ------------------------------------------------------------
-- detector_versions
-- 탐지 모델 버전 관리
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS detector_versions (
    id                      BIGSERIAL       PRIMARY KEY,
    detector_name           VARCHAR(100)    NOT NULL,
    version                 VARCHAR(20)     NOT NULL,
    detection_method        VARCHAR(50)     NOT NULL
                                CHECK (detection_method IN (
                                    'RULE','ROBUST_Z_SCORE','TREND_PROJECTION',
                                    'CROSS_VALIDATION','LSTM_AUTOENCODER')),
    -- 학습 모델 전용 필드 (비학습 detector는 NULL)
    model_format            VARCHAR(20),    -- pt, pkl, onnx 등
    artifact_path           VARCHAR(500),
    artifact_sha256         VARCHAR(64),    -- 모델 파일 무결성 검증
    feature_schema_version  VARCHAR(20),    -- 입력 feature 스키마 버전
    dataset_version         VARCHAR(50),    -- 학습 데이터셋 버전
    config_hash             VARCHAR(64),
    metrics_json            JSONB           NOT NULL DEFAULT '{}',
    -- ACTIVE: 실제 알람 발생 / SHADOW: 로그만 기록 / EXPERIMENTAL: 학습 미완료
    operating_mode          VARCHAR(20)     NOT NULL DEFAULT 'SHADOW'
                                CHECK (operating_mode IN ('ACTIVE','SHADOW','EXPERIMENTAL')),
    active                  BOOLEAN         NOT NULL DEFAULT FALSE,
    trained_at              TIMESTAMP,
    created_at              TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_detector_versions_name_version UNIQUE (detector_name, version)
);

-- ------------------------------------------------------------
-- anomaly_events
-- 이상 감지 이벤트 원장
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS anomaly_events (
    id                              BIGSERIAL       PRIMARY KEY,
    target_type                     VARCHAR(50)     NOT NULL DEFAULT 'CAMERA'
                                        CHECK (target_type = 'CAMERA'),
    target_camera_id                BIGINT          NOT NULL REFERENCES cameras(camera_id),
    anomaly_type                    VARCHAR(100)    NOT NULL
                                        CHECK (anomaly_type IN (
                                            'CAMERA_OFFLINE','FPS_DEGRADATION','FRAME_DROP_DEGRADATION',
                                            'LATENCY_DEGRADATION','BLUR_DEGRADATION',
                                            'OCR_QUALITY_DEGRADATION','RESOURCE_SATURATION',
                                            'NETWORK_INSTABILITY')),
    severity                        VARCHAR(50)     NOT NULL
                                        CHECK (severity IN ('WARNING','CRITICAL')),
    status                          VARCHAR(50)     NOT NULL DEFAULT 'OPEN'
                                        CHECK (status IN ('OPEN','ACKNOWLEDGED','RECOVERED','RESOLVED','DISMISSED')),
    detection_method                VARCHAR(50)     NOT NULL
                                        CHECK (detection_method IN (
                                            'RULE','ROBUST_Z_SCORE','TREND_PROJECTION',
                                            'CROSS_VALIDATION','LSTM_AUTOENCODER')),
    data_source                     VARCHAR(50)     NOT NULL DEFAULT 'REAL'
                                        CHECK (data_source IN ('REAL','OPEN_DATA','SIMULATED','FAULT_INJECTED','MOCK')),
    policy_id                       BIGINT          REFERENCES anomaly_policies(id),
    detector_version_id             BIGINT          REFERENCES detector_versions(id),

    anomaly_score                   NUMERIC(12,6)   CHECK (anomaly_score BETWEEN 0 AND 1),
    baseline_source                 VARCHAR(100),
    baseline_from                   TIMESTAMP,
    baseline_to                     TIMESTAMP,
    baseline_sample_count           INTEGER,
    trend_slope                     NUMERIC(12,6),
    trend_confidence                NUMERIC(7,6)    CHECK (trend_confidence BETWEEN 0 AND 1),
    prediction_horizon_minutes      INTEGER         CHECK (prediction_horizon_minutes > 0),
    projected_threshold_crossing_at TIMESTAMP,
    suspected_causes_json           JSONB           NOT NULL DEFAULT '[]',
    confirmed_cause                 VARCHAR(100)
                                        CHECK (confirmed_cause IN (
                                            'CAMERA_POWER_OR_NETWORK','CAMERA_LENS_OR_FOCUS',
                                            'LOW_ILLUMINATION','AI_PROCESSING_OVERLOAD',
                                            'OCR_PIPELINE_DEGRADATION','NETWORK_CONGESTION',
                                            'EXTERNAL_TRAFFIC_CHANGE','INSUFFICIENT_DATA','UNKNOWN')),
    resolution_note                 TEXT,
    recurrence_count                INTEGER         NOT NULL DEFAULT 0
                                        CHECK (recurrence_count >= 0),

    first_detected_at               TIMESTAMP       NOT NULL,
    last_detected_at                TIMESTAMP       NOT NULL,
    recovered_at                    TIMESTAMP,
    resolved_at                     TIMESTAMP,
    acknowledged_at                 TIMESTAMP,
    acknowledged_by                 BIGINT          REFERENCES members(member_id),
    resolved_by                     BIGINT          REFERENCES members(member_id),
    created_at                      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 동일 카메라·이상유형의 활성 이벤트 중복 방지
CREATE UNIQUE INDEX IF NOT EXISTS ux_anomaly_events_active
    ON anomaly_events (target_camera_id, anomaly_type)
    WHERE status IN ('OPEN', 'ACKNOWLEDGED', 'RECOVERED');

CREATE INDEX IF NOT EXISTS idx_anomaly_events_camera_status
    ON anomaly_events (target_camera_id, status);
CREATE INDEX IF NOT EXISTS idx_anomaly_events_status_severity_time
    ON anomaly_events (status, severity, first_detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_anomaly_events_first_detected
    ON anomaly_events (first_detected_at DESC);

-- ------------------------------------------------------------
-- anomaly_event_evidence
-- 이상 이벤트 판단 근거 (지표별 행 단위)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS anomaly_event_evidence (
    id                  BIGSERIAL       PRIMARY KEY,
    anomaly_event_id    BIGINT          NOT NULL REFERENCES anomaly_events(id),
    metric_name         VARCHAR(50)     NOT NULL,
    observed_value      NUMERIC(12,6),
    baseline_value      NUMERIC(12,6),
    threshold_value     NUMERIC(12,6),
    metric_score        NUMERIC(12,6),
    unit                VARCHAR(20),
    sampled_at          TIMESTAMP,
    context_json        JSONB           NOT NULL DEFAULT '{}',
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anomaly_event_evidence_event_id
    ON anomaly_event_evidence (anomaly_event_id, sampled_at DESC);

-- ------------------------------------------------------------
-- model_prediction_logs
-- LSTM AE SHADOW 모드 예측 로그
-- anomaly_score 기준(0~1): warning_threshold < critical_threshold 항상 성립
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS model_prediction_logs (
    id                      BIGSERIAL       PRIMARY KEY,
    camera_id               BIGINT          NOT NULL REFERENCES cameras(camera_id),
    detector_version_id     BIGINT          NOT NULL REFERENCES detector_versions(id),
    evaluated_at            TIMESTAMP       NOT NULL,
    input_window_from       TIMESTAMP       NOT NULL,
    input_window_to         TIMESTAMP       NOT NULL,
    anomaly_score           NUMERIC(7,6)    CHECK (anomaly_score BETWEEN 0 AND 1),
    warning_threshold       NUMERIC(7,6)    CHECK (warning_threshold BETWEEN 0 AND 1),
    critical_threshold      NUMERIC(7,6)    CHECK (critical_threshold BETWEEN 0 AND 1),
    -- predicted_anomaly=FALSE이면 predicted_severity는 반드시 NULL
    predicted_anomaly       BOOLEAN         NOT NULL DEFAULT FALSE,
    predicted_severity      VARCHAR(20)     CHECK (predicted_severity IN ('WARNING','CRITICAL')),
    data_source             VARCHAR(50)     NOT NULL DEFAULT 'REAL'
                                CHECK (data_source IN ('REAL','OPEN_DATA','SIMULATED','FAULT_INJECTED','MOCK')),
    quality_status          VARCHAR(50)     NOT NULL DEFAULT 'COMPLETE'
                                CHECK (quality_status IN ('COMPLETE','PARTIAL','INSUFFICIENT')),
    feature_schema_version  VARCHAR(20),
    top_features_json       JSONB           NOT NULL DEFAULT '[]',
    created_at              TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_model_prediction_logs_camera_detector_evaluated
        UNIQUE (camera_id, detector_version_id, evaluated_at),
    CONSTRAINT chk_model_prediction_logs_window
        CHECK (input_window_from < input_window_to),
    CONSTRAINT chk_model_prediction_logs_threshold_order
        CHECK (warning_threshold IS NULL OR critical_threshold IS NULL
               OR warning_threshold < critical_threshold),
    -- predicted_anomaly=FALSE이면 severity는 NULL이어야 함
    CONSTRAINT chk_model_prediction_logs_severity
        CHECK (predicted_anomaly = TRUE OR predicted_severity IS NULL)
);

CREATE INDEX IF NOT EXISTS idx_model_prediction_logs_camera_evaluated
    ON model_prediction_logs (camera_id, evaluated_at DESC);
CREATE INDEX IF NOT EXISTS idx_model_prediction_logs_detector_evaluated
    ON model_prediction_logs (detector_version_id, evaluated_at DESC);
CREATE INDEX IF NOT EXISTS idx_model_prediction_logs_predicted_anomaly
    ON model_prediction_logs (predicted_anomaly, evaluated_at DESC);

-- ------------------------------------------------------------
-- maintenance_tickets
-- 정비 티켓 (이벤트 1개당 티켓 1개)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS maintenance_tickets (
    id                  BIGSERIAL       PRIMARY KEY,
    anomaly_event_id    BIGINT          NOT NULL REFERENCES anomaly_events(id),
    ticket_number       VARCHAR(30)     NOT NULL,
    priority            VARCHAR(10)     NOT NULL
                            CHECK (priority IN ('P1','P2','P3')),
    status              VARCHAR(50)     NOT NULL DEFAULT 'OPEN'
                            CHECK (status IN ('OPEN','ASSIGNED','IN_PROGRESS','RESOLVED','CLOSED')),
    assignee_id         BIGINT          REFERENCES members(member_id),
    due_ack_at          TIMESTAMP,
    due_start_at        TIMESTAMP,
    acknowledged_at     TIMESTAMP,
    started_at          TIMESTAMP,
    resolved_at         TIMESTAMP,
    closed_at           TIMESTAMP,
    action_note         TEXT,
    created_by          BIGINT          REFERENCES members(member_id),
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_maintenance_tickets_anomaly_event UNIQUE (anomaly_event_id),
    CONSTRAINT uq_maintenance_tickets_ticket_number UNIQUE (ticket_number)
);

CREATE SEQUENCE IF NOT EXISTS maintenance_ticket_number_seq;

CREATE INDEX IF NOT EXISTS idx_maintenance_tickets_status_priority
    ON maintenance_tickets (status, priority);
CREATE INDEX IF NOT EXISTS idx_maintenance_tickets_assignee
    ON maintenance_tickets (assignee_id)
    WHERE status NOT IN ('RESOLVED','CLOSED');
CREATE INDEX IF NOT EXISTS idx_maintenance_tickets_due_ack
    ON maintenance_tickets (due_ack_at)
    WHERE status IN ('OPEN','ASSIGNED');

-- ------------------------------------------------------------
-- maintenance_ticket_histories
-- 정비 티켓 변경 이력 (append-only, 수정·삭제 없음)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS maintenance_ticket_histories (
    id                      BIGSERIAL       PRIMARY KEY,
    maintenance_ticket_id   BIGINT          NOT NULL REFERENCES maintenance_tickets(id),
    from_status             VARCHAR(50),
    to_status               VARCHAR(50)     NOT NULL,
    changed_by              BIGINT          REFERENCES members(member_id),
    note                    TEXT,
    changed_at              TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_maintenance_ticket_histories_ticket_id
    ON maintenance_ticket_histories (maintenance_ticket_id, changed_at DESC);
