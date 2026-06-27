from __future__ import annotations

from .contracts import DetectionCandidate, DetectionResult, DetectorInfo, Evidence, RuleDetectionInput
from .policies import (
    METRIC_ANOMALY_TYPES,
    METRIC_DIRECTIONS,
    METRIC_UNITS,
    RULE_CONSECUTIVE_WINDOWS,
    RULE_THRESHOLDS,
    SUSPECTED_CAUSES,
)

DETECTOR_NAME = "camera-rule"
DETECTOR_VERSION = "1.1.0"


def detect_rules(request: RuleDetectionInput) -> DetectionResult:
    sample = request.sample
    if sample.quality_status != "COMPLETE" or sample.is_imputed or sample.is_late_sample:
        return DetectionResult(
            camera_id=sample.camera_id,
            evaluated_at=sample.sampled_at,
            status="NONE",
            detector=DetectorInfo(DETECTOR_NAME, DETECTOR_VERSION, "RULE"),
            skipped_reason="sample_quality_not_eligible",
        )

    candidates: list[DetectionCandidate] = []
    for metric_name, thresholds in RULE_THRESHOLDS.items():
        observed = getattr(sample, metric_name, None)
        if observed is None:
            continue
        if metric_name == "ocr_fail_rate" and (sample.ocr_attempt_count or 0) < 20:
            continue

        required_windows = RULE_CONSECUTIVE_WINDOWS[metric_name]
        actual_windows = request.consecutive_windows.get(metric_name, required_windows)
        if actual_windows < required_windows:
            continue

        severity = _severity_for_metric(metric_name, observed, thresholds)
        if severity == "NONE":
            continue

        anomaly_type = (
            "CAMERA_OFFLINE"
            if metric_name == "last_frame_age_seconds"
            else METRIC_ANOMALY_TYPES[metric_name]
        )
        threshold = thresholds["critical" if severity == "CRITICAL" else "warning"]
        candidates.append(
            DetectionCandidate(
                anomaly_type=anomaly_type,
                severity=severity,
                detection_method="RULE",
                policy_code=f"{anomaly_type}_RULE_V1",
                detector_name=DETECTOR_NAME,
                detector_version=DETECTOR_VERSION,
                anomaly_score=_rule_score(metric_name, observed, thresholds),
                evidence=[
                    Evidence(
                        metric_name=metric_name,
                        observed_value=float(observed),
                        threshold_value=threshold,
                        unit=METRIC_UNITS.get(metric_name),
                        context={
                            "requiredConsecutiveWindows": required_windows,
                            "actualConsecutiveWindows": actual_windows,
                        },
                    )
                ],
                suspected_causes=SUSPECTED_CAUSES.get(anomaly_type, ["UNKNOWN"]),
            )
        )

    return DetectionResult(
        camera_id=sample.camera_id,
        evaluated_at=sample.sampled_at,
        status=_overall_status(candidates),
        detector=DetectorInfo(DETECTOR_NAME, DETECTOR_VERSION, "RULE"),
        candidates=candidates,
    )


def _severity_for_metric(metric_name: str, observed: float, thresholds: dict[str, float]) -> str:
    direction = "HIGHER_IS_WORSE" if metric_name == "last_frame_age_seconds" else METRIC_DIRECTIONS[metric_name]
    if direction == "LOWER_IS_WORSE":
        if observed < thresholds["critical"]:
            return "CRITICAL"
        if observed < thresholds["warning"]:
            return "WARNING"
        return "NONE"
    if observed > thresholds["critical"]:
        return "CRITICAL"
    if observed > thresholds["warning"]:
        return "WARNING"
    return "NONE"


def _rule_score(metric_name: str, observed: float, thresholds: dict[str, float]) -> float:
    direction = "HIGHER_IS_WORSE" if metric_name == "last_frame_age_seconds" else METRIC_DIRECTIONS[metric_name]
    warning = thresholds["warning"]
    critical = thresholds["critical"]
    if direction == "LOWER_IS_WORSE":
        if observed >= warning:
            return 0.0
        if observed <= critical:
            return 1.0
        return min(1.0, max(0.0, (warning - observed) / (warning - critical)))
    if observed <= warning:
        return 0.0
    if observed >= critical:
        return 1.0
    return min(1.0, max(0.0, (observed - warning) / (critical - warning)))


def _overall_status(candidates: list[DetectionCandidate]) -> str:
    if any(candidate.severity == "CRITICAL" for candidate in candidates):
        return "CRITICAL"
    if any(candidate.severity == "WARNING" for candidate in candidates):
        return "WARNING"
    return "NONE"
