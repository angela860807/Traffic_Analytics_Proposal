from __future__ import annotations

from .contracts import BaselineMetric, CameraSample, DetectionCandidate, Evidence
from .policies import METRIC_ANOMALY_TYPES, METRIC_DIRECTIONS, METRIC_UNITS, SUSPECTED_CAUSES

DETECTOR_NAME = "camera-robust-zscore"
DETECTOR_VERSION = "1.0.0"
WARNING_Z = 3.5
CRITICAL_Z = 5.0
MIN_BASELINE_SAMPLES = 30
MAD_SCALE = 1.4826
MAD_EPSILON = 1e-9


def detect_robust_zscore(sample: CameraSample, baselines: dict[str, BaselineMetric]) -> list[DetectionCandidate]:
    candidates: list[DetectionCandidate] = []
    for metric_name, direction in METRIC_DIRECTIONS.items():
        observed = getattr(sample, metric_name, None)
        baseline = baselines.get(metric_name)
        if observed is None or baseline is None:
            continue
        if baseline.sample_count < MIN_BASELINE_SAMPLES:
            candidates.append(_learning_candidate(metric_name, sample, baseline))
            continue
        if baseline.median is None or baseline.mad is None:
            continue

        scaled_mad = max(abs(float(baseline.mad)) * MAD_SCALE, MAD_EPSILON)
        z_score = (float(observed) - float(baseline.median)) / scaled_mad
        directional_z = -z_score if direction == "LOWER_IS_WORSE" else z_score
        if directional_z < WARNING_Z:
            continue

        severity = "CRITICAL" if directional_z >= CRITICAL_Z else "WARNING"
        anomaly_type = METRIC_ANOMALY_TYPES[metric_name]
        candidates.append(
            DetectionCandidate(
                anomaly_type=anomaly_type,
                severity=severity,
                detection_method="ROBUST_Z_SCORE",
                policy_code=f"{anomaly_type}_ROBUST_ZSCORE_V1",
                detector_name=DETECTOR_NAME,
                detector_version=DETECTOR_VERSION,
                anomaly_score=min(1.0, directional_z / CRITICAL_Z),
                evidence=[
                    Evidence(
                        metric_name=metric_name,
                        observed_value=float(observed),
                        baseline_value=float(baseline.median),
                        metric_score=float(directional_z),
                        unit=METRIC_UNITS.get(metric_name),
                        context={
                            "robustZ": z_score,
                            "directionalRobustZ": directional_z,
                            "mad": baseline.mad,
                            "sampleCount": baseline.sample_count,
                            "warningZ": WARNING_Z,
                            "criticalZ": CRITICAL_Z,
                            "baselineFrom": baseline.baseline_from.isoformat() if baseline.baseline_from else None,
                            "baselineTo": baseline.baseline_to.isoformat() if baseline.baseline_to else None,
                            "baselineDataSource": baseline.data_source,
                        },
                    )
                ],
                suspected_causes=SUSPECTED_CAUSES.get(anomaly_type, ["UNKNOWN"]),
            )
        )
    return candidates


def _learning_candidate(metric_name: str, sample: CameraSample, baseline: BaselineMetric) -> DetectionCandidate:
    anomaly_type = METRIC_ANOMALY_TYPES[metric_name]
    return DetectionCandidate(
        anomaly_type=anomaly_type,
        severity="LEARNING",
        detection_method="ROBUST_Z_SCORE",
        policy_code=f"{anomaly_type}_ROBUST_ZSCORE_V1",
        detector_name=DETECTOR_NAME,
        detector_version=DETECTOR_VERSION,
        evidence=[
            Evidence(
                metric_name=metric_name,
                observed_value=getattr(sample, metric_name, None),
                baseline_value=baseline.median,
                context={
                    "sampleCount": baseline.sample_count,
                    "minimumSampleCount": MIN_BASELINE_SAMPLES,
                    "reason": "baseline_sample_count_below_minimum",
                },
            )
        ],
    )
