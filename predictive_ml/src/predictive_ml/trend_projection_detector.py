from __future__ import annotations

from datetime import timedelta
from itertools import combinations
from math import sqrt

from .contracts import DetectionCandidate, Evidence, TrendPoint
from .policies import METRIC_ANOMALY_TYPES, METRIC_DIRECTIONS, METRIC_UNITS, RULE_THRESHOLDS, SUSPECTED_CAUSES

DETECTOR_NAME = "camera-trend-projection"
DETECTOR_VERSION = "1.0.0"
EWMA_ALPHA = 0.3
MIN_VALID_POINTS = 12
MIN_CONFIDENCE = 0.60


def detect_trend_projection(
    trends: dict[str, list[TrendPoint]],
    prediction_horizon_minutes: int = 10,
) -> list[DetectionCandidate]:
    candidates: list[DetectionCandidate] = []
    for metric_name, points in trends.items():
        if metric_name not in METRIC_DIRECTIONS or metric_name not in RULE_THRESHOLDS:
            continue
        valid_points = _valid_points(points)
        if len(valid_points) < MIN_VALID_POINTS:
            continue

        timestamps = [point.sampled_at for point in valid_points]
        values = [float(point.value) for point in valid_points if point.value is not None]
        smoothed = _ewma(values, EWMA_ALPHA)
        minutes = [(ts - timestamps[0]).total_seconds() / 60.0 for ts in timestamps]
        slope = _theil_sen_slope(minutes, smoothed)
        confidence = abs(_spearman_correlation(minutes, smoothed))
        direction = METRIC_DIRECTIONS[metric_name]
        if confidence < MIN_CONFIDENCE or not _is_worsening_slope(slope, direction):
            continue

        thresholds = RULE_THRESHOLDS[metric_name]
        for severity, threshold_name in (("CRITICAL", "critical"), ("WARNING", "warning")):
            crossing_at = _project_crossing(
                last_time=timestamps[-1],
                last_value=smoothed[-1],
                slope=slope,
                threshold=thresholds[threshold_name],
                direction=direction,
                horizon_minutes=prediction_horizon_minutes,
            )
            if crossing_at is None:
                continue
            anomaly_type = METRIC_ANOMALY_TYPES[metric_name]
            candidates.append(
                DetectionCandidate(
                    anomaly_type=anomaly_type,
                    severity=severity,
                    detection_method="TREND_PROJECTION",
                    policy_code="CAMERA_TREND_PROJECTION_V1",
                    detector_name=DETECTOR_NAME,
                    detector_version=DETECTOR_VERSION,
                    anomaly_score=min(1.0, confidence),
                    projected_threshold_crossing_at=crossing_at,
                    trend_slope=slope,
                    trend_confidence=confidence,
                    evidence=[
                        Evidence(
                            metric_name=metric_name,
                            observed_value=smoothed[-1],
                            threshold_value=thresholds[threshold_name],
                            metric_score=confidence,
                            unit=METRIC_UNITS.get(metric_name),
                            context={
                                "ewmaAlpha": EWMA_ALPHA,
                                "validPoints": len(valid_points),
                                "minimumValidPoints": MIN_VALID_POINTS,
                                "slopePerMinute": slope,
                                "spearmanConfidence": confidence,
                                "predictionHorizonMinutes": prediction_horizon_minutes,
                            },
                        )
                    ],
                    suspected_causes=SUSPECTED_CAUSES.get(anomaly_type, ["UNKNOWN"]),
                )
            )
            break
    return candidates


def _valid_points(points: list[TrendPoint]) -> list[TrendPoint]:
    return [
        point
        for point in sorted(points, key=lambda item: item.sampled_at)
        if point.value is not None
        and point.quality_status == "COMPLETE"
        and not point.is_imputed
        and not point.is_late_sample
    ]


def _ewma(values: list[float], alpha: float) -> list[float]:
    smoothed: list[float] = []
    for value in values:
        if not smoothed:
            smoothed.append(value)
        else:
            smoothed.append(alpha * value + (1.0 - alpha) * smoothed[-1])
    return smoothed


def _theil_sen_slope(x_values: list[float], y_values: list[float]) -> float:
    slopes = [
        (y2 - y1) / (x2 - x1)
        for (x1, y1), (x2, y2) in combinations(zip(x_values, y_values), 2)
        if x2 != x1
    ]
    if not slopes:
        return 0.0
    slopes.sort()
    mid = len(slopes) // 2
    if len(slopes) % 2:
        return slopes[mid]
    return (slopes[mid - 1] + slopes[mid]) / 2.0


def _spearman_correlation(x_values: list[float], y_values: list[float]) -> float:
    if len(x_values) < 2:
        return 0.0
    x_rank = _rank(x_values)
    y_rank = _rank(y_values)
    x_mean = sum(x_rank) / len(x_rank)
    y_mean = sum(y_rank) / len(y_rank)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_rank, y_rank))
    x_var = sum((x - x_mean) ** 2 for x in x_rank)
    y_var = sum((y - y_mean) ** 2 for y in y_rank)
    denominator = sqrt(x_var * y_var)
    return numerator / denominator if denominator else 0.0


def _rank(values: list[float]) -> list[float]:
    ordered = sorted((value, index) for index, value in enumerate(values))
    ranks = [0.0] * len(values)
    i = 0
    while i < len(ordered):
        j = i
        while j + 1 < len(ordered) and ordered[j + 1][0] == ordered[i][0]:
            j += 1
        avg_rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[ordered[k][1]] = avg_rank
        i = j + 1
    return ranks


def _is_worsening_slope(slope: float, direction: str) -> bool:
    if direction == "LOWER_IS_WORSE":
        return slope < 0
    return slope > 0


def _project_crossing(
    last_time,
    last_value: float,
    slope: float,
    threshold: float,
    direction: str,
    horizon_minutes: int,
):
    if slope == 0:
        return None
    minutes_to_cross = (threshold - last_value) / slope
    if minutes_to_cross <= 0 or minutes_to_cross > horizon_minutes:
        return None
    projected_value = last_value + slope * minutes_to_cross
    if direction == "LOWER_IS_WORSE" and projected_value > threshold:
        return None
    if direction == "HIGHER_IS_WORSE" and projected_value < threshold:
        return None
    return last_time + timedelta(minutes=minutes_to_cross)
