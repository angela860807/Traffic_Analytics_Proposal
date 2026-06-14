import hashlib
import json
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

    camera_id: int
    evaluated_at: Any


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
                    "consecutiveWindows": 3,
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
    module.received = []

    def detect_rules(request):
        module.received.append(("rules", request))
        return {
            "detector": {
                "name": "camera-rule",
                "version": "1.1.0",
                "method": "RULE",
            },
            "evaluatedAt": request.evaluated_at,
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
            "evaluatedAt": request.evaluated_at,
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


def test_adapter_converts_fastapi_request_to_ai_contract() -> None:
    module = build_fake_module()
    adapter = PredictiveDetectorAdapter(module=module)

    response = adapter.evaluate_rules(make_rule_request())

    assert response.detector.method == "RULE"
    assert module.received[0][0] == "rules"
    assert isinstance(module.received[0][1], FakeContract)
    assert not isinstance(module.received[0][1], RuleEvaluationRequest)


def test_adapter_keeps_model_result_in_shadow_candidates() -> None:
    module = build_fake_module()
    adapter = PredictiveDetectorAdapter(module=module)

    response = adapter.evaluate_degradation(make_degradation_request())

    assert response.candidates == []
    assert len(response.shadow_candidates) == 1
    assert response.shadow_candidates[0].operating_mode == "SHADOW"
    assert [name for name, _ in module.received] == [
        "degradation",
        "shadow",
    ]


def test_adapter_skips_shadow_model_when_baseline_is_learning() -> None:
    module = build_fake_module(baseline_status="LEARNING")
    adapter = PredictiveDetectorAdapter(module=module)

    response = adapter.evaluate_degradation(make_degradation_request())

    assert response.baseline_status == "LEARNING"
    assert response.shadow_candidates == []
    assert [name for name, _ in module.received] == ["degradation"]


def test_artifact_validator_checks_hash_and_feature_order(tmp_path: Path) -> None:
    for filename in REQUIRED_ARTIFACT_FILES:
        path = tmp_path / filename
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
