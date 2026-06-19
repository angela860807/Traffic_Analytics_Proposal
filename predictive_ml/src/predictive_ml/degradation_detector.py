from __future__ import annotations

from .contracts import DegradationDetectionInput, DetectionCandidate, DetectionResult, DetectorInfo
from .robust_zscore_detector import detect_robust_zscore
from .trend_projection_detector import detect_trend_projection


def detect_degradation(request: DegradationDetectionInput) -> DetectionResult:
    sample = request.sample
    if sample.quality_status != "COMPLETE" or sample.is_imputed or sample.is_late_sample:
        return DetectionResult(
            camera_id=sample.camera_id,
            evaluated_at=sample.sampled_at,
            status="NONE",
            detector=DetectorInfo("camera-trend-projection", "1.0.0", "TREND_PROJECTION"),
            skipped_reason="sample_quality_not_eligible",
        )

    learning_sample_count = _learning_sample_count(request)
    if learning_sample_count is not None:
        return DetectionResult(
            camera_id=sample.camera_id,
            evaluated_at=sample.sampled_at,
            status="LEARNING",
            detector=DetectorInfo("camera-trend-projection", "1.0.0", "TREND_PROJECTION"),
            baseline_status="LEARNING",
            required_sample_count=30,
            current_sample_count=learning_sample_count,
            candidates=[],
        )

    candidates: list[DetectionCandidate] = []
    candidates.extend(detect_robust_zscore(sample, request.baselines))
    candidates.extend(detect_trend_projection(request.trends, request.prediction_horizon_minutes))
    candidates = _deduplicate_candidates(candidates)

    return DetectionResult(
        camera_id=sample.camera_id,
        evaluated_at=sample.sampled_at,
        status=_overall_status(candidates),
        detector=DetectorInfo("camera-trend-projection", "1.0.0", "TREND_PROJECTION"),
        baseline_status="READY",
        candidates=candidates,
    )


def _learning_sample_count(request: DegradationDetectionInput) -> int | None:
    if not request.baselines:
        return 0
    counts = [baseline.sample_count for baseline in request.baselines.values()]
    if not counts:
        return 0
    minimum = min(counts)
    return minimum if minimum < 30 else None


def _deduplicate_candidates(candidates: list[DetectionCandidate]) -> list[DetectionCandidate]:
    severity_rank = {"LEARNING": 0, "WARNING": 1, "CRITICAL": 2}
    method_rank = {"ROBUST_Z_SCORE": 1, "TREND_PROJECTION": 2}
    selected: dict[tuple[str, str], DetectionCandidate] = {}
    for candidate in candidates:
        key = (candidate.anomaly_type, candidate.detection_method)
        current = selected.get(key)
        if current is None:
            selected[key] = candidate
            continue
        candidate_rank = (severity_rank.get(candidate.severity, 0), method_rank.get(candidate.detection_method, 0))
        current_rank = (severity_rank.get(current.severity, 0), method_rank.get(current.detection_method, 0))
        if candidate_rank > current_rank:
            selected[key] = candidate
    return list(selected.values())


def _overall_status(candidates: list[DetectionCandidate]) -> str:
    if any(candidate.severity == "CRITICAL" for candidate in candidates):
        return "CRITICAL"
    if any(candidate.severity == "WARNING" for candidate in candidates):
        return "WARNING"
    if candidates and all(candidate.severity == "LEARNING" for candidate in candidates):
        return "LEARNING"
    return "NONE"
