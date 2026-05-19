import asyncio
import base64
from datetime import datetime, timedelta
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
from app.services.backend_client import BackendClient
from app.services.inference_service import InferenceService
from app.services.plate_detector import PlateDetection
from app.services.plate_recognizer import PlateRecognition, PlateRecognizer
from app.services.speed_config import (
    Point,
    SpeedCameraConfig,
    SpeedTrackingConfig,
    VirtualLine,
    load_speed_camera_configs,
    parse_virtual_line,
    build_default_speed_config,
)
from app.schemas.speed import SpeedMeasurementResult, SpeedViolationCreateRequest
from app.services.speed_tracker import SpeedTracker, VehicleTrackInput
from app.services.vehicle_detector import VehicleDetection
from app.services.vehicle_detector import VehicleDetector
from app.services.frame_buffer import FrameBuffer
from app.services.stream_event_service import (
    STREAM_STATUS_FINALIZED,
    STREAM_STATUS_IDLE,
    STREAM_STATUS_TRACKING,
    StreamEventService,
    StreamProcessingResult,
)


client = TestClient(app)


def make_test_image_bytes() -> bytes:
    image = np.zeros((80, 160, 3), dtype=np.uint8)
    success, buffer = cv2.imencode(".jpg", image)

    assert success

    return buffer.tobytes()


class FakeYoloBox:
    def __init__(
        self,
        *,
        class_id: int,
        confidence_score: float,
        bbox: list[int],
    ) -> None:
        self.cls = [class_id]
        self.conf = [confidence_score]
        self.xyxy = [bbox]


class FakeYoloResult:
    def __init__(self, *, boxes: list[FakeYoloBox]) -> None:
        self.names = {
            0: "person",
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck",
        }
        self.boxes = boxes


class FakeYoloModel:
    def __init__(self, *, boxes: list[FakeYoloBox]) -> None:
        self.names = {
            0: "person",
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck",
        }
        self.boxes = boxes

    def __call__(self, image, *, conf, iou, max_det):
        return [FakeYoloResult(boxes=self.boxes)]


def mock_vehicle_detection(
    monkeypatch,
    service: InferenceService,
    *,
    confidence_score: float = 0.82,
) -> None:
    monkeypatch.setattr(
        service.vehicle_detector,
        "detect",
        lambda image: VehicleDetection(
            detection_type="VEHICLE",
            confidence_score=confidence_score,
            bbox=(0, 0, 150, 70),
        ),
    )


def make_unrecognized_detection() -> DetectionResult:
    return DetectionResult(
        camera_code="CAM_001",
        plate_number=None,
        detection_type="UNKNOWN",
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
        plate_crop_image_path="storage/detections/2026/04/30/CAM_001_103000_plate_crop.jpg",
        plate_crop_image_url="/static/detections/2026/04/30/CAM_001_103000_plate_crop.jpg",
        ocr_image_path="storage/detections/2026/04/30/CAM_001_103000_ocr.jpg",
        ocr_image_url="/static/detections/2026/04/30/CAM_001_103000_ocr.jpg",
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


def test_vehicle_detector_returns_best_allowed_vehicle_class(
    monkeypatch,
) -> None:
    monkeypatch.setattr("app.services.vehicle_detector.VEHICLE_MODEL_SOURCE", "fake.pt")
    monkeypatch.setattr(
        "app.services.vehicle_detector.VEHICLE_CLASS_NAMES",
        ("car", "bus", "truck", "motorcycle"),
    )

    detector = VehicleDetector()
    fake_model = FakeYoloModel(
        boxes=[
            FakeYoloBox(class_id=0, confidence_score=0.99, bbox=[0, 0, 20, 20]),
            FakeYoloBox(class_id=2, confidence_score=0.88, bbox=[10, 20, 80, 60]),
            FakeYoloBox(class_id=7, confidence_score=0.77, bbox=[30, 40, 100, 90]),
        ]
    )
    monkeypatch.setattr(detector, "_load_model", lambda: fake_model)

    result = detector.detect(np.zeros((100, 120, 3), dtype=np.uint8))

    assert result.detection_type == "VEHICLE"
    assert result.confidence_score == 0.88
    assert result.bbox == (10, 20, 80, 60)
    assert [box.class_name for box in result.boxes] == ["car", "truck"]


def test_vehicle_detector_returns_unknown_when_no_vehicle_class(
    monkeypatch,
) -> None:
    monkeypatch.setattr("app.services.vehicle_detector.VEHICLE_MODEL_SOURCE", "fake.pt")
    monkeypatch.setattr(
        "app.services.vehicle_detector.VEHICLE_CLASS_NAMES",
        ("car", "bus", "truck", "motorcycle"),
    )

    detector = VehicleDetector()
    fake_model = FakeYoloModel(
        boxes=[
            FakeYoloBox(class_id=0, confidence_score=0.99, bbox=[0, 0, 20, 20]),
        ]
    )
    monkeypatch.setattr(detector, "_load_model", lambda: fake_model)

    result = detector.detect(np.zeros((100, 120, 3), dtype=np.uint8))

    assert result.detection_type == "UNKNOWN"
    assert result.confidence_score == 0.0
    assert result.bbox is None
    assert result.boxes == []


def test_parse_virtual_line_from_string() -> None:
    line = parse_virtual_line("10,20,30,40")

    assert line.start.x == 10
    assert line.start.y == 20
    assert line.end.x == 30
    assert line.end.y == 40


def test_load_speed_camera_configs_from_json() -> None:
    configs = load_speed_camera_configs(
        """
        [
          {
            "cameraCode": "CAM_001",
            "lineA": [100, 200, 500, 200],
            "lineB": [100, 420, 500, 420],
            "distanceMeters": 12.5,
            "speedLimitKmh": 60.0,
            "enabled": true
          }
        ]
        """
    )

    config = configs["CAM_001"]

    assert config.camera_code == "CAM_001"
    assert config.line_a.start.x == 100
    assert config.line_b.end.y == 420
    assert config.distance_meters == 12.5
    assert config.speed_limit_kmh == 60.0
    assert config.enabled is True


def test_default_speed_config_uses_camera_code() -> None:
    config = build_default_speed_config("CAM_TEST")

    assert config.camera_code == "CAM_TEST"
    assert config.distance_meters > 0
    assert config.speed_limit_kmh > 0


def test_speed_camera_config_rejects_invalid_distance() -> None:
    try:
        load_speed_camera_configs(
            '[{"cameraCode":"CAM_001","lineA":[0,0,1,1],"lineB":[0,2,1,2],"distanceMeters":0,"speedLimitKmh":50}]'
        )
    except ValueError as exc:
        assert "distanceMeters" in str(exc)
    else:
        raise AssertionError("expected invalid distanceMeters to fail")


def make_speed_camera_config(
    *,
    enabled: bool = True,
    speed_limit_kmh: float = 30.0,
) -> SpeedCameraConfig:
    return SpeedCameraConfig(
        camera_code="CAM_001",
        line_a=VirtualLine(start=Point(0, 20), end=Point(100, 20)),
        line_b=VirtualLine(start=Point(0, 60), end=Point(100, 60)),
        distance_meters=10.0,
        speed_limit_kmh=speed_limit_kmh,
        enabled=enabled,
    )


def make_speed_tracking_config() -> SpeedTrackingConfig:
    return SpeedTrackingConfig(
        max_match_distance_pixels=120.0,
        track_ttl_seconds=10.0,
        min_elapsed_seconds=0.05,
        max_reasonable_kmh=220.0,
    )


def test_speed_tracker_measures_violation_after_line_a_b_crossing() -> None:
    tracker = SpeedTracker(tracking_config=make_speed_tracking_config())
    config = make_speed_camera_config(speed_limit_kmh=20.0)
    captured_at = datetime(2026, 5, 19, 15, 20, 0)

    first = tracker.process_detections(
        camera_code="CAM_001",
        captured_at=captured_at,
        detections=[VehicleTrackInput(bbox=(10, 0, 50, 10), confidence_score=0.9)],
        camera_config=config,
    )
    second = tracker.process_detections(
        camera_code="CAM_001",
        captured_at=captured_at + timedelta(seconds=1),
        detections=[VehicleTrackInput(bbox=(10, 10, 50, 30), confidence_score=0.9)],
        camera_config=config,
    )
    third = tracker.process_detections(
        camera_code="CAM_001",
        captured_at=captured_at + timedelta(seconds=2),
        detections=[VehicleTrackInput(bbox=(10, 50, 50, 70), confidence_score=0.9)],
        camera_config=config,
    )

    assert first == []
    assert second == []
    assert len(third) == 1
    assert third[0].track_id == 1
    assert third[0].measured_speed == 28.8
    assert third[0].elapsed_seconds == 1.25
    assert third[0].speed_limit == 20.0
    assert third[0].is_violation is True


def test_speed_tracker_estimates_speed_when_track_starts_after_line_a() -> None:
    tracker = SpeedTracker(tracking_config=make_speed_tracking_config())
    config = make_speed_camera_config(speed_limit_kmh=20.0)
    captured_at = datetime(2026, 5, 19, 15, 20, 0)

    first = tracker.process_detections(
        camera_code="CAM_001",
        captured_at=captured_at,
        detections=[VehicleTrackInput(bbox=(10, 10, 50, 30), confidence_score=0.9)],
        camera_config=config,
    )
    second = tracker.process_detections(
        camera_code="CAM_001",
        captured_at=captured_at + timedelta(seconds=1),
        detections=[VehicleTrackInput(bbox=(10, 30, 50, 50), confidence_score=0.9)],
        camera_config=config,
    )
    third = tracker.process_detections(
        camera_code="CAM_001",
        captured_at=captured_at + timedelta(seconds=2),
        detections=[VehicleTrackInput(bbox=(10, 50, 50, 70), confidence_score=0.9)],
        camera_config=config,
    )

    assert first == []
    assert second == []
    assert len(third) == 1
    assert third[0].measured_speed == 18.0
    assert third[0].elapsed_seconds == 2.0
    assert third[0].is_violation is False


def test_speed_tracker_skips_when_camera_config_disabled() -> None:
    tracker = SpeedTracker(tracking_config=make_speed_tracking_config())

    measurements = tracker.process_detections(
        camera_code="CAM_001",
        captured_at=datetime(2026, 5, 19, 15, 20, 0),
        detections=[VehicleTrackInput(bbox=(10, 0, 50, 10), confidence_score=0.9)],
        camera_config=make_speed_camera_config(enabled=False),
    )

    assert measurements == []


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
    assert response.json()["analysisStatus"] == "ANALYSIS_ONLY"

    assert data["cameraCode"] == "CAM_001"
    assert data["plateNumber"] is None
    assert data["detectionType"] == "UNKNOWN"
    assert data["directionType"] == "IN"
    assert data["confidenceScore"] == 0.0
    assert data["imagePath"] is not None
    assert Path(data["imagePath"]).exists()
    assert data["imageUrl"].startswith("/static/detections/")
    assert data["plateCropImageUrl"] is None
    assert data["ocrImageUrl"] is None


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
    assert response.json()["analysisStatus"] == "ANALYSIS_ONLY"

    assert data["cameraCode"] == "CAM_001"
    assert data["plateNumber"] is None
    assert data["detectionType"] == "UNKNOWN"
    assert data["imagePath"] is not None
    assert Path(data["imagePath"]).exists()
    assert data["imageUrl"].startswith("/static/detections/")
    assert data["plateCropImageUrl"] is None
    assert data["ocrImageUrl"] is None


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
    mock_vehicle_detection(monkeypatch, service)

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
    assert result.image_url.endswith("/2026/04/30/CAM_001_103000_frame.jpg")
    assert result.plate_crop_image_path.endswith("CAM_001_103000_plate_crop.jpg")
    assert result.plate_crop_image_url.endswith("/2026/04/30/CAM_001_103000_plate_crop.jpg")
    assert result.ocr_image_path.endswith("CAM_001_103000_ocr.jpg")
    assert result.ocr_image_url.endswith("/2026/04/30/CAM_001_103000_ocr.jpg")
    assert (storage_dir / "CAM_001_103000_frame.jpg").exists()
    assert (storage_dir / "CAM_001_103000_plate_crop.jpg").exists()
    assert (storage_dir / "CAM_001_103000_ocr.jpg").exists()


def test_detection_includes_crop_and_ocr_images_when_ocr_fails_after_bbox(
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
    mock_vehicle_detection(monkeypatch, service)

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
            text=None,
            confidence_score=0.0,
        ),
    )

    result = asyncio.run(
        service.detect_from_image_bytes(
            camera_code="CAM_001",
            captured_at=datetime(2026, 4, 30, 10, 30, 0),
            image_bytes=make_test_image_bytes(),
        )
    )

    assert result.plate_number is None
    assert result.detection_type == "VEHICLE"
    assert result.plate_crop_image_url.endswith("/2026/04/30/CAM_001_103000_plate_crop.jpg")
    assert result.ocr_image_url.endswith("/2026/04/30/CAM_001_103000_ocr.jpg")


def test_detection_returns_vehicle_when_vehicle_detected_without_plate(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setattr(
        "app.services.image_storage_service.IMAGE_STORAGE_DIR",
        str(tmp_path / "detections"),
    )

    service = InferenceService()
    mock_vehicle_detection(monkeypatch, service, confidence_score=0.81)
    monkeypatch.setattr(
        service.plate_detector,
        "detect",
        lambda image: PlateDetection(
            detection_type="UNKNOWN",
            confidence_score=0.0,
            bbox=None,
        ),
    )

    result = asyncio.run(
        service.detect_from_image_bytes(
            camera_code="CAM_001",
            captured_at=datetime(2026, 4, 30, 10, 30, 0),
            image_bytes=make_test_image_bytes(),
        )
    )

    assert result.plate_number is None
    assert result.detection_type == "VEHICLE"
    assert result.confidence_score == 0.81
    assert result.plate_crop_image_url is None
    assert result.ocr_image_url is None


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
        return VehicleDetection(
            detection_type="UNKNOWN",
            confidence_score=0.0,
            bbox=None,
        )

    monkeypatch.setattr(
        "app.services.inference_service.preprocess_frame_for_detection",
        fake_preprocess,
    )
    monkeypatch.setattr(service.vehicle_detector, "detect", fake_detect)

    result = asyncio.run(
        service.detect_from_image_bytes(
            camera_code="CAM_001",
            captured_at=datetime(2026, 4, 30, 10, 30, 0),
            image_bytes=make_test_image_bytes(),
        )
    )

    assert result.detection_type == "UNKNOWN"
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
    mock_vehicle_detection(monkeypatch, service)

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
    assert result.plate_crop_image_path.endswith("CAM_001_103000_plate_crop.jpg")
    assert result.plate_crop_image_url.endswith("/2026/04/30/CAM_001_103000_plate_crop.jpg")
    assert result.ocr_image_path.endswith("CAM_001_103000_ocr.jpg")
    assert result.ocr_image_url.endswith("/2026/04/30/CAM_001_103000_ocr.jpg")
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


def test_stream_event_service_finalizes_after_bbox_misses(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setattr("app.services.stream_event_service.SAVE_EVENT_DEBUG", True)
    monkeypatch.setattr(
        "app.services.stream_event_service.IMAGE_STORAGE_DIR",
        str(tmp_path / "detections"),
    )

    image_bytes = make_test_image_bytes()
    detections = [
        VehicleDetection("UNKNOWN", 0.0, None),
        VehicleDetection("VEHICLE", 0.93, (20, 20, 120, 50)),
        VehicleDetection("UNKNOWN", 0.0, None),
        VehicleDetection("UNKNOWN", 0.0, None),
        VehicleDetection("UNKNOWN", 0.0, None),
        VehicleDetection("UNKNOWN", 0.0, None),
        VehicleDetection("UNKNOWN", 0.0, None),
    ]

    class FakeInferenceService:
        def detect_vehicle_bbox_from_image(self, image):
            return detections.pop(0)

        async def detect_from_image_bytes(
            self,
            *,
            camera_code,
            captured_at,
            image_bytes,
            vehicle_detection=None,
        ):
            return make_recognized_detection(detected_at=captured_at)

    service = StreamEventService(
        buffer=FrameBuffer(max_frames_per_camera=3),
        inference_service=FakeInferenceService(),
    )
    captured_at = datetime(2026, 5, 14, 14, 30, 0)

    idle_result = asyncio.run(
        service.process_frame(
            camera_code="CAM_001",
            captured_at=captured_at,
            content_type="image/jpeg",
            image_bytes=image_bytes,
        )
    )
    assert idle_result.stream_status == STREAM_STATUS_IDLE

    tracking_result = asyncio.run(
        service.process_frame(
            camera_code="CAM_001",
            captured_at=captured_at + timedelta(milliseconds=200),
            content_type="image/jpeg",
            image_bytes=image_bytes,
        )
    )
    assert tracking_result.stream_status == STREAM_STATUS_TRACKING
    assert tracking_result.event_id is not None

    finalized_result = None
    for index in range(5):
        finalized_result = asyncio.run(
            service.process_frame(
                camera_code="CAM_001",
                captured_at=captured_at + timedelta(milliseconds=400 + (index * 200)),
                content_type="image/jpeg",
                image_bytes=image_bytes,
            )
        )

    assert finalized_result is not None
    assert finalized_result.stream_status == STREAM_STATUS_FINALIZED
    assert finalized_result.result is not None
    assert finalized_result.result.plate_number == "123A4567"
    assert finalized_result.event_age_seconds >= 0
    assert len(list((tmp_path / "detections" / "debug").rglob("*.jpg"))) == 1


def test_stream_frame_endpoint_returns_tracking(monkeypatch) -> None:
    class FakeStreamService:
        async def process_frame(self, *, camera_code, captured_at, content_type, image_bytes):
            return StreamProcessingResult(
                stream_status=STREAM_STATUS_TRACKING,
                camera_code=camera_code,
                event_id="CAM_001-20260514143000-test",
                frame_count=2,
                bbox=(10, 20, 80, 50),
                bboxes=[(10, 20, 80, 50), (90, 20, 150, 50)],
                bbox_confidence_score=0.93,
                event_age_seconds=1.5,
            )

    monkeypatch.setattr(
        detection_route,
        "stream_detection_service",
        FakeStreamService(),
    )

    response = client.post(
        "/api/detections/stream-frame",
        data={
            "cameraCode": "CAM_001",
            "capturedAt": "2026-05-14T14:30:00",
        },
        files={
            "image": ("frame.jpg", make_test_image_bytes(), "image/jpeg"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["streamStatus"] == "TRACKING"
    assert body["eventId"] == "CAM_001-20260514143000-test"
    assert body["frameCount"] == 2
    assert body["bbox"] == [10, 20, 80, 50]
    assert body["bboxes"] == [[10, 20, 80, 50], [90, 20, 150, 50]]
    assert body["bboxConfidenceScore"] == 0.93
    assert body["eventAgeSeconds"] == 1.5
    assert body["analysisStatus"] is None
    assert body["data"] is None


def test_stream_frame_endpoint_sends_finalized_detection_to_backend(monkeypatch) -> None:
    detection_route.duplicate_detection_guard.clear()

    sent_statuses = []

    class FakeStreamService:
        async def process_frame(self, *, camera_code, captured_at, content_type, image_bytes):
            return StreamProcessingResult(
                stream_status=STREAM_STATUS_FINALIZED,
                camera_code=camera_code,
                event_id="CAM_001-20260514143000-test",
                frame_count=6,
                result=make_recognized_detection(detected_at=captured_at),
            )

    async def record_backend_send(result, detection_status=None):
        sent_statuses.append(detection_status)
        return {"data": {"status": "FLOW_EVENT_CREATED"}}

    monkeypatch.setattr(
        detection_route,
        "stream_detection_service",
        FakeStreamService(),
    )
    monkeypatch.setattr(
        detection_route.backend_client,
        "send_detection",
        record_backend_send,
    )

    response = client.post(
        "/api/detections/stream-frame",
        data={
            "cameraCode": "CAM_001",
            "capturedAt": "2026-05-14T14:30:00",
        },
        files={
            "image": ("frame.jpg", make_test_image_bytes(), "image/jpeg"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["streamStatus"] == "FINALIZED"
    assert body["analysisStatus"] == "FLOW_EVENT_CREATED"
    assert body["data"]["plateNumber"] == "123A4567"
    assert sent_statuses == [None]

    detection_route.duplicate_detection_guard.clear()


def test_stream_frame_endpoint_sends_speed_violation_when_flow_event_id_exists(
    monkeypatch,
) -> None:
    detection_route.duplicate_detection_guard.clear()

    speed_payloads = []
    captured_at = datetime(2026, 5, 14, 14, 30, 0)
    speed_violation = SpeedMeasurementResult(
        track_id=1,
        measured_speed=72.35,
        speed_limit=50.0,
        distance_meters=10.0,
        elapsed_seconds=0.498,
        is_violation=True,
        measured_at=captured_at,
    )

    class FakeStreamService:
        async def process_frame(self, *, camera_code, captured_at, content_type, image_bytes):
            return StreamProcessingResult(
                stream_status=STREAM_STATUS_FINALIZED,
                camera_code=camera_code,
                event_id="CAM_001-20260514143000-test",
                frame_count=6,
                result=make_recognized_detection(detected_at=captured_at),
                speed_measurements=[speed_violation],
                speed_violation=speed_violation,
            )

    async def record_detection_send(result, detection_status=None):
        return {
            "data": {
                "status": "FLOW_EVENT_CREATED",
                "flowEventId": 301,
            }
        }

    async def record_speed_send(request):
        speed_payloads.append(request)
        return {"data": {"violationId": 1}}

    monkeypatch.setattr(
        detection_route,
        "stream_detection_service",
        FakeStreamService(),
    )
    monkeypatch.setattr(
        detection_route.backend_client,
        "send_detection",
        record_detection_send,
    )
    monkeypatch.setattr(
        detection_route.backend_client,
        "send_speed_violation",
        record_speed_send,
    )

    response = client.post(
        "/api/detections/stream-frame",
        data={
            "cameraCode": "CAM_001",
            "capturedAt": captured_at.isoformat(),
        },
        files={
            "image": ("frame.jpg", make_test_image_bytes(), "image/jpeg"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["streamStatus"] == "FINALIZED"
    assert body["speedViolation"]["measuredSpeed"] == 72.35
    assert body["speedViolationSent"] is True
    assert len(speed_payloads) == 1
    assert speed_payloads[0].flow_event_id == 301
    assert speed_payloads[0].plate_number == "123A4567"
    assert speed_payloads[0].measured_speed == 72.35

    detection_route.duplicate_detection_guard.clear()


def test_stream_event_service_keeps_non_violation_speed_until_finalized() -> None:
    image_bytes = make_test_image_bytes()

    class FakeInferenceService:
        def detect_vehicle_bbox_from_image(self, image):
            return VehicleDetection("VEHICLE", 0.93, (10, 0, 50, 10))

        async def detect_from_image_bytes(
            self,
            *,
            camera_code,
            captured_at,
            image_bytes,
            vehicle_detection=None,
        ):
            return make_recognized_detection(detected_at=captured_at)

    service = StreamEventService(
        buffer=FrameBuffer(max_frames_per_camera=3),
        inference_service=FakeInferenceService(),
        speed_tracker=SpeedTracker(tracking_config=make_speed_tracking_config()),
    )
    captured_at = datetime(2026, 5, 14, 14, 30, 0)
    event = service._start_event("CAM_001", captured_at, 0.0)
    measurement = SpeedMeasurementResult(
        track_id=1,
        measured_speed=36.0,
        speed_limit=50.0,
        distance_meters=10.0,
        elapsed_seconds=1.0,
        is_violation=False,
        measured_at=captured_at,
    )
    event.speed_measurement = measurement

    result = asyncio.run(
        service.process_frame(
            camera_code="CAM_001",
            captured_at=captured_at + timedelta(seconds=10),
            content_type="image/jpeg",
            image_bytes=image_bytes,
        )
    )

    assert result.stream_status == STREAM_STATUS_FINALIZED
    assert result.speed_measurements == [measurement]
    assert result.speed_violation is None


def test_backend_client_payload_includes_crop_and_ocr_image_fields(monkeypatch) -> None:
    captured = {}

    class FakeResponse:
        content = b'{"status":"ok"}'

        def raise_for_status(self):
            return None

        def json(self):
            return {"status": "ok"}

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return None

        async def post(self, url, json, headers):
            captured["json"] = json
            captured["headers"] = headers
            return FakeResponse()

    monkeypatch.setattr("app.services.backend_client.BACKEND_INTERNAL_API_KEY", "test-key")
    monkeypatch.setattr("app.services.backend_client.httpx.AsyncClient", FakeAsyncClient)

    asyncio.run(
        BackendClient().send_detection(
            make_recognized_detection(),
            "DUPLICATE_SKIPPED",
        )
    )

    payload = captured["json"]

    assert payload["status"] == "DUPLICATE_SKIPPED"
    assert payload["plateCropImagePath"].endswith("_plate_crop.jpg")
    assert payload["plateCropImageUrl"].endswith("_plate_crop.jpg")
    assert payload["ocrImagePath"].endswith("_ocr.jpg")
    assert payload["ocrImageUrl"].endswith("_ocr.jpg")
    assert captured["headers"]["X-Internal-Api-Key"] == "test-key"


def test_backend_client_speed_violation_payload(monkeypatch) -> None:
    captured = {}

    class FakeResponse:
        content = b'{"status":"ok"}'

        def raise_for_status(self):
            return None

        def json(self):
            return {"status": "ok"}

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return None

        async def post(self, url, json, headers):
            captured["url"] = url
            captured["json"] = json
            captured["headers"] = headers
            return FakeResponse()

    monkeypatch.setattr("app.services.backend_client.BACKEND_INTERNAL_API_KEY", "test-key")
    monkeypatch.setattr("app.services.backend_client.httpx.AsyncClient", FakeAsyncClient)

    asyncio.run(
        BackendClient().send_speed_violation(
            SpeedViolationCreateRequest(
                flow_event_id=301,
                plate_number="123A4567",
                camera_code="CAM_001",
                measured_speed=72.35,
                speed_limit=50.0,
                violation_image_path="storage/detections/frame.jpg",
                violation_image_url="/static/detections/frame.jpg",
                violated_at=datetime(2026, 5, 19, 15, 20, 0),
            )
        )
    )

    assert captured["url"].endswith("/api/speed-violations")
    assert captured["json"]["flowEventId"] == 301
    assert captured["json"]["plateNumber"] == "123A4567"
    assert captured["json"]["measuredSpeed"] == 72.35
    assert captured["headers"]["X-Internal-Api-Key"] == "test-key"


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
    assert body["analysisStatus"] == "OCR_FAILED"
    assert body["data"]["plateNumber"] is None
    assert body["data"]["detectionType"] == "UNKNOWN"
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
    assert body["analysisStatus"] == "OCR_FAILED"
    assert body["data"]["plateNumber"] is None
    assert body["data"]["detectionType"] == "UNKNOWN"
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
    assert first_response.json()["message"] == (
        "Detection result saved as FLOW_EVENT_CREATED"
    )
    assert first_response.json()["analysisStatus"] == "FLOW_EVENT_CREATED"
    assert second_response.status_code == 200
    assert second_response.json()["message"] == (
        "Duplicate detection sent to backend as DUPLICATE_SKIPPED"
    )
    assert second_response.json()["analysisStatus"] == "DUPLICATE_SKIPPED"
    assert sent_statuses == [None, "DUPLICATE_SKIPPED"]

    detection_route.duplicate_detection_guard.clear()
