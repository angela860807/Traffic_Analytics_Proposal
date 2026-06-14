from typing import Literal

from pydantic import AwareDatetime, Field

from app.schemas.camera_health import CameraHealthObservation, CameraHealthSchema


BaselineStatus = Literal["READY", "LEARNING"]
DetectionMethod = Literal[
    "RULE",
    "ROBUST_Z_SCORE",
    "TREND_PROJECTION",
    "CROSS_VALIDATION",
    "LSTM_AUTOENCODER",
]
DetectorOperatingMode = Literal["ACTIVE", "SHADOW", "EXPERIMENTAL"]
AnomalyType = Literal[
    "CAMERA_OFFLINE",
    "FPS_DEGRADATION",
    "FRAME_DROP_DEGRADATION",
    "LATENCY_DEGRADATION",
    "BLUR_DEGRADATION",
    "OCR_QUALITY_DEGRADATION",
    "RESOURCE_SATURATION",
    "NETWORK_INSTABILITY",
]
Severity = Literal["WARNING", "CRITICAL"]
TargetType = Literal["CAMERA"]


class RulePolicy(CameraHealthSchema):
    policy_code: str = Field(alias="policyCode", min_length=1, max_length=100)
    warning_threshold: float = Field(alias="warningThreshold")
    critical_threshold: float = Field(alias="criticalThreshold")
    consecutive_windows: int = Field(alias="consecutiveWindows", gt=0)


class RuleEvaluationRequest(CameraHealthSchema):
    camera_id: int = Field(alias="cameraId", gt=0)
    evaluated_at: AwareDatetime = Field(alias="evaluatedAt")
    samples: list[CameraHealthObservation] = Field(min_length=1)
    policies: list[RulePolicy] = Field(min_length=1)


class BaselineMetric(CameraHealthSchema):
    median: float
    mad: float = Field(ge=0)


class BaselineWindow(CameraHealthSchema):
    source: str = Field(min_length=1, max_length=100)
    from_at: AwareDatetime = Field(alias="from")
    to_at: AwareDatetime = Field(alias="to")
    sample_count: int = Field(alias="sampleCount", ge=0)
    metrics: dict[str, BaselineMetric]


class TrafficContext(CameraHealthSchema):
    current_camera_vehicle_count: int | None = Field(
        default=None,
        alias="currentCameraVehicleCount",
        ge=0,
    )
    adjacent_camera_vehicle_counts: dict[str, int] = Field(
        default_factory=dict,
        alias="adjacentCameraVehicleCounts",
    )
    quality_status: Literal["COMPLETE", "PARTIAL", "INSUFFICIENT"] = Field(
        alias="qualityStatus"
    )


class DegradationPolicy(CameraHealthSchema):
    policy_code: str = Field(alias="policyCode", min_length=1, max_length=100)
    window_minutes: int = Field(alias="windowMinutes", gt=0)
    minimum_valid_samples: int = Field(alias="minimumValidSamples", gt=0)
    ewma_alpha: float = Field(alias="ewmaAlpha", gt=0, le=1)
    minimum_trend_confidence: float = Field(
        alias="minimumTrendConfidence",
        ge=0,
        le=1,
    )
    prediction_horizon_minutes: int = Field(
        alias="predictionHorizonMinutes",
        gt=0,
    )


class DegradationEvaluationRequest(CameraHealthSchema):
    camera_id: int = Field(alias="cameraId", gt=0)
    evaluated_at: AwareDatetime = Field(alias="evaluatedAt")
    recent_health_samples: list[CameraHealthObservation] = Field(
        alias="recentHealthSamples"
    )
    baseline: BaselineWindow
    traffic_context: TrafficContext = Field(alias="trafficContext")
    policy: DegradationPolicy


class DetectorDescriptor(CameraHealthSchema):
    name: str = Field(min_length=1, max_length=100)
    version: str = Field(min_length=1, max_length=50)
    method: DetectionMethod


class TrendEvidence(CameraHealthSchema):
    slope: float
    confidence: float = Field(ge=0, le=1)
    prediction_horizon_minutes: int = Field(
        alias="predictionHorizonMinutes",
        gt=0,
    )
    projected_threshold_crossing_at: AwareDatetime | None = Field(
        default=None,
        alias="projectedThresholdCrossingAt",
    )


class MetricEvidence(CameraHealthSchema):
    metric_name: str = Field(alias="metricName", min_length=1, max_length=100)
    observed_value: float | None = Field(default=None, alias="observedValue")
    baseline_value: float | None = Field(default=None, alias="baselineValue")
    threshold_value: float | None = Field(default=None, alias="thresholdValue")
    metric_score: float | None = Field(default=None, alias="metricScore")
    unit: str | None = Field(default=None, max_length=30)
    sampled_at: AwareDatetime = Field(alias="sampledAt")
    context: dict[str, bool | int | float | str | None] = Field(
        default_factory=dict
    )


class DetectionCandidate(CameraHealthSchema):
    target_type: TargetType = Field(default="CAMERA", alias="targetType")
    camera_id: int = Field(alias="cameraId", gt=0)
    anomaly_type: AnomalyType = Field(alias="anomalyType")
    severity: Severity
    anomaly_score: float = Field(alias="anomalyScore", ge=0, le=1)
    policy_code: str = Field(alias="policyCode", min_length=1, max_length=100)
    trend: TrendEvidence | None = None
    suspected_causes: list[str] = Field(
        default_factory=list,
        alias="suspectedCauses",
    )
    evidence: list[MetricEvidence] = Field(default_factory=list)


class TopFeature(CameraHealthSchema):
    feature_name: str = Field(alias="featureName", min_length=1, max_length=100)
    feature_value: float = Field(alias="featureValue", ge=0)


class ShadowPrediction(CameraHealthSchema):
    target_type: TargetType = Field(default="CAMERA", alias="targetType")
    camera_id: int = Field(alias="cameraId", gt=0)
    detection_method: Literal["LSTM_AUTOENCODER"] = Field(
        default="LSTM_AUTOENCODER",
        alias="detectionMethod",
    )
    operating_mode: Literal["SHADOW"] = Field(
        default="SHADOW",
        alias="operatingMode",
    )
    anomaly_score: float = Field(alias="anomalyScore", ge=0, le=1)
    warning_threshold: float = Field(alias="warningThreshold", ge=0, le=1)
    critical_threshold: float = Field(alias="criticalThreshold", ge=0, le=1)
    predicted_anomaly: bool = Field(alias="predictedAnomaly")
    predicted_severity: Severity | None = Field(
        default=None,
        alias="predictedSeverity",
    )
    input_window_from: AwareDatetime = Field(alias="inputWindowFrom")
    input_window_to: AwareDatetime = Field(alias="inputWindowTo")
    feature_schema_version: str = Field(
        alias="featureSchemaVersion",
        min_length=1,
        max_length=100,
    )
    top_features: list[TopFeature] = Field(
        default_factory=list,
        alias="topFeatures",
    )


class DetectionEvaluationResponse(CameraHealthSchema):
    detector: DetectorDescriptor
    evaluated_at: AwareDatetime = Field(alias="evaluatedAt")
    baseline_status: BaselineStatus | None = Field(
        default=None,
        alias="baselineStatus",
    )
    required_sample_count: int | None = Field(
        default=None,
        alias="requiredSampleCount",
        ge=0,
    )
    current_sample_count: int | None = Field(
        default=None,
        alias="currentSampleCount",
        ge=0,
    )
    candidates: list[DetectionCandidate] = Field(default_factory=list)
    shadow_candidates: list[ShadowPrediction] = Field(
        default_factory=list,
        alias="shadowCandidates",
    )


class DetectorHealth(CameraHealthSchema):
    name: str = Field(min_length=1, max_length=100)
    version: str = Field(min_length=1, max_length=50)
    method: DetectionMethod | None = None
    operating_mode: DetectorOperatingMode | None = Field(
        default=None,
        alias="operatingMode",
    )
    model_format: str | None = Field(
        default=None,
        alias="modelFormat",
        max_length=100,
    )
    feature_schema_version: str | None = Field(
        default=None,
        alias="featureSchemaVersion",
        max_length=100,
    )
    active: bool


class DetectorHealthResponse(CameraHealthSchema):
    status: Literal["UP", "DEGRADED", "DOWN"]
    package_version: str | None = Field(
        default=None,
        alias="packageVersion",
        max_length=100,
    )
    detectors: list[DetectorHealth] = Field(default_factory=list)
    artifact_status: Literal[
        "READY",
        "NOT_CONFIGURED",
        "MISSING",
        "INVALID",
    ] = Field(default="NOT_CONFIGURED", alias="artifactStatus")
    artifact_errors: list[str] = Field(
        default_factory=list,
        alias="artifactErrors",
    )
