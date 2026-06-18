from fastapi.testclient import TestClient

from app.api.routes.predictive_detection import (
    get_predictive_detector_adapter,
)
import app.core.middleware as middleware
import app.core.security as security
from app.main import app
from app.services.predictive_detector_adapter import PredictiveDetectorAdapter

from .test_predictive_adapter import (
    build_fake_module,
    make_degradation_request,
    make_rule_request,
    write_valid_artifacts,
)


def test_validation_error_uses_common_contract_and_request_id(
    monkeypatch,
) -> None:
    monkeypatch.setattr(security, "BACKEND_INTERNAL_API_KEY", "secret")
    request_id = "25e3259d-7bbf-41af-a81c-43ec67550867"

    with TestClient(app) as client:
        response = client.post(
            "/internal/v1/anomaly-detection/camera-health/evaluate",
            headers={
                "X-Internal-Api-Key": "secret",
                "X-Request-Id": request_id,
            },
            json={"cameraId": 0},
        )

    assert response.status_code == 400
    assert response.headers["X-Request-Id"] == request_id
    assert response.json()["code"] == "INVALID_REQUEST"
    assert response.json()["requestId"] == request_id
    assert response.json()["fieldErrors"]


def test_internal_api_rejects_oversized_body(monkeypatch) -> None:
    monkeypatch.setattr(security, "BACKEND_INTERNAL_API_KEY", "secret")
    monkeypatch.setattr(middleware, "INTERNAL_API_MAX_BODY_BYTES", 32)

    with TestClient(app) as client:
        response = client.post(
            "/internal/v1/anomaly-detection/camera-health/evaluate",
            headers={"X-Internal-Api-Key": "secret"},
            content=b'{"payload":"' + (b"x" * 64) + b'"}',
        )

    assert response.status_code == 413
    assert response.json()["code"] == "INVALID_REQUEST"
    assert response.headers["X-Request-Id"] == response.json()["requestId"]


def test_predictive_metrics_requires_internal_api_key(monkeypatch) -> None:
    monkeypatch.setattr(security, "BACKEND_INTERNAL_API_KEY", "secret")

    with TestClient(app) as client:
        unauthorized = client.get(
            "/internal/v1/anomaly-detection/metrics"
        )
        authorized = client.get(
            "/internal/v1/anomaly-detection/metrics",
            headers={"X-Internal-Api-Key": "secret"},
        )

    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
    payload = authorized.json()
    assert "endpoints" in payload
    assert "detectors" in payload
    assert "delivery" in payload


def test_two_predictive_endpoints_accept_handoff_fixtures(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setattr(security, "BACKEND_INTERNAL_API_KEY", "secret")
    write_valid_artifacts(tmp_path)
    adapter = PredictiveDetectorAdapter(
        module=build_fake_module(),
        model_dir=str(tmp_path),
        artifact_required=True,
    )
    app.dependency_overrides[get_predictive_detector_adapter] = lambda: adapter

    try:
        with TestClient(app) as client:
            rule_response = client.post(
                "/internal/v1/anomaly-detection/camera-health/evaluate",
                headers={"X-Internal-Api-Key": "secret"},
                json=make_rule_request().model_dump(
                    by_alias=True,
                    mode="json",
                ),
            )
            degradation_response = client.post(
                "/internal/v1/anomaly-detection/camera-degradation/evaluate",
                headers={"X-Internal-Api-Key": "secret"},
                json=make_degradation_request().model_dump(
                    by_alias=True,
                    mode="json",
                ),
            )
    finally:
        app.dependency_overrides.clear()

    assert rule_response.status_code == 200
    assert rule_response.json()["detector"]["method"] == "RULE"
    assert degradation_response.status_code == 200
    assert degradation_response.json()["baselineStatus"] == "READY"
    assert len(degradation_response.json()["shadowCandidates"]) == 1
