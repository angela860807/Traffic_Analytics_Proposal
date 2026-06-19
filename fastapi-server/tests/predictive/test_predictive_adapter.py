import hashlib
import json
import logging
from pathlib import Path
from types import ModuleType
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.predictive_detection import (
    DegradationEvaluationRequest,
    RuleEvaluationRequest,
)
from app.services.predictive_artifacts import (
    EXPECTED_FEATURES,
    REQUIRED_ARTIFACT_FILES,
    PredictiveArtifactValidator,
)
from app.services.predictive_detector_adapter import PredictiveDetectorAdapter


EVALUATED_AT = "2026-06-14T12:05:00+09:00"


class FakeContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    sample: Any | None = None
    consecutive_windows: dict[str, int] = {}
    baselines: dict[str, Any] = {}
    trends: dict[str, list[Any]] = {}
    prediction_horizon_minutes: int | None = None
    camera_id: int | None = None
    sampled_at: Any | None = None
    sequence: list[Any] = []


class FakeStruct:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def make_rule_request() -> RuleEvaluationRequest:
    return RuleEvaluationRequest.model_validate(
        {
            "cameraId": 1,
            "evaluatedAt": EVALUATED_AT,
            "samples": [
                {
                    "sampledAt": "2026-06-14T12:04:00+09:00",
                    "fpsAvg": 4.8,
                    "qualityStatus": "COMPLETE",
                }
            ],
            "policies": [
                {
                    "policyCode": "FPS_DEGRADATION_RULE_V1",
                    "warningThreshold": 10,
                    "criticalThreshold": 5,
                    "warningConsecutiveWindows": 3,
                    "criticalConsecutiveWindows": 3,
                }
            ],
        }
    )


def make_degradation_request() -> DegradationEvaluationRequest:
    return DegradationEvaluationRequest.model_validate(
        {
            "cameraId": 1,
            "evaluatedAt": EVALUATED_AT,
            "recentHealthSamples": [
                {
                    "sampledAt": "2026-06-14T12:04:00+09:00",
                    "fpsAvg": 11.2,
                    "qualityStatus": "COMPLETE",
                }
            ],
            "baseline": {
                "source": "CAMERA_30_MINUTE_BUCKET_14D",
                "from": "2026-05-31T12:00:00+09:00",
                "to": "2026-06-14T12:00:00+09:00",
                "sampleCount": 54,
                "metrics": {"fpsAvg": {"median": 24.1, "mad": 2.1}},
            },
            "trafficContext": {
                "currentCameraVehicleCount": 8,
                "adjacentCameraVehicleCounts": {"2": 43},
                "qualityStatus": "COMPLETE",
            },
            "policy": {
                "policyCode": "CAMERA_TREND_PROJECTION_V1",
                "windowMinutes": 15,
                "minimumValidSamples": 12,
                "ewmaAlpha": 0.3,
                "minimumTrendConfidence": 0.6,
                "predictionHorizonMinutes": 10,
            },
        }
    )


def build_fake_module(*, baseline_status: str = "READY") -> ModuleType:
    module = ModuleType("predictive_ml")
    module.__version__ = "0.2.0"
    module.RuleDetectionInput = FakeContract
    module.DegradationDetectionInput = FakeContract
    module.ModelPredictionInput = FakeContract
    module.CameraSample = FakeStruct
    module.BaselineMetric = FakeStruct
    module.TrendPoint = FakeStruct
    module.received = []

    def detect_rules(request):
        module.received.append(("rules", request))
        return {
            "detector": {
                "name": "camera-rule",
                "version": "1.1.0",
                "method": "RULE",
            },
            "evaluatedAt": request.sample.sampled_at,
            "candidates": [],
        }

    def detect_degradation(request):
        module.received.append(("degradation", request))
        return {
            "detector": {
                "name": "camera-trend-projection",
                "version": "1.0.0",
                "method": "TREND_PROJECTION",
            },
            "evaluatedAt": request.sample.sampled_at,
            "baselineStatus": baseline_status,
            "candidates": [],
        }

    def predict_anomaly(request):
        module.received.append(("shadow", request))
        return {
            "targetType": "CAMERA",
            "cameraId": request.camera_id,
            "detectionMethod": "LSTM_AUTOENCODER",
            "operatingMode": "SHADOW",
            "anomalyScore": 0.91,
            "warningThreshold": 0.72,
            "criticalThreshold": 0.82,
            "predictedAnomaly": True,
            "predictedSeverity": "CRITICAL",
            "inputWindowFrom": "2026-06-14T11:05:00+09:00",
            "inputWindowTo": EVALUATED_AT,
            "featureSchemaVersion": "camera-health-sequence-v1",
            "topFeatures": [],
        }

    def get_detector_manifest():
        return [
            {
                "name": "camera-rule",
                "version": "1.1.0",
                "method": "RULE",
                "operatingMode": "ACTIVE",
                "active": True,
            }
        ]

    module.detect_rules = detect_rules
    module.detect_degradation = detect_degradation
    module.predict_anomaly = predict_anomaly
    module.get_detector_manifest = get_detector_manifest
    return module


def write_valid_artifacts(model_dir: Path) -> None:
    model_dir.mkdir(parents=True, exist_ok=True)
    for filename in REQUIRED_ARTIFACT_FILES:
        path = model_dir / filename
        if filename == "feature_schema.json":
            path.write_text(
                json.dumps(
                    {
                        "featureSchemaVersion": "camera-health-sequence-v1",
                        "features": list(EXPECTED_FEATURES),
                    }
                ),
                encoding="utf-8",
            )
        else:
            path.write_bytes(filename.encode("utf-8"))


def test_adapter_converts_fastapi_request_to_ai_contract() -> None:
    module = build_fake_module()
    adapter = PredictiveDetectorAdapter(module=module)

    response = adapter.evaluate_rules(make_rule_request())

    assert response.detector.method == "RULE"
    assert module.received[0][0] == "rules"
    assert isinstance(module.received[0][1], FakeContract)
    assert not isinstance(module.received[0][1], RuleEvaluationRequest)


def test_adapter_keeps_model_result_in_shadow_candidates(
    tmp_path: Path,
) -> None:
    module = build_fake_module()
    write_valid_artifacts(tmp_path)
    adapter = PredictiveDetectorAdapter(
        module=module,
        model_dir=str(tmp_path),
        artifact_required=True,
    )

    response = adapter.evaluate_degradation(make_degradation_request())

    assert response.candidates == []
    assert len(response.shadow_candidates) == 1
    assert response.shadow_candidates[0].operating_mode == "SHADOW"
    assert [name for name, _ in module.received] == [
        "degradation",
        "shadow",
    ]


def test_adapter_logs_package_and_artifact_status_once(
    tmp_path: Path,
    caplog,
) -> None:
    module = build_fake_module()
    write_valid_artifacts(tmp_path)
    adapter = PredictiveDetectorAdapter(
        module=module,
        model_dir=str(tmp_path),
        artifact_required=True,
    )
    caplog.set_level(
        logging.INFO,
        logger="app.services.predictive_detector_adapter",
    )

    adapter.initialize()
    adapter.initialize()

    startup_logs = [
        record.getMessage()
        for record in caplog.records
        if "predictive detector initialized" in record.getMessage()
    ]
    assert len(startup_logs) == 1
    assert "packageVersion=0.2.0" in startup_logs[0]
    assert "artifactStatus=READY" in startup_logs[0]


def test_adapter_skips_shadow_model_when_baseline_is_learning() -> None:
    module = build_fake_module(baseline_status="LEARNING")
    adapter = PredictiveDetectorAdapter(module=module)

    response = adapter.evaluate_degradation(make_degradation_request())

    assert response.baseline_status == "LEARNING"
    assert response.shadow_candidates == []
    assert [name for name, _ in module.received] == ["degradation"]


def test_adapter_skips_shadow_model_when_artifacts_are_not_configured(
    tmp_path: Path,
) -> None:
    module = build_fake_module()
    model_dir = tmp_path / "not-configured"
    adapter = PredictiveDetectorAdapter(
        module=module,
        model_dir=str(model_dir),
        artifact_required=False,
    )

    response = adapter.evaluate_degradation(make_degradation_request())
    health = adapter.get_health()

    assert response.shadow_candidates == []
    assert [name for name, _ in module.received] == ["degradation"]
    assert health.status == "DEGRADED"
    assert health.artifact_status == "NOT_CONFIGURED"


def test_adapter_skips_shadow_model_when_required_artifacts_are_missing(
    tmp_path: Path,
) -> None:
    module = build_fake_module()
    model_dir = tmp_path / "missing"
    adapter = PredictiveDetectorAdapter(
        module=module,
        model_dir=str(model_dir),
        artifact_required=True,
    )

    response = adapter.evaluate_degradation(make_degradation_request())
    health = adapter.get_health()

    assert response.shadow_candidates == []
    assert [name for name, _ in module.received] == ["degradation"]
    assert health.status == "DEGRADED"
    assert health.artifact_status == "MISSING"


def test_adapter_skips_shadow_model_when_artifacts_are_invalid(
    tmp_path: Path,
) -> None:
    module = build_fake_module()
    adapter = PredictiveDetectorAdapter(
        module=module,
        model_dir=str(tmp_path),
        artifact_required=True,
    )

    response = adapter.evaluate_degradation(make_degradation_request())
    health = adapter.get_health()

    assert response.shadow_candidates == []
    assert [name for name, _ in module.received] == ["degradation"]
    assert health.status == "DEGRADED"
    assert health.artifact_status == "INVALID"


def test_artifact_validator_checks_hash_and_feature_order(tmp_path: Path) -> None:
    write_valid_artifacts(tmp_path)

    model_hash = hashlib.sha256(
        (tmp_path / "lstm_ae.pt").read_bytes()
    ).hexdigest()
    status = PredictiveArtifactValidator(
        model_dir=tmp_path,
        required=True,
        expected_sha256={"lstm_ae.pt": model_hash},
    ).inspect()

    assert status.status == "READY"
    assert status.feature_schema_version == "camera-health-sequence-v1"
    assert set(status.verified_files) == set(REQUIRED_ARTIFACT_FILES)
