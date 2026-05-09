import asyncio
import base64
from datetime import datetime
from pathlib import Path

import cv2
import httpx
import numpy as np
from fastapi.testclient import TestClient

import app.api.routes.detection as detection_route
from app.main import app
from app.schemas.detection import DetectionResult
from app.services.inference_service import InferenceService
from app.services.plate_detector import PlateDetection
from app.services.plate_recognizer import PlateRecognition


client = TestClient(app)


def make_test_image_bytes() -> bytes:
    image = np.zeros((80, 160, 3), dtype=np.uint8)
    success, buffer = cv2.imencode(".jpg", image)

    assert success

    return buffer.tobytes()


def make_unrecognized_detection() -> DetectionResult:
    return DetectionResult(
        camera_code="CAM_001",
        plate_number=None,
        detection_type="VEHICLE",
        direction_type="IN",
        confidence_score=0.0,
        image_path="storage/detections/2026/04/30/CAM_001_103000_frame.jpg",
        image_url="/static/detections/2026/04/30/CAM_001_103000_frame.jpg",
        detected_at=datetime(2026, 4, 30, 10, 30, 0),
    )


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "traffic-ai-server",
    }


def test_create_mock_detection(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        "app.services.image_storage_service.IMAGE_STORAGE_DIR",
        str(tmp_path / "detections"),
    )

    image_bytes = make_test_image_bytes()

    body = {
        "cameraCode": "CAM_001",
        "capturedAt": "2026-04-30T10:30:00",
        "imageBase64": base64.b64encode(image_bytes).decode("ascii"),
    }

    response = client.post("/api/detections/mock", json=body)

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["cameraCode"] == "CAM_001"
    assert data["plateNumber"] == "123가4567"
    assert data["detectionType"] == "PLATE"
    assert data["directionType"] == "IN"
    assert data["confidenceScore"] == 0.9321
    assert data["imagePath"] is not None
    assert Path(data["imagePath"]).exists()
    assert data["imageUrl"].startswith("/static/detections/")


def test_create_mock_detection_with_invalid_base64() -> None:
    body = {
        "cameraCode": "CAM_001",
        "capturedAt": "2026-04-30T10:30:00",
        "imageBase64": "invalid-base64",
    }

    response = client.post("/api/detections/mock", json=body)

    assert response.status_code == 400
    assert response.json()["detail"] == "imageBase64 must be valid image base64"


def test_create_detection_from_image(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        "app.services.image_storage_service.IMAGE_STORAGE_DIR",
        str(tmp_path / "detections"),
    )

    image_bytes = make_test_image_bytes()

    response = client.post(
        "/api/detections/image",
        data={
            "cameraCode": "CAM_001",
            "capturedAt": "2026-04-30T10:30:00",
        },
        files={
            "image": ("sample.jpg", image_bytes, "image/jpeg"),
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["cameraCode"] == "CAM_001"
    assert data["plateNumber"] == "123가4567"
    assert data["imagePath"] is not None
    assert Path(data["imagePath"]).exists()
    assert data["imageUrl"].startswith("/static/detections/")


def test_detection_saves_frame_crop_and_ocr_images_when_enabled(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setattr(
        "app.services.image_storage_service.IMAGE_STORAGE_DIR",
        str(tmp_path / "detections"),
    )
    monkeypatch.setattr("app.services.inference_service.SAVE_PLATE_CROP", True)
    monkeypatch.setattr(
        "app.services.inference_service.SAVE_OCR_PREPROCESSED_IMAGE",
        True,
    )

    service = InferenceService()

    monkeypatch.setattr(
        service.plate_detector,
        "detect",
        lambda image: PlateDetection(
            detection_type="PLATE",
            confidence_score=0.9321,
            bbox=(10, 20, 80, 50),
        ),
    )
    monkeypatch.setattr(
        service.plate_recognizer,
        "recognize",
        lambda image: PlateRecognition(
            text="123A4567",
            confidence_score=0.95,
        ),
    )

    image_bytes = make_test_image_bytes()

    result = asyncio.run(
        service.detect_from_image_bytes(
            camera_code="CAM_001",
            captured_at=datetime(2026, 4, 30, 10, 30, 0),
            image_bytes=image_bytes,
        )
    )

    storage_dir = tmp_path / "detections" / "2026" / "04" / "30"

    assert result.image_path.endswith("CAM_001_103000_frame.jpg")
    assert (storage_dir / "CAM_001_103000_frame.jpg").exists()
    assert (storage_dir / "CAM_001_103000_plate_crop.jpg").exists()
    assert (storage_dir / "CAM_001_103000_ocr.jpg").exists()


def test_detection_can_reprocess_saved_image_without_resaving_frame(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setattr(
        "app.services.image_storage_service.IMAGE_STORAGE_DIR",
        str(tmp_path / "detections"),
    )
    monkeypatch.setattr("app.services.inference_service.SAVE_PLATE_CROP", True)
    monkeypatch.setattr(
        "app.services.inference_service.SAVE_OCR_PREPROCESSED_IMAGE",
        True,
    )

    service = InferenceService()

    monkeypatch.setattr(
        service.plate_detector,
        "detect",
        lambda image: PlateDetection(
            detection_type="PLATE",
            confidence_score=0.9321,
            bbox=(10, 20, 80, 50),
        ),
    )
    monkeypatch.setattr(
        service.plate_recognizer,
        "recognize",
        lambda image: PlateRecognition(
            text="123A4567",
            confidence_score=0.95,
        ),
    )

    storage_dir = tmp_path / "detections" / "2026" / "04" / "30"
    storage_dir.mkdir(parents=True)
    saved_image_path = storage_dir / "CAM_001_103000_frame.jpg"

    image = np.zeros((80, 160, 3), dtype=np.uint8)
    assert cv2.imwrite(str(saved_image_path), image)

    result = asyncio.run(
        service.detect_from_saved_image(
            camera_code="CAM_001",
            captured_at=datetime(2026, 4, 30, 10, 30, 0),
            image_path=str(saved_image_path),
        )
    )

    assert result.image_path == str(saved_image_path).replace("\\", "/")
    assert result.image_url.endswith("/2026/04/30/CAM_001_103000_frame.jpg")
    assert (storage_dir / "CAM_001_103000_plate_crop.jpg").exists()
    assert (storage_dir / "CAM_001_103000_ocr.jpg").exists()
    assert len(list(storage_dir.glob("*_frame.jpg"))) == 1



def test_create_detection_from_unsupported_file_type() -> None:
    response = client.post(
        "/api/detections/image",
        data={
            "cameraCode": "CAM_001",
            "capturedAt": "2026-04-30T10:30:00",
        },
        files={
            "image": ("sample.txt", b"not-image", "text/plain"),
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "image must be jpeg or png"


def test_create_detection_from_invalid_image_bytes() -> None:
    response = client.post(
        "/api/detections/image",
        data={
            "cameraCode": "CAM_001",
            "capturedAt": "2026-04-30T10:30:00",
        },
        files={
            "image": ("sample.jpg", b"not-valid-image", "image/jpeg"),
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "image must be a valid jpg or png"


def test_create_and_send_mock_detection_without_backend(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        "app.services.image_storage_service.IMAGE_STORAGE_DIR",
        str(tmp_path / "detections"),
    )

    async def raise_request_error(result):
        raise httpx.ConnectError("backend unavailable")

    monkeypatch.setattr(
        detection_route.backend_client,
        "send_detection",
        raise_request_error,
    )

    image_bytes = make_test_image_bytes()

    body = {
        "cameraCode": "CAM_001",
        "capturedAt": "2026-04-30T10:30:00",
        "imageBase64": base64.b64encode(image_bytes).decode("ascii"),
    }

    response = client.post("/api/detections/mock/send", json=body)

    assert response.status_code == 503
    assert response.json()["detail"] == "Spring Boot API is not reachable"


def test_create_and_send_mock_detection_skips_backend_when_plate_is_not_recognized(
    monkeypatch,
) -> None:
    async def return_unrecognized_detection(request):
        return make_unrecognized_detection()

    async def fail_if_called(result):
        raise AssertionError("backend should not be called for unrecognized plates")

    monkeypatch.setattr(
        detection_route.inference_service,
        "detect_from_frame",
        return_unrecognized_detection,
    )
    monkeypatch.setattr(
        detection_route.backend_client,
        "send_detection",
        fail_if_called,
    )

    image_bytes = make_test_image_bytes()
    body = {
        "cameraCode": "CAM_001",
        "capturedAt": "2026-04-30T10:30:00",
        "imageBase64": base64.b64encode(image_bytes).decode("ascii"),
    }

    response = client.post("/api/detections/mock/send", json=body)

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == (
        "Detection result created but not sent to backend because plate was not recognized"
    )
    assert body["data"]["plateNumber"] is None
    assert body["data"]["detectionType"] == "VEHICLE"


def test_create_and_send_image_detection_skips_backend_when_plate_is_not_recognized(
    monkeypatch,
) -> None:
    async def return_unrecognized_detection(*, camera_code, captured_at, image_bytes):
        return make_unrecognized_detection()

    async def fail_if_called(result):
        raise AssertionError("backend should not be called for unrecognized plates")

    monkeypatch.setattr(
        detection_route.inference_service,
        "detect_from_image_bytes",
        return_unrecognized_detection,
    )
    monkeypatch.setattr(
        detection_route.backend_client,
        "send_detection",
        fail_if_called,
    )

    response = client.post(
        "/api/detections/image/send",
        data={
            "cameraCode": "CAM_001",
            "capturedAt": "2026-04-30T10:30:00",
        },
        files={
            "image": ("sample.jpg", make_test_image_bytes(), "image/jpeg"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == (
        "Detection result created but not sent to backend because plate was not recognized"
    )
    assert body["data"]["plateNumber"] is None
    assert body["data"]["detectionType"] == "VEHICLE"
