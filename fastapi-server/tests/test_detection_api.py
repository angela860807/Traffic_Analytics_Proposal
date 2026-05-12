import asyncio
import base64
from datetime import datetime
import logging
from pathlib import Path

import cv2
import httpx
import numpy as np
from fastapi.testclient import TestClient

import app.api.routes.detection as detection_route
from app.main import app
from app.schemas.detection import DetectionResult
import app.services.image_preprocessor as image_preprocessor
from app.services.inference_service import InferenceService
from app.services.plate_detector import PlateDetection
from app.services.plate_recognizer import PlateRecognition, PlateRecognizer


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


def make_recognized_detection(
    detected_at: datetime = datetime(2026, 4, 30, 10, 30, 0),
) -> DetectionResult:
    return DetectionResult(
        camera_code="CAM_001",
        plate_number="123A4567",
        detection_type="PLATE",
        direction_type="IN",
        confidence_score=0.9321,
        image_path="storage/detections/2026/04/30/CAM_001_103000_frame.jpg",
        image_url="/static/detections/2026/04/30/CAM_001_103000_frame.jpg",
        detected_at=detected_at,
    )


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "traffic-ai-server",
    }


def test_plate_number_normalization_keeps_korean_plate_characters() -> None:
    recognizer = PlateRecognizer()

    cases = {
        "서울 12가 3456": "서울12가3456",
        "123가4567": "123가4567",
        "ABC123가4567!!": "123가4567",
        "  경기 78나 9012\n": "경기78나9012",
        None: None,
        "ABC-!!": None,
    }

    for raw_text, expected in cases.items():
        assert recognizer._normalize_plate_number(raw_text) == expected


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


def test_detection_preprocess_none_keeps_frame_unchanged(monkeypatch) -> None:
    monkeypatch.setattr(image_preprocessor, "DETECTION_PREPROCESS_MODE", "none")

    image = np.zeros((80, 160, 3), dtype=np.uint8)
    preprocessed = image_preprocessor.preprocess_frame_for_detection(image)

    assert preprocessed is image


def test_detection_preprocess_standard_keeps_shape(monkeypatch) -> None:
    monkeypatch.setattr(image_preprocessor, "DETECTION_PREPROCESS_MODE", "standard")

    image = np.zeros((80, 160, 3), dtype=np.uint8)
    preprocessed = image_preprocessor.preprocess_frame_for_detection(image)

    assert preprocessed.shape == image.shape
    assert preprocessed.dtype == image.dtype


def test_inference_uses_detection_preprocess_before_detector(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setattr(
        "app.services.image_storage_service.IMAGE_STORAGE_DIR",
        str(tmp_path / "detections"),
    )
    monkeypatch.setattr("app.services.inference_service.SAVE_PLATE_CROP", False)
    monkeypatch.setattr(
        "app.services.inference_service.SAVE_OCR_PREPROCESSED_IMAGE",
        False,
    )

    service = InferenceService()
    original_image_ids = []
    detector_image_ids = []

    def fake_preprocess(image):
        original_image_ids.append(id(image))
        return image.copy()

    def fake_detect(image):
        detector_image_ids.append(id(image))
        return PlateDetection(
            detection_type="VEHICLE",
            confidence_score=0.0,
            bbox=None,
        )

    monkeypatch.setattr(
        "app.services.inference_service.preprocess_frame_for_detection",
        fake_preprocess,
    )
    monkeypatch.setattr(service.plate_detector, "detect", fake_detect)

    result = asyncio.run(
        service.detect_from_image_bytes(
            camera_code="CAM_001",
            captured_at=datetime(2026, 4, 30, 10, 30, 0),
            image_bytes=make_test_image_bytes(),
        )
    )

    assert result.detection_type == "VEHICLE"
    assert len(original_image_ids) == 1
    assert len(detector_image_ids) == 1
    assert detector_image_ids[0] != original_image_ids[0]


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

    async def raise_request_error(result, detection_status=None):
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


def test_create_and_send_mock_detection_includes_spring_error_body(
    monkeypatch,
    tmp_path,
    caplog,
) -> None:
    monkeypatch.setattr(
        "app.services.image_storage_service.IMAGE_STORAGE_DIR",
        str(tmp_path / "detections"),
    )

    async def raise_spring_error(result, detection_status=None):
        request = httpx.Request("POST", "http://spring/api/v1/detection-logs")
        response = httpx.Response(
            status_code=500,
            text='{"code":"SERVER_ERROR","message":"column \\"status\\" does not exist"}',
            request=request,
        )
        raise httpx.HTTPStatusError(
            "Spring server error",
            request=request,
            response=response,
        )

    monkeypatch.setattr(
        detection_route.backend_client,
        "send_detection",
        raise_spring_error,
    )
    caplog.set_level(logging.WARNING, logger="app.api.routes.detection")

    image_bytes = make_test_image_bytes()
    body = {
        "cameraCode": "CAM_001",
        "capturedAt": "2026-04-30T10:30:00",
        "imageBase64": base64.b64encode(image_bytes).decode("ascii"),
    }

    response = client.post("/api/detections/mock/send", json=body)

    assert response.status_code == 502
    detail = response.json()["detail"]
    assert "Spring Boot API returned error: 500" in detail
    assert "status" in detail
    assert "does not exist" in detail
    assert "status" in caplog.text
    assert "does not exist" in caplog.text


def test_create_and_send_mock_detection_sends_ocr_failed_when_plate_is_not_recognized(
    monkeypatch,
) -> None:
    sent_statuses = []

    async def return_unrecognized_detection(request):
        return make_unrecognized_detection()

    async def record_backend_send(result, detection_status=None):
        sent_statuses.append(detection_status)

    monkeypatch.setattr(
        detection_route.inference_service,
        "detect_from_frame",
        return_unrecognized_detection,
    )
    monkeypatch.setattr(
        detection_route.backend_client,
        "send_detection",
        record_backend_send,
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
        "Detection result sent to backend as OCR_FAILED"
    )
    assert body["data"]["plateNumber"] is None
    assert body["data"]["detectionType"] == "VEHICLE"
    assert sent_statuses == ["OCR_FAILED"]


def test_create_and_send_image_detection_sends_ocr_failed_when_plate_is_not_recognized(
    monkeypatch,
) -> None:
    sent_statuses = []

    async def return_unrecognized_detection(*, camera_code, captured_at, image_bytes):
        return make_unrecognized_detection()

    async def record_backend_send(result, detection_status=None):
        sent_statuses.append(detection_status)

    monkeypatch.setattr(
        detection_route.inference_service,
        "detect_from_image_bytes",
        return_unrecognized_detection,
    )
    monkeypatch.setattr(
        detection_route.backend_client,
        "send_detection",
        record_backend_send,
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
        "Detection result sent to backend as OCR_FAILED"
    )
    assert body["data"]["plateNumber"] is None
    assert body["data"]["detectionType"] == "VEHICLE"
    assert sent_statuses == ["OCR_FAILED"]


def test_create_and_send_image_detection_sends_duplicate_status_to_backend(
    monkeypatch,
) -> None:
    detection_route.duplicate_detection_guard.clear()
    sent_statuses = []

    async def return_recognized_detection(*, camera_code, captured_at, image_bytes):
        return make_recognized_detection()

    async def record_backend_send(result, detection_status=None):
        sent_statuses.append(detection_status)

    monkeypatch.setattr(
        detection_route.inference_service,
        "detect_from_image_bytes",
        return_recognized_detection,
    )
    monkeypatch.setattr(
        detection_route.backend_client,
        "send_detection",
        record_backend_send,
    )

    request_kwargs = {
        "data": {
            "cameraCode": "CAM_001",
            "capturedAt": "2026-04-30T10:30:00",
        },
        "files": {
            "image": ("sample.jpg", make_test_image_bytes(), "image/jpeg"),
        },
    }

    first_response = client.post("/api/detections/image/send", **request_kwargs)
    second_response = client.post("/api/detections/image/send", **request_kwargs)

    assert first_response.status_code == 200
    assert first_response.json()["message"] == "Detection result sent to backend"
    assert second_response.status_code == 200
    assert second_response.json()["message"] == (
        "Duplicate detection sent to backend as DUPLICATE_SKIPPED"
    )
    assert sent_statuses == [None, "DUPLICATE_SKIPPED"]

    detection_route.duplicate_detection_guard.clear()
