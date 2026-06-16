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
