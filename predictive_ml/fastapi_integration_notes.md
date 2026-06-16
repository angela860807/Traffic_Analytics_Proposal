# FastAPI Integration Notes

Reference documents:

- `C:/Users/User/Downloads/03_API_계약서_ver2.md`
- `C:/bk/Traffic_Analytics_Proposal/docs/phase2-predictive-maintenance/06_FastAPI_작업_TODO.md`

## Public AI Package Interface

FastAPI should call only these public functions:

```python
from predictive_ml import (
    detect_rules,
    detect_degradation,
    predict_anomaly,
    get_detector_manifest,
)
```

Do not duplicate Rule, robust z-score, EWMA, Theil-Sen, or Spearman logic inside FastAPI.

## Function Mapping

| FastAPI endpoint | AI function |
|---|---|
| `POST /internal/v1/anomaly-detection/camera-health/evaluate` | `detect_rules()` |
| `POST /internal/v1/anomaly-detection/camera-degradation/evaluate` | `detect_degradation()` and `predict_anomaly()` |
| `GET /internal/v1/anomaly-detection/health` | `get_detector_manifest()` |

## Current Contract Alignment

- `detect_rules()` returns detector metadata, evaluated time, status, and active candidates.
- `detect_degradation()` returns `baseline_status`.
- If baseline samples are fewer than 30, `detect_degradation()` returns:
  - `baseline_status="LEARNING"`
  - `required_sample_count=30`
  - `current_sample_count=<minimum baseline count>`
  - `candidates=[]`
- Trend projection uses API/DB policy code:
  - `CAMERA_TREND_PROJECTION_V1`
- `predict_anomaly()` exists as the public SHADOW interface.
  - It loads the v6 LSTM-AE artifact from `predictive_ml/model`.
  - The model directory can be overridden with `TAS_PM_LSTM_AE_MODEL_DIR`.
  - Missing or invalid runtime dependencies are returned as `skipped_reason`.

## Field Naming

The AI package uses Python snake_case dataclasses.
FastAPI adapter should convert to API camelCase:

| AI field | API field |
|---|---|
| `evaluated_at` | `evaluatedAt` |
| `baseline_status` | `baselineStatus` |
| `policy_code` | `policyCode` |
| `anomaly_type` | `anomalyType` |
| `detection_method` | `detectionMethod` |
| `anomaly_score` | `anomalyScore` |
| `projected_threshold_crossing_at` | `projectedThresholdCrossingAt` |
| `suspected_causes` | `suspectedCauses` |
| `metric_name` | `metricName` |
| `observed_value` | `observedValue` |
| `baseline_value` | `baselineValue` |
| `threshold_value` | `thresholdValue` |
| `metric_score` | `metricScore` |

## Remaining AI Handoff Work

- Run `predict_anomaly()` inside `(tas-pm-env)` or the FastAPI runtime where `torch`, `numpy`, and `scikit-learn` are installed.
- Add request/response fixture JSON for both FastAPI internal detector endpoints.
