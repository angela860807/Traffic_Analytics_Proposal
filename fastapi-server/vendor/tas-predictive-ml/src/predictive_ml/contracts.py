from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal


Severity = Literal["NONE", "WARNING", "CRITICAL", "LEARNING"]
BaselineStatus = Literal["READY", "LEARNING"]
DetectionMethod = Literal[
    "RULE",
    "ROBUST_Z_SCORE",
    "TREND_PROJECTION",
    "CROSS_VALIDATION",
    "LSTM_AUTOENCODER",
]


@dataclass(frozen=True)
class DetectorInfo:
    name: str
    version: str
    method: DetectionMethod


@dataclass(frozen=True)
class CameraSample:
    camera_id: int
    sampled_at: datetime
    fps_avg: float | None = None
    frame_drop_rate: float | None = None
    latency_p95_ms: float | None = None
    blur_score_avg: float | None = None
    ocr_fail_rate: float | None = None
    cpu_usage_pct: float | None = None
    memory_usage_pct: float | None = None
    network_rtt_ms: float | None = None
    last_frame_age_seconds: float | None = None
    ocr_attempt_count: int | None = None
    data_source: str = "REAL"
    quality_status: str = "COMPLETE"
    is_imputed: bool = False
    is_late_sample: bool = False


@dataclass(frozen=True)
class TrendPoint:
    sampled_at: datetime
    value: float | None
    quality_status: str = "COMPLETE"
    is_imputed: bool = False
    is_late_sample: bool = False


@dataclass(frozen=True)
class BaselineMetric:
    median: float | None
    mad: float | None
    sample_count: int
    baseline_from: datetime | None = None
    baseline_to: datetime | None = None
    data_source: str = "REAL"


@dataclass(frozen=True)
class Evidence:
    metric_name: str
    observed_value: float | None
    threshold_value: float | None = None
    baseline_value: float | None = None
    metric_score: float | None = None
    unit: str | None = None
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ShadowTopFeature:
    feature_name: str
    feature_value: float


@dataclass(frozen=True)
class DetectionCandidate:
    anomaly_type: str
    severity: Severity
    detection_method: DetectionMethod
    policy_code: str
    detector_name: str
    detector_version: str
    anomaly_score: float | None = None
    evidence: list[Evidence] = field(default_factory=list)
    suspected_causes: list[str] = field(default_factory=list)
    projected_threshold_crossing_at: datetime | None = None
    trend_slope: float | None = None
    trend_confidence: float | None = None


@dataclass(frozen=True)
class DetectionResult:
    camera_id: int
    evaluated_at: datetime
    status: Severity
    detector: DetectorInfo
    baseline_status: BaselineStatus = "READY"
    candidates: list[DetectionCandidate] = field(default_factory=list)
    required_sample_count: int | None = None
    current_sample_count: int | None = None
    skipped_reason: str | None = None


@dataclass(frozen=True)
class RuleDetectionInput:
    sample: CameraSample
    consecutive_windows: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class DegradationDetectionInput:
    sample: CameraSample
    baselines: dict[str, BaselineMetric] = field(default_factory=dict)
    trends: dict[str, list[TrendPoint]] = field(default_factory=dict)
    prediction_horizon_minutes: int = 10


@dataclass(frozen=True)
class ModelPredictionInput:
    camera_id: int
    sampled_at: datetime
    sequence: list[CameraSample]


@dataclass(frozen=True)
class ShadowPredictionResult:
    camera_id: int
    evaluated_at: datetime
    input_window_from: datetime | None = None
    input_window_to: datetime | None = None
    target_type: Literal["CAMERA"] = "CAMERA"
    detection_method: Literal["LSTM_AUTOENCODER"] = "LSTM_AUTOENCODER"
    operating_mode: Literal["SHADOW"] = "SHADOW"
    detector_name: str = "camera-lstm-autoencoder"
    detector_version: str = "1.0.0"
    anomaly_score: float | None = None
    warning_threshold: float | None = None
    critical_threshold: float | None = None
    predicted_anomaly: bool = False
    predicted_severity: Literal["WARNING", "CRITICAL"] | None = None
    feature_schema_version: str = "camera-health-sequence-v1"
    top_features: list[ShadowTopFeature] = field(default_factory=list)
    skipped_reason: str | None = None
