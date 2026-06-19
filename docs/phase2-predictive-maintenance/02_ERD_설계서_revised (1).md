# TAS 2차 프로젝트 ERD 설계서

## 1. 설계 원칙

- 기존 `cameras`, `zones`, `vehicle_flow_events`, `detection_analysis_results`, `speed_violations`, `members`를 재사용한다.
- 정비 대상은 CCTV와 영상·AI 처리 파이프라인으로 한정한다.
- 교통 데이터는 `traffic_context_samples`에 저장하고 CCTV 이상 판별의 보조 근거로 사용한다.
- 원천 데이터, 집계 데이터, 이상 이벤트, 정비 업무를 분리한다.
- API는 JPA Entity를 직접 반환하지 않고 DTO로 변환한다.
- 신규 스키마는 기존 저장소 규칙의 번호형 PostgreSQL migration SQL로 관리한다.
- DBMS 기준은 Docker Compose의 PostgreSQL 16이다.
- PK는 기존 001~006 schema와 호환되는 `BIGSERIAL`을 사용한다.
- 업무 Enum은 PostgreSQL native enum 대신 `VARCHAR + CHECK`로 관리해 Java Enum과 migration 변경을 단순화한다.
- 시간은 기존 프로젝트 전체와 일관성을 위해 `TIMESTAMP + LocalDateTime`을 사용한다.
- 가변 근거 데이터는 `JSONB`를 사용한다.
- `JSONB` GIN index는 실제 검색 조건으로 사용하는 컬럼에만 생성한다.
- `CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`로 재실행 안전성을 보장한다.

## 2. ERD

```mermaid
erDiagram
    ZONES ||--o{ CAMERAS : contains
    CAMERAS ||--o{ VEHICLE_FLOW_EVENTS : produces
    CAMERAS ||--o{ DETECTION_ANALYSIS_RESULTS : produces
    VEHICLE_FLOW_EVENTS ||--o| SPEED_VIOLATIONS : may_create

    CAMERAS ||--o{ CAMERA_HEALTH_SAMPLES : sampled
    CAMERAS ||--o{ TRAFFIC_CONTEXT_SAMPLES : contextualizes
    ZONES ||--o{ TRAFFIC_CONTEXT_SAMPLES : groups
    CAMERAS ||--o{ CAMERA_LINKS : upstream
    CAMERAS ||--o{ CAMERA_LINKS : downstream

    DETECTOR_VERSIONS ||--o{ ANOMALY_EVENTS : generated_by
    DETECTOR_VERSIONS ||--o{ MODEL_PREDICTION_LOGS : predicts
    ANOMALY_POLICIES ||--o{ ANOMALY_EVENTS : applies
    MEMBERS ||--o{ ANOMALY_POLICIES : updated_by
    CAMERAS ||--o{ ANOMALY_EVENTS : maintenance_target
    CAMERAS ||--o{ MODEL_PREDICTION_LOGS : scored
    ANOMALY_EVENTS ||--o{ ANOMALY_EVENT_EVIDENCE : contains
    ANOMALY_EVENTS ||--o| MAINTENANCE_TICKETS : creates
    MEMBERS ||--o{ MAINTENANCE_TICKETS : assigned
    MEMBERS ||--o{ MAINTENANCE_TICKETS : created_by
    MEMBERS ||--o{ ANOMALY_EVENTS : acknowledged_by
    MEMBERS ||--o{ ANOMALY_EVENTS : resolved_by
    MAINTENANCE_TICKETS ||--o{ MAINTENANCE_TICKET_HISTORIES : records
    MEMBERS ||--o{ MAINTENANCE_TICKET_HISTORIES : changed_by

    CAMERA_HEALTH_SAMPLES {
        bigint id PK
        bigint camera_id FK
        varchar processor_code
        timestamp sampled_at
        integer sample_window_seconds
        numeric fps_avg
        numeric frame_drop_rate
        integer latency_p95_ms
        numeric blur_score_avg
        numeric brightness_score_avg
        integer detection_count
        integer ocr_attempt_count
        integer ocr_failure_count
        numeric ocr_fail_rate
        numeric cpu_usage_pct
        numeric memory_usage_pct
        numeric disk_usage_pct
        integer network_rtt_ms
        timestamp last_frame_at
        varchar data_source
        varchar quality_status
        boolean is_imputed
        boolean is_late_sample
        varchar idempotency_key UK
        timestamp created_at
    }

    TRAFFIC_CONTEXT_SAMPLES {
        bigint id PK
        bigint camera_id FK
        bigint zone_id FK
        timestamp sampled_at
        integer window_minutes
        integer vehicle_count
        numeric avg_speed_kmh
        integer speed_measurement_count
        integer speed_violation_count
        integer ocr_attempt_count
        integer ocr_success_count
        integer ocr_failure_count
        integer in_count
        integer out_count
        varchar data_source
        varchar quality_status
        boolean is_imputed
        bigint source_from_flow_event_id FK
        bigint source_to_flow_event_id FK
        varchar idempotency_key UK
        timestamp created_at
        timestamp updated_at
    }

    CAMERA_LINKS {
        bigint id PK
        bigint upstream_camera_id FK
        bigint downstream_camera_id FK
        varchar direction
        integer expected_travel_time_seconds
        numeric expected_flow_ratio
        numeric tolerance_ratio
        boolean enabled
        timestamp created_at
        timestamp updated_at
    }

    ANOMALY_POLICIES {
        bigint id PK
        varchar policy_code UK
        varchar anomaly_type
        varchar detection_method
        numeric warning_threshold
        numeric critical_threshold
        varchar threshold_direction
        integer warning_consecutive_windows
        integer critical_consecutive_windows
        integer minimum_sample_count
        integer prediction_horizon_minutes
        integer cooldown_minutes
        jsonb config_json
        boolean enabled
        bigint updated_by FK
        timestamp created_at
        timestamp updated_at
    }

    DETECTOR_VERSIONS {
        bigint id PK
        varchar detector_name
        varchar version
        varchar detection_method
        varchar operating_mode
        varchar model_format
        varchar artifact_path
        varchar artifact_sha256
        varchar feature_schema_version
        varchar dataset_version
        varchar config_hash
        jsonb metrics_json
        boolean active
        timestamp trained_at
        timestamp created_at
    }

    ANOMALY_EVENTS {
        bigint id PK
        varchar target_type
        bigint target_camera_id FK
        varchar anomaly_type
        varchar severity
        varchar status
        varchar detection_method
        varchar data_source
        bigint policy_id FK
        bigint detector_version_id FK
        numeric anomaly_score
        varchar baseline_source
        timestamp baseline_from
        timestamp baseline_to
        integer baseline_sample_count
        numeric trend_slope
        numeric trend_confidence
        integer prediction_horizon_minutes
        timestamp projected_threshold_crossing_at
        jsonb suspected_causes_json
        varchar confirmed_cause
        text resolution_note
        integer recurrence_count
        timestamp first_detected_at
        timestamp last_detected_at
        timestamp recovered_at
        timestamp resolved_at
        timestamp acknowledged_at
        bigint acknowledged_by FK
        bigint resolved_by FK
        timestamp created_at
        timestamp updated_at
    }

    ANOMALY_EVENT_EVIDENCE {
        bigint id PK
        bigint anomaly_event_id FK
        varchar metric_name
        numeric observed_value
        numeric baseline_value
        numeric threshold_value
        numeric metric_score
        varchar unit
        timestamp sampled_at
        jsonb context_json
        timestamp created_at
    }

    MODEL_PREDICTION_LOGS {
        bigint id PK
        bigint camera_id FK
        bigint detector_version_id FK
        timestamp evaluated_at
        timestamp input_window_from
        timestamp input_window_to
        numeric anomaly_score
        numeric warning_threshold
        numeric critical_threshold
        boolean predicted_anomaly
        varchar predicted_severity
        varchar data_source
        varchar quality_status
        varchar feature_schema_version
        jsonb top_features_json
        timestamp created_at
    }

    MAINTENANCE_TICKETS {
        bigint id PK
        bigint anomaly_event_id FK_UK
        varchar ticket_number UK
        varchar priority
        varchar status
        bigint assignee_id FK
        timestamp due_ack_at
        timestamp due_start_at
        timestamp acknowledged_at
        timestamp started_at
        timestamp resolved_at
        timestamp closed_at
        text action_note
        bigint created_by FK
        timestamp created_at
        timestamp updated_at
    }

    MAINTENANCE_TICKET_HISTORIES {
        bigint id PK
        bigint maintenance_ticket_id FK
        varchar from_status
        varchar to_status
        bigint changed_by FK
        text note
        timestamp changed_at
    }
```

## 3. 신규 테이블 계약

### 3-1. `camera_health_samples`

카메라와 AI 처리 프로세스의 1분 상태를 저장한다.

```text
UNIQUE(camera_id, sampled_at)
UNIQUE(idempotency_key)
fps_avg >= 0
0 <= frame_drop_rate <= 1
0 <= blur_score_avg <= 1
0 <= brightness_score_avg <= 1
0 <= ocr_fail_rate <= 1
0 <= cpu_usage_pct <= 100
0 <= memory_usage_pct <= 100
0 <= disk_usage_pct <= 100
is_late_sample: 10분 초과 지연 샘플 표시 (저장하되 실시간 탐지 제외)
```

인덱스:

```text
(camera_id, sampled_at DESC)
(quality_status, sampled_at DESC)
(data_source, sampled_at DESC)
```

멱등 저장:

```sql
INSERT INTO camera_health_samples (...)
VALUES (...)
ON CONFLICT (camera_id, sampled_at)
DO UPDATE SET
  fps_avg = EXCLUDED.fps_avg,
  frame_drop_rate = EXCLUDED.frame_drop_rate,
  latency_p95_ms = EXCLUDED.latency_p95_ms,
  quality_status = EXCLUDED.quality_status;
```

### 3-2. `traffic_context_samples`

기존 차량, OCR, 과속 데이터를 5분 단위로 집계한다. 혼잡 정비 이벤트가 아니라 CCTV 이상 원인 교차검증에 사용한다.

```text
UNIQUE(camera_id, zone_id, sampled_at)
UNIQUE(idempotency_key)
window_minutes = 5
vehicle_count >= 0
speed_violation_count >= 0
ocr_success_count + ocr_failure_count <= ocr_attempt_count
```

인덱스:

```text
(camera_id, sampled_at DESC)
(zone_id, sampled_at DESC)
(data_source, sampled_at DESC)
```

동일 5분 구간의 재집계는 `ON CONFLICT (camera_id, zone_id, sampled_at) DO UPDATE`로 처리한다.

### 3-3. `camera_links`

인접 카메라의 방향, 예상 이동 시간, 정상 흐름 비율을 정의한다.

```text
UNIQUE(upstream_camera_id, downstream_camera_id, direction)
upstream_camera_id <> downstream_camera_id
expected_travel_time_seconds > 0
0 <= expected_flow_ratio <= 2
0 <= tolerance_ratio <= 1
```

### 3-4. `anomaly_policies`

초기 정책 코드:

```text
CAMERA_OFFLINE_RULE_V1
FPS_DEGRADATION_RULE_V1
FRAME_DROP_DEGRADATION_RULE_V1
LATENCY_DEGRADATION_RULE_V1
BLUR_DEGRADATION_RULE_V1
OCR_QUALITY_DEGRADATION_RULE_V1
RESOURCE_SATURATION_RULE_V1
NETWORK_INSTABILITY_RULE_V1
CAMERA_ROBUST_ZSCORE_V1
CAMERA_TREND_PROJECTION_V1
TRAFFIC_CONTEXT_VALIDATION_V1
```

`threshold_direction` 규칙:

```text
HIGHER_IS_WORSE: 값이 높을수록 위험 → warning_threshold < critical_threshold
LOWER_IS_WORSE:  값이 낮을수록 위험 → warning_threshold > critical_threshold
```

`warning_consecutive_windows` / `critical_consecutive_windows` 분리:
RESOURCE_SATURATION처럼 WARNING과 CRITICAL의 연속 위반 횟수가 다른 경우를 지원한다.

추세 정책의 `config_json` 예:

```json
{
  "windowMinutes": 15,
  "minimumValidSamples": 12,
  "ewmaAlpha": 0.3,
  "minimumTrendConfidence": 0.6,
  "predictionHorizonMinutes": 10
}
```

CAMERA_OFFLINE `config_json` 예:

```json
{"offlineThresholdSeconds": 60}
```

NETWORK_INSTABILITY `config_json` 예:

```json
{"frameDisconnectAlsoCritical": true}
```

### 3-5. `detector_versions`

```text
UNIQUE(detector_name, version)
```

초기 레코드:

```text
camera-rule                    / 1.1.0 / RULE             / ACTIVE
camera-robust-zscore           / 1.0.0 / ROBUST_Z_SCORE   / ACTIVE
camera-trend-projection        / 1.0.0 / TREND_PROJECTION  / ACTIVE
camera-context-cross-validator / 1.0.0 / CROSS_VALIDATION  / ACTIVE
camera-lstm-autoencoder        / 1.0.0 / LSTM_AUTOENCODER  / EXPERIMENTAL
```

`operating_mode` 의미:

```text
ACTIVE:       실제 알람 발생
SHADOW:       로그만 기록, 알람 없음
EXPERIMENTAL: 학습 미완료, FastAPI 미적재
```

학습 모델은 `artifact_path`, `artifact_sha256`, `feature_schema_version`, `dataset_version`, `trained_at`이 필수다. 비학습 detector는 해당 필드를 `null`로 둔다.

### 3-6. `anomaly_events`

- MVP의 `target_type` 값은 `CAMERA`만 허용한다.
- `target_camera_id`는 필수다.
- 교통 맥락만으로 이벤트를 생성하지 않는다.
- 추세 탐지가 아니면 추세·예측 컬럼은 `null`이다.
- `confirmed_cause`는 아래 9개 값만 허용한다.
- `recurrence_count >= 0` 제약이 있다.

```sql
CREATE UNIQUE INDEX ux_anomaly_events_active
ON anomaly_events (target_camera_id, anomaly_type)
WHERE status IN ('OPEN', 'ACKNOWLEDGED', 'RECOVERED');
```

### 3-7. `anomaly_event_evidence`

판단 근거를 행 단위로 저장한다. 교통 맥락은 `context_json`에 출처 카메라와 시간 구간을 포함한다.

```json
{
  "metricName": "fpsAvg",
  "observedValue": 8.4,
  "baselineValue": 24.1,
  "thresholdValue": 10.0,
  "metricScore": -4.2,
  "unit": "fps",
  "context": {
    "adjacentTrafficNormal": true,
    "sourceCameraIds": [1, 2]
  }
}
```

### 3-8. `maintenance_tickets`

```text
UNIQUE(anomaly_event_id)
UNIQUE(ticket_number)
ticket_number 형식: MNT-YYYYMMDD-0001
```

동시 생성 충돌을 피하기 위해 PostgreSQL sequence(`maintenance_ticket_number_seq`)를 사용한다.

### 3-9. `model_prediction_logs`

LSTM AutoEncoder의 SHADOW 추론 결과를 저장한다.

```text
UNIQUE(camera_id, detector_version_id, evaluated_at)
0 <= anomaly_score <= 1
0 <= warning_threshold <= 1
0 <= critical_threshold <= 1
warning_threshold < critical_threshold
input_window_from < input_window_to
predicted_anomaly = FALSE이면 predicted_severity는 NULL
```

- 이 테이블은 `anomaly_events`와 직접 연결하지 않는다.
- `predicted_anomaly=true`여도 이벤트·티켓 생성 조건으로 사용하지 않는다.
- `top_features_json`은 설명용 상위 변화 feature만 저장하며 원본 시계열 전체를 복제하지 않는다.

인덱스:

```text
(camera_id, evaluated_at DESC)
(detector_version_id, evaluated_at DESC)
(predicted_anomaly, evaluated_at DESC)
```

### 3-10. `maintenance_ticket_histories`

상태, 담당자, 조치 메모 변경을 append-only로 기록한다. 수정·삭제 API는 제공하지 않는다.

## 4. Enum 계약

| 구분 | 값 |
|---|---|
| `DataSource` | `REAL`, `OPEN_DATA`, `SIMULATED`, `FAULT_INJECTED`, `MOCK` |
| `QualityStatus` | `COMPLETE`, `PARTIAL`, `INSUFFICIENT` |
| `TargetType` | `CAMERA` |
| `DetectionMethod` | `RULE`, `ROBUST_Z_SCORE`, `TREND_PROJECTION`, `CROSS_VALIDATION`, `LSTM_AUTOENCODER` |
| `DetectorOperatingMode` | `ACTIVE`, `SHADOW`, `EXPERIMENTAL` |
| `ThresholdDirection` | `HIGHER_IS_WORSE`, `LOWER_IS_WORSE` |
| `AnomalyType` | `CAMERA_OFFLINE`, `FPS_DEGRADATION`, `FRAME_DROP_DEGRADATION`, `LATENCY_DEGRADATION`, `BLUR_DEGRADATION`, `OCR_QUALITY_DEGRADATION`, `RESOURCE_SATURATION`, `NETWORK_INSTABILITY` |
| `Severity` | `WARNING`, `CRITICAL` |
| `AnomalyStatus` | `OPEN`, `ACKNOWLEDGED`, `RECOVERED`, `RESOLVED`, `DISMISSED` |
| `TicketPriority` | `P1`, `P2`, `P3` |
| `TicketStatus` | `OPEN`, `ASSIGNED`, `IN_PROGRESS`, `RESOLVED`, `CLOSED` |
| `UserRole` | `USER`, `OPERATOR`, `MAINTAINER`, `ADMIN` |
| `HealthStatus` | `NORMAL`, `DEGRADED`, `CRITICAL`, `OFFLINE`, `BASELINE_LEARNING`, `INSUFFICIENT_DATA` |
| `SuspectedCause` | `CAMERA_POWER_OR_NETWORK`, `CAMERA_LENS_OR_FOCUS`, `LOW_ILLUMINATION`, `AI_PROCESSING_OVERLOAD`, `OCR_PIPELINE_DEGRADATION`, `NETWORK_CONGESTION`, `EXTERNAL_TRAFFIC_CHANGE`, `INSUFFICIENT_DATA`, `UNKNOWN` |

## 5. 기존 데이터 연결

`traffic_context_samples` 집계 원천:

- `vehicle_flow_events`: 차량 수, 방향, 평균 속도
- `detection_analysis_results`: OCR 시도·성공·실패
- `speed_violations`: 과속 이벤트 수

추적 컬럼:

- `source_from_flow_event_id`
- `source_to_flow_event_id`
- 집계 로그의 시간 범위와 처리 건수

## 6. 마이그레이션

1. 적용된 `001`~`006` migration은 수정하지 않는다.
2. 신규 테이블은 `007_predictive_maintenance_schema.sql`로 생성한다.
3. 정책과 detector version은 `008_predictive_seed_policies.sql`로 삽입한다.
4. 현재 저장소에는 자동 migration runner가 없으므로 `psql`로 transaction 검증 후 적용한다.
5. 로컬 개발의 기존 `ddl-auto=update`와 팀 공용·시연의 `ddl-auto=validate` 설정을 Spring profile로 분리한다.
6. 팀 공용·시연 profile은 `spring.sql.init.mode=never`를 사용한다.
7. 데모 데이터는 migration이 아니라 별도 seed profile로 주입한다.

## 7. 보관 정책

| 데이터 | 보관 |
|---|---:|
| 카메라 상태 샘플 | 90일 |
| 교통 맥락 샘플 | 90일 |
| 이상 이벤트·근거 | 1년 |
| 정비 티켓·이력 | 1년 |
| detector version·정책 | 영구 |
| SHADOW 모델 예측 로그 | 90일 |

이벤트와 티켓이 참조하는 근거는 일반 샘플 정리 작업과 별도로 보존한다.
