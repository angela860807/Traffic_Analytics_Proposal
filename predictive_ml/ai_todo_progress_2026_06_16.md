# TAS-PM AI TODO Progress - 2026-06-16

## Completed Model Experiments

- LSTM-AE v4 precursor evaluation completed.
- LSTM-AE v5 time-pattern experiment completed.
- LSTM-AE v6 time-pattern + precursor experiment completed.
- Current representative LSTM-AE candidate:
  - `camera-lstm-autoencoder / 1.0.0 / LSTM_AUTOENCODER / SHADOW`
  - artifact version: `v6_timepattern_precursor_thr999`
  - average early lead time: 43.4 minutes
  - average scenario F1: 0.8051
  - false alarms: 61 normal sequences

## Completed Detector Package Work

Added installable package skeleton:

```text
predictive_ml/
  pyproject.toml
  src/predictive_ml/
    contracts.py
    rule_detector.py
    robust_zscore_detector.py
    trend_projection_detector.py
    degradation_detector.py
    policies.py
    manifest.py
  configs/detector-policy.yaml
  tests/smoke_test_detectors.py
```

Implemented public functions:

```python
detect_rules(request: RuleDetectionInput) -> DetectionResult
detect_degradation(request: DegradationDetectionInput) -> DetectionResult
get_detector_manifest() -> dict
```

Implemented detector logic:

- Rule Detector
  - camera offline
  - FPS degradation
  - frame drop degradation
  - latency degradation
  - blur degradation
  - OCR quality degradation
  - resource saturation
  - network instability
- Robust Z-Score Detector
  - median/MAD baseline
  - 30-sample learning guard
  - warning z-score 3.5
  - critical z-score 5.0
- Trend Projection Detector
  - last 15-minute input contract
  - EWMA alpha 0.3
  - Theil-Sen slope
  - Spearman confidence
  - 10-minute prediction horizon

## Verification

Smoke test command:

```powershell
$env:PYTHONPATH='C:\bk\Traffic_Analytics_Proposal\predictive_ml\src'
python C:\bk\Traffic_Analytics_Proposal\predictive_ml\tests\smoke_test_detectors.py
```

Result:

```text
predictive_ml detector smoke test passed
```

## LSTM-AE SHADOW Connection

Connected `predict_anomaly()` to the v6 LSTM-AE artifact:

```text
predictive_ml/model/lstm_ae_v6_timepattern_precursor_thr999.pt
predictive_ml/model/scaler_v6_timepattern_precursor.pkl
predictive_ml/model/threshold_v6_timepattern_precursor_thr999.json
predictive_ml/model/metrics_v6_timepattern_precursor_thr999.json
predictive_ml/model/feature_schema_v6_timepattern_precursor.json
predictive_ml/model/training_manifest_v6_timepattern_precursor.json
predictive_ml/model/artifact_sha256_v6_timepattern_precursor.json
```

The runtime model directory can be overridden with:

```text
TAS_PM_LSTM_AE_MODEL_DIR
```

## Remaining AI Work

- Copy v4, v5, v6 scripts/results/artifacts from `C:\bk\tas-pm-ai` into `predictive_ml`.
- Copy v4 and v5 scripts/results if version-by-version Git history is needed.
- Add FastAPI handoff fixture JSON.
- Add traffic context cross-validator.
- Run detector logic on generated simulation samples and record comparison with LSTM-AE v6.

## Runtime Verification - 2026-06-18

All checks below were executed from `C:\bk\Traffic_Analytics_Proposal` with:

```powershell
$env:PYTHONPATH="C:\bk\Traffic_Analytics_Proposal\predictive_ml\src"
```

### 1. Detector Package Smoke Test

Command:

```powershell
python C:\bk\Traffic_Analytics_Proposal\predictive_ml\tests\smoke_test_detectors.py
```

Result:

```text
predictive_ml detector smoke test passed
```

Meaning:

- `detect_rules()` imports and runs.
- `detect_degradation()` imports and runs.
- `get_detector_manifest()` returns package metadata.
- Rule, robust z-score, and trend projection basic paths are not broken.

### 2. LSTM-AE v6 SHADOW Normal Sample

Input summary:

- 30-minute sequence
- Stable normal-like values
- `fps_avg=28.0`, `frame_drop_rate=0.01`, `latency_p95_ms=330`

Result:

```text
predicted_anomaly: False
predicted_severity: None
anomaly_score: 0.05324674290148313
warning_threshold: 0.410734
critical_threshold: 0.462065
skipped_reason: None
top_features: fpsAvg, cpuUsagePct, ocrFailRate
```

Meaning:

- v6 model, scaler, threshold, and feature schema loaded successfully.
- Normal-like sequence stayed below the warning threshold.
- `skipped_reason=None` confirms actual inference was executed.

### 3. LSTM-AE v6 SHADOW Degrading Sample

Input summary:

- 30-minute degrading sequence
- FPS gradually decreases
- frame drop, latency, CPU, memory, OCR fail rate, and RTT gradually increase

Result:

```text
predicted_anomaly: True
predicted_severity: CRITICAL
anomaly_score: 1.0
warning_threshold: 0.410734
critical_threshold: 0.462065
skipped_reason: None
top_features: frameDropRate, latencyP95Ms, fpsAvg
```

Meaning:

- v6 LSTM-AE separates normal-like and degrading sequences in runtime inference.
- Main reconstruction-error contributors match the injected degradation pattern.

### 4. Rule Detector FPS Warning

Input summary:

- `fps_avg=7.5`
- `consecutive_windows={"fps_avg": 3}`

Result:

```text
status: WARNING
detector: camera-rule / 1.1.0 / RULE
candidate_count: 1
anomaly_type: FPS_DEGRADATION
severity: WARNING
score: 0.5
policy_code: FPS_DEGRADATION_RULE_V1
```

Evidence summary:

```text
metric_name: fps_avg
observed_value: 7.5
threshold_value: 10.0
requiredConsecutiveWindows: 3
actualConsecutiveWindows: 3
```

Meaning:

- Rule detector creates explainable evidence for threshold-based FPS degradation.

### 5. Robust Z-Score and Trend Projection Critical Case

Input summary:

- Current `fps_avg=7.5`
- Baseline `median=28.0`, `mad=1.0`, `sample_count=42`
- Last 15-minute FPS trend decreases from 20.0 to 6.0

Result:

```text
status: CRITICAL
baseline_status: READY
candidate_count: 2
```

Candidate 1:

```text
anomaly_type: FPS_DEGRADATION
severity: CRITICAL
method: ROBUST_Z_SCORE
score: 1.0
policy_code: FPS_DEGRADATION_ROBUST_ZSCORE_V1
directionalRobustZ: 13.827060569270202
criticalZ: 5.0
```

Candidate 2:

```text
anomaly_type: FPS_DEGRADATION
severity: CRITICAL
method: TREND_PROJECTION
score: 1.0
policy_code: CAMERA_TREND_PROJECTION_V1
projected_threshold_crossing_at: 2026-06-18 12:33:39.692586
trend_slope: -0.9060409893083176
trend_confidence: 1.0
```

Meaning:

- Robust z-score detects strong deviation from the camera baseline.
- Trend projection estimates threshold crossing within the 10-minute prediction horizon.

### 6. Baseline Learning Guard

Input summary:

- `sample_count=12`
- Required baseline sample count is 30

Result:

```text
status: LEARNING
baseline_status: LEARNING
required_sample_count: 30
current_sample_count: 12
candidate_count: 0
skipped_reason: None
```

Meaning:

- When baseline data is insufficient, degradation detection avoids creating anomaly candidates.
- This prevents unstable z-score/trend judgments for newly added or under-sampled cameras.

## Updated Remaining AI Work - 2026-06-18

- Add FastAPI handoff fixture JSON for rule, degradation, and LSTM SHADOW responses.
- Decide whether `predictive_ml` should be handed to the FastAPI `woong` branch as source package, wheel, or selected files.
- Verify `predict_anomaly()` inside the actual FastAPI runtime or Docker image.
- Add or defer traffic context cross-validator for external traffic vs equipment degradation separation.
- Document final integration rule: ACTIVE candidates from Rule/z-score/trend, SHADOW candidates from LSTM-AE only.
