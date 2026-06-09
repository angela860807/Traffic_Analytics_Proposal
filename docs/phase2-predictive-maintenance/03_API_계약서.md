# TAS 2차 프로젝트 API 계약서

## 1. 계약 원칙

- 외부 운영 API는 Spring Boot가 `/api/v1/predictive` 아래에서 제공한다.
- Frontend는 FastAPI를 직접 호출하지 않는다.
- 내부 통신은 `/internal/v1`과 `X-Internal-Api-Key`를 사용한다.
- JSON 필드는 `camelCase`, Enum은 `UPPER_SNAKE_CASE`를 사용한다.
- 시간은 ISO-8601 offset 형식이다.
- Entity를 직접 응답하지 않는다.
- 교통 맥락은 CCTV 판단 근거이며 독립적인 정비 이상 유형이 아니다.

## 2. 공통 계약

### 2-1. 인증

```http
Authorization: Bearer <JWT>
X-Request-Id: <UUID>
```

내부 API:

```http
X-Internal-Api-Key: <secret>
X-Request-Id: <UUID>
```

### 2-2. 페이지 응답

```json
{
  "content": [],
  "page": 0,
  "size": 20,
  "totalElements": 0,
  "totalPages": 0,
  "sort": "firstDetectedAt,desc"
}
```

`size`는 1~100만 허용한다.

### 2-3. 에러 응답

```json
{
  "timestamp": "2026-06-09T14:05:00+09:00",
  "status": 400,
  "code": "INVALID_REQUEST",
  "message": "요청값이 올바르지 않습니다.",
  "requestId": "25e3259d-7bbf-41af-a81c-43ec67550867",
  "fieldErrors": [
    {
      "field": "toStatus",
      "reason": "허용되지 않은 상태 전이입니다."
    }
  ]
}
```

공통 코드:

```text
INVALID_REQUEST
UNAUTHORIZED
FORBIDDEN
RESOURCE_NOT_FOUND
CONFLICT
INVALID_STATE_TRANSITION
DUPLICATE_RESOURCE
BASELINE_NOT_READY
INTERNAL_DETECTOR_UNAVAILABLE
```

### 2-4. Enum

```text
DataSource: REAL, OPEN_DATA, SIMULATED, FAULT_INJECTED, MOCK
QualityStatus: COMPLETE, PARTIAL, INSUFFICIENT
TargetType: CAMERA
DetectionMethod: RULE, ROBUST_Z_SCORE, TREND_PROJECTION, CROSS_VALIDATION
AnomalyType: CAMERA_OFFLINE, FPS_DEGRADATION, FRAME_DROP_DEGRADATION,
             LATENCY_DEGRADATION, BLUR_DEGRADATION,
             OCR_QUALITY_DEGRADATION, RESOURCE_SATURATION,
             NETWORK_INSTABILITY
Severity: WARNING, CRITICAL
AnomalyStatus: OPEN, ACKNOWLEDGED, RECOVERED, RESOLVED, DISMISSED
TicketPriority: P1, P2, P3
TicketStatus: OPEN, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED
HealthStatus: NORMAL, DEGRADED, CRITICAL, OFFLINE,
              BASELINE_LEARNING, INSUFFICIENT_DATA
BaselineStatus: READY, LEARNING
```

## 3. Frontend용 Spring Boot API

### 3-1. 운영 요약

```http
GET /api/v1/predictive/summary?dataSource=REAL
```

```json
{
  "totalCameras": 12,
  "normalCameras": 8,
  "degradedCameras": 2,
  "criticalCameras": 1,
  "offlineCameras": 1,
  "baselineLearningCameras": 0,
  "openAnomalies": 4,
  "predictedRisks": 2,
  "overdueTickets": 1,
  "mttaMinutes": 7.4,
  "mttrMinutes": 41.2,
  "generatedAt": "2026-06-09T14:05:00+09:00"
}
```

### 3-2. 카메라 운영 상태

```http
GET /api/v1/predictive/cameras?zoneId=3&healthStatus=DEGRADED&dataSource=REAL&page=0&size=20&sort=healthScore,asc
```

응답 항목:

```json
{
  "cameraId": 1,
  "cameraName": "정문-01",
  "zoneId": 3,
  "healthScore": 62.5,
  "healthStatus": "DEGRADED",
  "baselineStatus": "READY",
  "activeAnomalyCount": 1,
  "predictedRiskCount": 1,
  "latestSampledAt": "2026-06-09T14:04:00+09:00",
  "dataSource": "REAL"
}
```

### 3-3. 카메라 상태 이력

```http
GET /api/v1/predictive/cameras/1/health-history?from=2026-06-09T13:00:00%2B09:00&to=2026-06-09T14:00:00%2B09:00&dataSource=REAL
```

```json
{
  "cameraId": 1,
  "samples": [
    {
      "sampledAt": "2026-06-09T13:59:00+09:00",
      "fpsAvg": 8.4,
      "frameDropRate": 0.34,
      "latencyP95Ms": 2300,
      "blurScoreAvg": 0.42,
      "ocrFailRate": 0.31,
      "cpuUsagePct": 88.2,
      "memoryUsagePct": 72.1,
      "networkRttMs": 84,
      "healthScore": 58.6,
      "qualityStatus": "COMPLETE"
    }
  ]
}
```

### 3-4. 교통 맥락 이력

```http
GET /api/v1/predictive/traffic-context?cameraId=1&zoneId=3&from=2026-06-09T00:00:00%2B09:00&to=2026-06-10T00:00:00%2B09:00&dataSource=REAL
```

```json
{
  "cameraId": 1,
  "zoneId": 3,
  "samples": [
    {
      "sampledAt": "2026-06-09T13:55:00+09:00",
      "windowMinutes": 5,
      "vehicleCount": 47,
      "avgSpeedKmh": 42.8,
      "speedViolationCount": 3,
      "ocrAttemptCount": 41,
      "ocrSuccessCount": 37,
      "ocrFailureCount": 4,
      "qualityStatus": "COMPLETE",
      "dataSource": "REAL"
    }
  ]
}
```

### 3-5. 이상 이벤트 목록

```http
GET /api/v1/predictive/anomaly-events?cameraId=1&severity=CRITICAL&status=OPEN&anomalyType=FPS_DEGRADATION&detectionMethod=TREND_PROJECTION&dataSource=REAL&from=2026-06-09T00:00:00%2B09:00&to=2026-06-10T00:00:00%2B09:00&page=0&size=20&sort=firstDetectedAt,desc
```

응답 항목:

```json
{
  "id": 101,
  "targetType": "CAMERA",
  "cameraId": 1,
  "cameraName": "정문-01",
  "anomalyType": "FPS_DEGRADATION",
  "severity": "WARNING",
  "status": "OPEN",
  "detectionMethod": "TREND_PROJECTION",
  "anomalyScore": 0.86,
  "projectedThresholdCrossingAt": "2026-06-09T14:12:00+09:00",
  "firstDetectedAt": "2026-06-09T14:02:00+09:00",
  "lastDetectedAt": "2026-06-09T14:04:00+09:00",
  "dataSource": "REAL"
}
```

### 3-6. 이상 이벤트 상세

```http
GET /api/v1/predictive/anomaly-events/101
```

```json
{
  "id": 101,
  "targetType": "CAMERA",
  "cameraId": 1,
  "cameraName": "정문-01",
  "anomalyType": "FPS_DEGRADATION",
  "severity": "WARNING",
  "status": "OPEN",
  "detectionMethod": "TREND_PROJECTION",
  "detector": {
    "name": "camera-trend-projection",
    "version": "1.0.0"
  },
  "policyCode": "CAMERA_TREND_PROJECTION_V1",
  "baseline": {
    "source": "CAMERA_30_MINUTE_BUCKET_14D",
    "from": "2026-05-26T14:00:00+09:00",
    "to": "2026-06-09T14:00:00+09:00",
    "sampleCount": 54
  },
  "trend": {
    "slope": -0.73,
    "confidence": 0.81,
    "predictionHorizonMinutes": 10,
    "projectedThresholdCrossingAt": "2026-06-09T14:12:00+09:00"
  },
  "suspectedCauses": [
    "AI_PROCESSING_OVERLOAD"
  ],
  "evidence": [
    {
      "metricName": "fpsAvg",
      "observedValue": 11.2,
      "baselineValue": 24.1,
      "thresholdValue": 10.0,
      "metricScore": -4.2,
      "unit": "fps",
      "sampledAt": "2026-06-09T14:04:00+09:00",
      "context": {
        "adjacentTrafficNormal": true,
        "cpuUsagePct": 91.3
      }
    }
  ],
  "ticket": {
    "id": 501,
    "ticketNumber": "MNT-20260609-0001",
    "priority": "P2",
    "status": "OPEN"
  }
}
```

### 3-7. 이상 이벤트 확인

```http
POST /api/v1/predictive/anomaly-events/101/acknowledge
Content-Type: application/json

{
  "note": "현장 점검 요청"
}
```

권한: `OPERATOR`, `ADMIN`

### 3-8. 이상 이벤트 해결

```http
POST /api/v1/predictive/anomaly-events/101/resolve
Content-Type: application/json

{
  "confirmedCause": "AI_PROCESSING_OVERLOAD",
  "resolutionNote": "분석 프로세스 재기동 후 FPS 정상화"
}
```

### 3-9. 이상 이벤트 오탐 종료

```http
POST /api/v1/predictive/anomaly-events/101/dismiss
Content-Type: application/json

{
  "reason": "정상 야간 교통량 감소를 장애로 판단한 오탐"
}
```

권한: `OPERATOR`, `ADMIN`

### 3-10. 정비 티켓 목록

```http
GET /api/v1/predictive/maintenance-tickets?priority=P1&status=OPEN&assigneeId=7&page=0&size=20&sort=createdAt,desc
```

응답 항목:

```json
{
  "id": 501,
  "ticketNumber": "MNT-20260609-0001",
  "anomalyEventId": 101,
  "cameraId": 1,
  "priority": "P2",
  "status": "OPEN",
  "assignee": null,
  "dueAckAt": "2026-06-09T14:32:00+09:00",
  "dueStartAt": "2026-06-09T16:02:00+09:00",
  "ackOverdue": false,
  "startOverdue": false,
  "createdAt": "2026-06-09T14:02:00+09:00"
}
```

### 3-11. 수동 정비 티켓 생성

```http
POST /api/v1/predictive/maintenance-tickets
Content-Type: application/json

{
  "anomalyEventId": 101,
  "priority": "P3",
  "actionNote": "예방 점검"
}
```

### 3-12. 정비 티켓 배정

```http
POST /api/v1/predictive/maintenance-tickets/501/assign
Content-Type: application/json

{
  "assigneeId": 7,
  "note": "네트워크 점검 담당 배정"
}
```

### 3-13. 정비 티켓 상태 변경

```http
POST /api/v1/predictive/maintenance-tickets/501/status
Content-Type: application/json

{
  "toStatus": "IN_PROGRESS",
  "note": "현장 점검 시작"
}
```

`RESOLVED`는 `note`가 필수이며 허용된 상태 전이만 처리한다.

### 3-14. 정책 목록

```http
GET /api/v1/predictive/policies?enabled=true
```

```json
{
  "policyCode": "CAMERA_TREND_PROJECTION_V1",
  "anomalyType": "FPS_DEGRADATION",
  "detectionMethod": "TREND_PROJECTION",
  "warningThreshold": 10.0,
  "criticalThreshold": 5.0,
  "minimumSampleCount": 12,
  "predictionHorizonMinutes": 10,
  "config": {
    "windowMinutes": 15,
    "ewmaAlpha": 0.3,
    "minimumTrendConfidence": 0.6
  },
  "enabled": true,
  "updatedAt": "2026-06-09T09:00:00+09:00"
}
```

### 3-15. 정책 수정

```http
PATCH /api/v1/predictive/policies/CAMERA_TREND_PROJECTION_V1
Content-Type: application/json

{
  "predictionHorizonMinutes": 10,
  "minimumSampleCount": 12,
  "config": {
    "windowMinutes": 15,
    "ewmaAlpha": 0.3,
    "minimumTrendConfidence": 0.65
  },
  "enabled": true
}
```

권한: `ADMIN`

## 4. FastAPI -> Spring Boot 수집 API

### 4-1. 카메라 상태 샘플 저장

```http
POST /internal/v1/camera-health-samples
```

```json
{
  "idempotencyKey": "camera-1-20260609T140400+0900",
  "cameraId": 1,
  "processorCode": "edge-01",
  "sampledAt": "2026-06-09T14:04:00+09:00",
  "sampleWindowSeconds": 60,
  "fpsAvg": 11.2,
  "frameDropRate": 0.21,
  "latencyP95Ms": 1600,
  "blurScoreAvg": 0.42,
  "brightnessScoreAvg": 0.51,
  "detectionCount": 9,
  "ocrAttemptCount": 8,
  "ocrFailureCount": 2,
  "ocrFailRate": 0.25,
  "cpuUsagePct": 91.3,
  "memoryUsagePct": 74.1,
  "diskUsagePct": 61.5,
  "networkRttMs": 84,
  "lastFrameAt": "2026-06-09T14:04:58+09:00",
  "dataSource": "REAL",
  "qualityStatus": "COMPLETE",
  "isImputed": false
}
```

응답:

```json
{
  "sampleId": 9001,
  "created": true
}
```

## 5. Spring Boot -> FastAPI 탐지 API

### 5-1. 즉시 Rule 평가

```http
POST /internal/v1/anomaly-detection/camera-health/evaluate
```

```json
{
  "cameraId": 1,
  "evaluatedAt": "2026-06-09T14:05:00+09:00",
  "samples": [
    {
      "sampledAt": "2026-06-09T14:04:00+09:00",
      "fpsAvg": 4.8,
      "frameDropRate": 0.64,
      "latencyP95Ms": 5200,
      "blurScoreAvg": 0.42,
      "ocrFailRate": 0.25,
      "ocrAttemptCount": 24,
      "cpuUsagePct": 96.1,
      "memoryUsagePct": 76.0,
      "networkRttMs": 80,
      "lastFrameAt": "2026-06-09T14:04:58+09:00",
      "qualityStatus": "COMPLETE"
    }
  ],
  "policies": [
    {
      "policyCode": "FPS_DEGRADATION_RULE_V1",
      "warningThreshold": 10.0,
      "criticalThreshold": 5.0,
      "consecutiveWindows": 3
    }
  ]
}
```

### 5-2. 기준선·추세·교통 맥락 평가

```http
POST /internal/v1/anomaly-detection/camera-degradation/evaluate
```

```json
{
  "cameraId": 1,
  "evaluatedAt": "2026-06-09T14:05:00+09:00",
  "recentHealthSamples": [],
  "baseline": {
    "source": "CAMERA_30_MINUTE_BUCKET_14D",
    "from": "2026-05-26T14:00:00+09:00",
    "to": "2026-06-09T14:00:00+09:00",
    "sampleCount": 54,
    "metrics": {
      "fpsAvg": {
        "median": 24.1,
        "mad": 2.1
      },
      "latencyP95Ms": {
        "median": 540.0,
        "mad": 85.0
      }
    }
  },
  "trafficContext": {
    "currentCameraVehicleCount": 8,
    "adjacentCameraVehicleCounts": {
      "2": 43,
      "3": 39
    },
    "qualityStatus": "COMPLETE"
  },
  "policy": {
    "policyCode": "CAMERA_TREND_PROJECTION_V1",
    "windowMinutes": 15,
    "minimumValidSamples": 12,
    "ewmaAlpha": 0.3,
    "minimumTrendConfidence": 0.6,
    "predictionHorizonMinutes": 10
  }
}
```

### 5-3. 공통 탐지 응답

```json
{
  "detector": {
    "name": "camera-trend-projection",
    "version": "1.0.0",
    "method": "TREND_PROJECTION"
  },
  "evaluatedAt": "2026-06-09T14:05:00+09:00",
  "baselineStatus": "READY",
  "candidates": [
    {
      "targetType": "CAMERA",
      "cameraId": 1,
      "anomalyType": "FPS_DEGRADATION",
      "severity": "WARNING",
      "anomalyScore": 0.86,
      "policyCode": "CAMERA_TREND_PROJECTION_V1",
      "trend": {
        "slope": -0.73,
        "confidence": 0.81,
        "predictionHorizonMinutes": 10,
        "projectedThresholdCrossingAt": "2026-06-09T14:12:00+09:00"
      },
      "suspectedCauses": [
        "AI_PROCESSING_OVERLOAD"
      ],
      "evidence": [
        {
          "metricName": "fpsAvg",
          "observedValue": 11.2,
          "baselineValue": 24.1,
          "thresholdValue": 10.0,
          "metricScore": -4.2,
          "unit": "fps",
          "sampledAt": "2026-06-09T14:04:00+09:00",
          "context": {
            "adjacentTrafficNormal": true
          }
        }
      ]
    }
  ]
}
```

기준선 부족 응답:

```json
{
  "detector": {
    "name": "camera-trend-projection",
    "version": "1.0.0",
    "method": "TREND_PROJECTION"
  },
  "evaluatedAt": "2026-06-09T14:05:00+09:00",
  "baselineStatus": "LEARNING",
  "requiredSampleCount": 30,
  "currentSampleCount": 12,
  "candidates": []
}
```

### 5-4. FastAPI 상태

```http
GET /internal/v1/anomaly-detection/health
```

```json
{
  "status": "UP",
  "detectors": [
    {
      "name": "camera-rule",
      "version": "1.1.0",
      "active": true
    },
    {
      "name": "camera-robust-zscore",
      "version": "1.0.0",
      "active": true
    },
    {
      "name": "camera-trend-projection",
      "version": "1.0.0",
      "active": true
    },
    {
      "name": "camera-context-cross-validator",
      "version": "1.0.0",
      "active": true
    }
  ]
}
```

## 6. 권한

| 기능 | USER | OPERATOR | MAINTAINER | ADMIN |
|---|---:|---:|---:|---:|
| 기존 교통·과속 조회 | O | O | O | O |
| 예지보전 대시보드 조회 | - | O | O | O |
| 이벤트 확인·오탐 종료 | - | O | - | O |
| 티켓 배정 | - | O | - | O |
| 티켓 작업 상태·조치 변경 | - | O | O | O |
| 정책 수정 | - | - | - | O |

## 7. 정렬 허용 필드

```text
cameras: cameraName, healthScore, latestSampledAt
anomaly-events: firstDetectedAt, lastDetectedAt, severity, anomalyScore
maintenance-tickets: createdAt, dueAckAt, dueStartAt, priority
```

허용 목록 밖의 정렬 필드는 `400 INVALID_REQUEST`로 응답한다.

## 8. 버전 변경

- 필드 추가는 하위 호환으로 처리한다.
- 필드 삭제·이름 변경·Enum 제거는 `/api/v2`에서 수행한다.
- Enum 추가 시 Frontend의 unknown fallback을 함께 검증한다.
- 내부 detector 요청·응답 스키마 변경 시 Spring Boot와 FastAPI 테스트를 같은 PR에서 수정한다.
