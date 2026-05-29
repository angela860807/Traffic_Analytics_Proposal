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
from app.services.bbox_tracker import BboxTracker
from app.services.inference_service import InferenceService
from app.services.plate_detector import PlateDetection
from app.services.plate_recognizer import PlateRecognition, PlateRecognizer
from app.services.speed_config import (
    Point,
    SpeedCameraConfig,
    SpeedTrackingConfig,
    SPEED_MODE_LINE_CROSSING,
    SPEED_MODE_TRACK_DELTA,
    VirtualLine,
    load_speed_camera_configs,
    parse_virtual_line,
    build_default_speed_config,
    get_speed_camera_config,
    reset_speed_settings_cache,
    validate_speed_settings,
)
from app.schemas.speed import SpeedMeasurementResult, SpeedViolationCreateRequest
from app.services.speed_tracker import SpeedTracker, VehicleTrackInput
from app.services.vehicle_detector import VehicleDetection, VehicleDetectionBox
from app.services.vehicle_detector import VehicleDetector
from app.services.frame_buffer import BufferedFrame, FrameBuffer
from app.services.stream_event_service import (
    STREAM_STATUS_FINALIZED,
    STREAM_STATUS_IDLE,
    STREAM_STATUS_TRACKING,
    StreamEventService,
    StreamProcessingResult,
)
from scripts.stream_video_file import (
    build_full_frame_speed_zone_config,
    build_speed_zone_config,
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
        frame_image_path="storage/detections/2026/04/30/CAM_001_103000_frame.jpg",
        frame_image_url="/static/detections/2026/04/30/CAM_001_103000_frame.jpg",
        detected_at=datetime(2026, 4, 30, 10, 30, 0),
        processing_status="NO_VEHICLE",
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
        frame_image_path="storage/detections/2026/04/30/CAM_001_103000_frame.jpg",
        frame_image_url="/static/detections/2026/04/30/CAM_001_103000_frame.jpg",
        vehicle_crop_image_path="storage/detections/2026/04/30/CAM_001_103000_vehicle_crop.jpg",
        vehicle_crop_image_url="/static/detections/2026/04/30/CAM_001_103000_vehicle_crop.jpg",
        plate_crop_image_path="storage/detections/2026/04/30/CAM_001_103000_plate_crop.jpg",
        plate_crop_image_url="/static/detections/2026/04/30/CAM_001_103000_plate_crop.jpg",
        ocr_image_path="storage/detections/2026/04/30/CAM_001_103000_ocr.jpg",
        ocr_image_url="/static/detections/2026/04/30/CAM_001_103000_ocr.jpg",
        detected_at=detected_at,
        processing_status="OCR_COMPLETED",
    )


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "traffic-ai-server",
    }


def test_detection_warmup_endpoint_loads_models(monkeypatch) -> None:
    loaded = []

    monkeypatch.setattr(detection_route, "VEHICLE_MODEL_SOURCE", "vehicle.pt")
    monkeypatch.setattr(detection_route, "PLATE_MODEL_PATH", "plate.pt")
    monkeypatch.setattr(
        detection_route.inference_service.vehicle_detector,
        "_load_model",
        lambda: loaded.append("vehicle"),
    )
    monkeypatch.setattr(
        detection_route.inference_service.plate_detector,
        "_load_model",
        lambda: loaded.append("plate"),
    )
    monkeypatch.setattr(
        detection_route.inference_service.plate_recognizer,
        "_load_ocr",
        lambda: loaded.append("ocr"),
    )

    response = client.post("/api/detections/warmup")

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["loadedModels"] == [
        "vehicleYolo",
        "plateYolo",
        "paddleOcr",
    ]
    assert loaded == ["vehicle", "plate", "ocr"]


def test_stream_ocr_status_endpoint_returns_saved_status() -> None:
    detection_route.stream_ocr_statuses.clear()
    detection_route.stream_ocr_status_seen_at.clear()
    result = make_recognized_detection()
    detection_route.remember_stream_ocr_status(
        "event-1",
        camera_code="CAM_001",
        processing_status="OCR_COMPLETED",
        analysis_status="FLOW_EVENT_CREATED",
        message="done",
        result=result,
    )

    response = client.get("/api/detections/stream-events/event-1/ocr-status")

    assert response.status_code == 200
    body = response.json()
    assert body["eventId"] == "event-1"
    assert body["processingStatus"] == "OCR_COMPLETED"
    assert body["plateNumber"] == "123A4567"

    detection_route.stream_ocr_statuses.clear()
    detection_route.stream_ocr_status_seen_at.clear()


def test_stream_ocr_status_cleanup_removes_expired_status(monkeypatch) -> None:
    detection_route.stream_ocr_statuses.clear()
    detection_route.stream_ocr_status_seen_at.clear()
    monkeypatch.setattr(detection_route, "STREAM_OCR_STATUS_TTL_SECONDS", 10.0)

    detection_route.remember_stream_ocr_status(
        "event-old",
        camera_code="CAM_001",
        processing_status="OCR_COMPLETED",
        message="done",
        result=make_recognized_detection(),
    )
    detection_route.stream_ocr_status_seen_at["event-old"] = 100.0

    detection_route.cleanup_stream_ocr_statuses(now_monotonic=111.0)

    assert "event-old" not in detection_route.stream_ocr_statuses
    assert "event-old" not in detection_route.stream_ocr_status_seen_at


def test_plate_number_normalization_keeps_korean_plate_characters() -> None:
    recognizer = PlateRecognizer()

    cases = {
        "\uc11c\uc6b8 12\uac00 3456": "\uc11c\uc6b812\uac003456",
        "123\uac004567": "123\uac004567",
        "ABC123\uac004567!!": "123\uac004567",
        "  \uacbd\uae30 78\ub098 9012\n": "\uacbd\uae3078\ub0989012",
        None: None,
        "ABC-!!": None,
    }

    for raw_text, expected in cases.items():
        assert recognizer._normalize_plate_number(raw_text) == expected


def test_plate_recognizer_prefers_korean_plate_shape_over_longer_digits() -> None:
    recognizer = PlateRecognizer()
    korean_plate = PlateRecognition("62시6617", 0.95)
    longer_digits = PlateRecognition("62116617", 0.99)

    assert recognizer._is_better_recognition(korean_plate, longer_digits)
    assert not recognizer._is_better_recognition(longer_digits, korean_plate)


def test_plate_number_normalization_extracts_plate_shape_from_noise() -> None:
    recognizer = PlateRecognizer()

    assert recognizer._normalize_plate_number("ABC 62\uc2dc6617!!XYZ") == "62\uc2dc6617"


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


def test_bbox_tracker_keeps_track_id_for_nearby_bbox() -> None:
    tracker = BboxTracker(
        ttl_seconds=2.0,
        min_iou=0.10,
        max_center_distance_pixels=80.0,
    )
    captured_at = datetime(2026, 5, 14, 14, 30, 0)

    first = tracker.update(
        camera_code="CAM_001",
        captured_at=captured_at,
        boxes=[
            VehicleDetectionBox(
                bbox=(10, 20, 80, 60),
                confidence_score=0.92,
                class_name="car",
            )
        ],
    )
    second = tracker.update(
        camera_code="CAM_001",
        captured_at=captured_at + timedelta(seconds=0.3),
        boxes=[
            VehicleDetectionBox(
                bbox=(16, 24, 86, 64),
                confidence_score=0.91,
                class_name="car",
            )
        ],
    )

    assert first[0].track_id == second[0].track_id


def test_bbox_tracker_creates_new_track_after_ttl() -> None:
    tracker = BboxTracker(
        ttl_seconds=0.2,
        min_iou=0.10,
        max_center_distance_pixels=80.0,
    )
    captured_at = datetime(2026, 5, 14, 14, 30, 0)

    first = tracker.update(
        camera_code="CAM_001",
        captured_at=captured_at,
        boxes=[
            VehicleDetectionBox(
                bbox=(10, 20, 80, 60),
                confidence_score=0.92,
                class_name="car",
            )
        ],
    )
    second = tracker.update(
        camera_code="CAM_001",
        captured_at=captured_at + timedelta(seconds=0.5),
        boxes=[
            VehicleDetectionBox(
                bbox=(16, 24, 86, 64),
                confidence_score=0.91,
                class_name="car",
            )
        ],
    )

    assert first[0].track_id != second[0].track_id


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
            "roi": [[80, 180], [520, 180], [520, 440], [80, 440]],
            "distanceMeters": 12.5,
            "speedLimitKmh": 60.0,
            "enabled": true,
            "homography": {
              "imagePoints": [[0, 0], [100, 0], [0, 100], [100, 100]],
              "worldPointsMeters": [[0, 0], [10, 0], [0, 20], [10, 20]]
            }
          }
        ]
        """
    )

    config = configs["CAM_001"]

    assert config.camera_code == "CAM_001"
    assert config.line_a.start.x == 100
    assert config.line_b.end.y == 420
    assert config.roi is not None
    assert len(config.roi) == 4
    assert config.distance_meters == 12.5
    assert config.speed_limit_kmh == 60.0
    assert config.enabled is True
    assert config.homography is not None
    assert len(config.homography.image_points) == 4


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


def test_speed_camera_config_rejects_invalid_homography() -> None:
    try:
        load_speed_camera_configs(
            """
            [
              {
                "cameraCode": "CAM_001",
                "lineA": [0, 0, 100, 0],
                "lineB": [0, 50, 100, 50],
                "distanceMeters": 10.0,
                "speedLimitKmh": 50.0,
                "homography": {
                  "imagePoints": [[0, 0], [100, 0], [0, 100]],
                  "worldPointsMeters": [[0, 0], [10, 0], [0, 20]]
                }
              }
            ]
            """
        )
    except ValueError as exc:
        assert "homography" in str(exc)
    else:
        raise AssertionError("expected invalid homography to fail")


def test_speed_camera_config_rejects_invalid_roi() -> None:
    try:
        load_speed_camera_configs(
            """
            [
              {
                "cameraCode": "CAM_001",
                "lineA": [0, 0, 100, 0],
                "lineB": [0, 50, 100, 50],
                "roi": [[0, 0], [100, 0]],
                "distanceMeters": 10.0,
                "speedLimitKmh": 50.0
              }
            ]
            """
        )
    except ValueError as exc:
        assert "roi" in str(exc)
    else:
        raise AssertionError("expected invalid roi to fail")


def test_clicked_speed_zone_points_build_config() -> None:
    clicked_points = [
        (10, 20),
        (110, 20),
        (110, 80),
        (10, 80),
    ]
    config = build_speed_zone_config(
        camera_code="CAM_001",
        roi_points=clicked_points,
        line_a_points=[clicked_points[0], clicked_points[1]],
        line_b_points=[clicked_points[3], clicked_points[2]],
        distance_meters=14.0,
        speed_limit_kmh=50.0,
        roi_width_meters=3.5,
        roi_height_meters=14.0,
    )[0]

    assert config["roi"] == [[10, 20], [110, 20], [110, 80], [10, 80]]
    assert config["speedMode"] == "TRACK_DELTA"
    assert config["lineA"] == [10, 20, 110, 20]
    assert config["lineB"] == [10, 80, 110, 80]
    assert config["homography"]["imagePoints"] == config["roi"]
    assert config["homography"]["worldPointsMeters"] == [
        [0, 0],
        [3.5, 0],
        [3.5, 14.0],
        [0, 14.0],
    ]


def test_full_frame_speed_zone_builds_default_roi_and_lines() -> None:
    config = build_full_frame_speed_zone_config(
        camera_code="CAM_001",
        frame_width=320,
        frame_height=180,
        distance_meters=14.0,
        speed_limit_kmh=50.0,
        roi_width_meters=14.0,
        roi_height_meters=14.0,
    )[0]

    assert config["roi"] == [[0, 0], [319, 0], [319, 179], [0, 179]]
    assert config["speedMode"] == "TRACK_DELTA"
    assert config["lineA"] == [0, 0, 319, 0]
    assert config["lineB"] == [0, 179, 319, 179]
    assert config["homography"]["imagePoints"] == config["roi"]


def test_speed_settings_validation_caches_camera_configs(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.speed_config.SPEED_CAMERA_CONFIGS_JSON",
        """
        [
          {
            "cameraCode": "CAM_CACHE",
            "lineA": [0, 10, 100, 10],
            "lineB": [0, 40, 100, 40],
            "distanceMeters": 8.0,
            "speedLimitKmh": 30.0,
            "enabled": "false"
          }
        ]
        """,
    )
    reset_speed_settings_cache()

    validate_speed_settings()
    config = get_speed_camera_config("CAM_CACHE")

    assert config.distance_meters == 8.0
    assert config.speed_limit_kmh == 30.0
    assert config.enabled is False

    reset_speed_settings_cache()


def test_speed_settings_validation_rejects_invalid_json(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.speed_config.SPEED_CAMERA_CONFIGS_JSON",
        "[invalid-json",
    )
    reset_speed_settings_cache()

    try:
        validate_speed_settings()
    except ValueError as exc:
        assert "SPEED_CAMERA_CONFIGS_JSON" in str(exc)
    else:
        raise AssertionError("expected invalid SPEED_CAMERA_CONFIGS_JSON to fail")
    finally:
        reset_speed_settings_cache()


def test_app_startup_validates_speed_settings(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.speed_config.SPEED_CAMERA_CONFIGS_JSON",
        "[invalid-json",
    )
    reset_speed_settings_cache()

    try:
        with TestClient(app):
            raise AssertionError("expected startup settings validation to fail")
    except ValueError as exc:
        assert "SPEED_CAMERA_CONFIGS_JSON" in str(exc)
    finally:
        reset_speed_settings_cache()


def make_speed_camera_config(
    *,
    enabled: bool = True,
    speed_limit_kmh: float = 30.0,
    with_homography: bool = False,
    roi: tuple[Point, ...] | None = None,
    speed_mode: str = SPEED_MODE_LINE_CROSSING,
) -> SpeedCameraConfig:
    homography = None
    if with_homography:
        homography = load_speed_camera_configs(
            """
            [
              {
                "cameraCode": "CAM_001",
                "lineA": [0, 20, 100, 20],
                "lineB": [0, 60, 100, 60],
                "distanceMeters": 10.0,
                "speedLimitKmh": 30.0,
                "homography": {
                  "imagePoints": [[0, 0], [100, 0], [0, 100], [100, 100]],
                  "worldPointsMeters": [[0, 0], [10, 0], [0, 20], [10, 20]]
                }
              }
            ]
            """
        )["CAM_001"].homography

    return SpeedCameraConfig(
        camera_code="CAM_001",
        line_a=VirtualLine(start=Point(0, 20), end=Point(100, 20)),
        line_b=VirtualLine(start=Point(0, 60), end=Point(100, 60)),
        distance_meters=10.0,
        speed_limit_kmh=speed_limit_kmh,
        speed_mode=speed_mode,
        enabled=enabled,
        roi=roi,
        homography=homography,
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
    assert third[0].is_estimated is True
    assert third[0].accuracy_level == "ESTIMATED"


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


def test_speed_tracker_uses_homography_distance_when_configured() -> None:
    tracker = SpeedTracker(tracking_config=make_speed_tracking_config())
    config = make_speed_camera_config(speed_limit_kmh=20.0, with_homography=True)
    captured_at = datetime(2026, 5, 19, 15, 20, 0)

    tracker.process_detections(
        camera_code="CAM_001",
        captured_at=captured_at,
        detections=[VehicleTrackInput(bbox=(10, 0, 50, 10), confidence_score=0.9)],
        camera_config=config,
    )
    tracker.process_detections(
        camera_code="CAM_001",
        captured_at=captured_at + timedelta(seconds=1),
        detections=[VehicleTrackInput(bbox=(10, 10, 50, 30), confidence_score=0.9)],
        camera_config=config,
    )
    measurements = tracker.process_detections(
        camera_code="CAM_001",
        captured_at=captured_at + timedelta(seconds=2),
        detections=[VehicleTrackInput(bbox=(10, 50, 50, 70), confidence_score=0.9)],
        camera_config=config,
    )

    assert len(measurements) == 1
    assert measurements[0].distance_meters == 8.0
    assert measurements[0].measured_speed == 23.04
    assert measurements[0].accuracy_level == "HOMOGRAPHY_ESTIMATED"
    assert measurements[0].is_violation is True


def test_speed_tracker_ignores_detections_outside_roi() -> None:
    tracker = SpeedTracker(tracking_config=make_speed_tracking_config())
    config = make_speed_camera_config(
        speed_limit_kmh=20.0,
        roi=(
            Point(0, 20),
            Point(100, 20),
            Point(100, 60),
            Point(0, 60),
        ),
    )
    captured_at = datetime(2026, 5, 19, 15, 20, 0)

    first = tracker.process_detections(
        camera_code="CAM_001",
        captured_at=captured_at,
        detections=[VehicleTrackInput(bbox=(110, 0, 150, 10), confidence_score=0.9)],
        camera_config=config,
    )
    second = tracker.process_detections(
        camera_code="CAM_001",
        captured_at=captured_at + timedelta(seconds=1),
        detections=[VehicleTrackInput(bbox=(110, 10, 150, 30), confidence_score=0.9)],
        camera_config=config,
    )
    third = tracker.process_detections(
        camera_code="CAM_001",
        captured_at=captured_at + timedelta(seconds=2),
        detections=[VehicleTrackInput(bbox=(110, 50, 150, 70), confidence_score=0.9)],
        camera_config=config,
    )

    assert first == []
    assert second == []
    assert third == []


def test_speed_tracker_measures_track_delta_with_homography() -> None:
    tracker = SpeedTracker(tracking_config=make_speed_tracking_config())
    config = make_speed_camera_config(
        speed_limit_kmh=20.0,
        with_homography=True,
        speed_mode=SPEED_MODE_TRACK_DELTA,
    )
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
        detections=[VehicleTrackInput(bbox=(10, 40, 50, 50), confidence_score=0.9)],
        camera_config=config,
    )

    assert first == []
    assert len(second) == 1
    assert second[0].speed_mode == "TRACK_DELTA"
    assert second[0].distance_meters == 8.0
    assert second[0].measured_speed == 28.8
    assert second[0].accuracy_level == "HOMOGRAPHY_ESTIMATED"


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
    monkeypatch.setattr("app.services.inference_service.SAVE_VEHICLE_CROP", True)
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
    monkeypatch.setattr(
        service.plate_recognizer,
        "recognize_best",
        lambda variants: PlateRecognition(
            text="123A4567",
            confidence_score=0.95,
            variant_name=variants[-1][0],
            variant_image=variants[-1][1],
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
    assert result.frame_image_path == result.image_path
    assert result.frame_image_url == result.image_url
    assert result.vehicle_crop_image_path.endswith("CAM_001_103000_vehicle_crop.jpg")
    assert result.vehicle_crop_image_url.endswith("/2026/04/30/CAM_001_103000_vehicle_crop.jpg")
    assert result.plate_crop_image_path.endswith("CAM_001_103000_plate_crop.jpg")
    assert result.plate_crop_image_url.endswith("/2026/04/30/CAM_001_103000_plate_crop.jpg")
    assert result.ocr_image_path.endswith("CAM_001_103000_ocr.jpg")
    assert result.ocr_image_url.endswith("/2026/04/30/CAM_001_103000_ocr.jpg")
    assert (storage_dir / "CAM_001_103000_frame.jpg").exists()
    assert (storage_dir / "CAM_001_103000_vehicle_crop.jpg").exists()
    assert (storage_dir / "CAM_001_103000_plate_crop.jpg").exists()
    assert (storage_dir / "CAM_001_103000_ocr.jpg").exists()
    assert result.processing_status == "OCR_COMPLETED"

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


def test_stream_event_service_uses_high_res_crop_for_finalized_ocr() -> None:
    image_bytes = make_test_image_bytes()
    high_res_crop_bytes = make_test_image_bytes()
    detections = [
        VehicleDetection("VEHICLE", 0.93, (20, 20, 120, 50)),
        VehicleDetection("UNKNOWN", 0.0, None),
        VehicleDetection("UNKNOWN", 0.0, None),
        VehicleDetection("UNKNOWN", 0.0, None),
        VehicleDetection("UNKNOWN", 0.0, None),
        VehicleDetection("UNKNOWN", 0.0, None),
    ]
    captured = {}

    class FakeInferenceService:
        def detect_vehicle_bbox_from_image(self, image):
            return detections.pop(0)

        async def detect_from_image_bytes(self, **kwargs):
            captured.update(kwargs)
            return make_recognized_detection(detected_at=kwargs["captured_at"])

    service = StreamEventService(
        buffer=FrameBuffer(max_frames_per_camera=3),
        inference_service=FakeInferenceService(),
    )
    captured_at = datetime(2026, 5, 14, 14, 30, 0)

    tracking_result = asyncio.run(
        service.process_frame(
            camera_code="CAM_001",
            captured_at=captured_at,
            content_type="image/jpeg",
            image_bytes=image_bytes,
            high_res_crop_bytes=high_res_crop_bytes,
            high_res_crop_content_type="image/jpeg",
        )
    )
    assert tracking_result.stream_status == STREAM_STATUS_TRACKING

    finalized_result = None
    for index in range(5):
        finalized_result = asyncio.run(
            service.process_frame(
                camera_code="CAM_001",
                captured_at=captured_at + timedelta(milliseconds=200 * (index + 1)),
                content_type="image/jpeg",
                image_bytes=image_bytes,
            )
        )

    assert finalized_result is not None
    assert finalized_result.stream_status == STREAM_STATUS_FINALIZED
    assert captured["high_res_crop_bytes"] == high_res_crop_bytes


def test_stream_event_service_attaches_delayed_high_res_crop_by_frame_number() -> None:
    image_bytes = make_test_image_bytes()
    high_res_crop_bytes = make_test_image_bytes()
    detections = [
        VehicleDetection("VEHICLE", 0.93, (20, 20, 120, 50)),
        VehicleDetection("UNKNOWN", 0.0, None),
        VehicleDetection("UNKNOWN", 0.0, None),
        VehicleDetection("UNKNOWN", 0.0, None),
        VehicleDetection("UNKNOWN", 0.0, None),
        VehicleDetection("UNKNOWN", 0.0, None),
    ]
    captured = {}

    class FakeInferenceService:
        def detect_vehicle_bbox_from_image(self, image):
            return detections.pop(0)

        async def detect_from_image_bytes(self, **kwargs):
            captured.update(kwargs)
            return make_recognized_detection(detected_at=kwargs["captured_at"])

    service = StreamEventService(
        buffer=FrameBuffer(max_frames_per_camera=3),
        inference_service=FakeInferenceService(),
    )
    captured_at = datetime(2026, 5, 14, 14, 30, 0)

    tracking_result = asyncio.run(
        service.process_frame(
            camera_code="CAM_001",
            captured_at=captured_at,
            content_type="image/jpeg",
            image_bytes=image_bytes,
            frame_number=1,
        )
    )
    assert tracking_result.stream_status == STREAM_STATUS_TRACKING

    finalized_result = None
    for index in range(5):
        finalized_result = asyncio.run(
            service.process_frame(
                camera_code="CAM_001",
                captured_at=captured_at + timedelta(milliseconds=200 * (index + 1)),
                content_type="image/jpeg",
                image_bytes=image_bytes,
                frame_number=index + 2,
                high_res_crop_bytes=high_res_crop_bytes if index == 0 else None,
                high_res_crop_content_type="image/jpeg" if index == 0 else None,
                high_res_crop_frame_number=1 if index == 0 else None,
            )
        )

    assert finalized_result is not None
    assert finalized_result.stream_status == STREAM_STATUS_FINALIZED
    assert captured["high_res_crop_bytes"] == high_res_crop_bytes


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
                track_id=3,
                event_age_seconds=1.5,
                processing_status="TRACKING",
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
    assert body["trackId"] == 3
    assert body["eventAgeSeconds"] == 1.5
    assert body["processingStatus"] == "TRACKING"
    assert body["analysisStatus"] is None
    assert body["data"] is None


def test_stream_frame_endpoint_accepts_high_res_crop(monkeypatch) -> None:
    captured = {}

    class FakeStreamService:
        async def process_frame(self, **kwargs):
            captured.update(kwargs)
            return StreamProcessingResult(
                stream_status=STREAM_STATUS_TRACKING,
                camera_code=kwargs["camera_code"],
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
            "frameNumber": "7",
            "highResCropFrameNumber": "6",
        },
        files={
            "image": ("frame.jpg", make_test_image_bytes(), "image/jpeg"),
            "highResCrop": ("crop.jpg", make_test_image_bytes(), "image/jpeg"),
        },
    )

    assert response.status_code == 200
    assert captured["frame_number"] == 7
    assert captured["high_res_crop_frame_number"] == 6
    assert captured["high_res_crop_bytes"]
    assert captured["high_res_crop_content_type"] == "image/jpeg"


def test_stream_frame_endpoint_rejects_invalid_high_res_crop_type() -> None:
    response = client.post(
        "/api/detections/stream-frame",
        data={
            "cameraCode": "CAM_001",
            "capturedAt": "2026-05-14T14:30:00",
        },
        files={
            "image": ("frame.jpg", make_test_image_bytes(), "image/jpeg"),
            "highResCrop": ("crop.txt", b"bad", "text/plain"),
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "highResCrop must be jpeg or png"


def test_high_res_stream_ocr_endpoint_sends_detection_to_backend(monkeypatch) -> None:
    detection_route.duplicate_detection_guard.clear()
    captured = {}
    detected_at = datetime(2026, 5, 14, 14, 30, 0)

    async def return_high_res_detection(
        *,
        camera_code,
        captured_at,
        image_bytes,
        vehicle_detection=None,
    ):
        captured["camera_code"] = camera_code
        captured["captured_at"] = captured_at
        captured["image_bytes"] = image_bytes
        captured["vehicle_detection"] = vehicle_detection
        return make_recognized_detection(detected_at=captured_at)

    async def record_backend_send(result, detection_status=None):
        captured["backend_result"] = result
        captured["backend_status"] = detection_status
        return {"data": {"status": "FLOW_EVENT_CREATED", "flowEventId": 301}}

    monkeypatch.setattr(
        detection_route.inference_service,
        "detect_from_image_bytes",
        return_high_res_detection,
    )
    monkeypatch.setattr(
        detection_route.backend_client,
        "send_detection",
        record_backend_send,
    )

    response = client.post(
        "/api/detections/stream-frame/highres-ocr",
        data={
            "cameraCode": "CAM_001",
            "capturedAt": detected_at.isoformat(),
            "frameNumber": "123",
        },
        files={
            "highResCrop": ("crop.jpg", make_test_image_bytes(), "image/jpeg"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["analysisStatus"] == "FLOW_EVENT_CREATED"
    assert body["data"]["plateNumber"] == "123A4567"
    assert captured["camera_code"] == "CAM_001"
    assert captured["captured_at"] == detected_at
    assert captured["image_bytes"]
    assert captured["vehicle_detection"].detection_type == "VEHICLE"
    assert captured["backend_status"] is None

    detection_route.duplicate_detection_guard.clear()


def test_stream_event_highres_ocr_uses_deferred_finalized_event(monkeypatch) -> None:
    detection_route.duplicate_detection_guard.clear()
    detection_route.stream_finalized_results.clear()
    detection_route.stream_ocr_statuses.clear()
    detection_route.stream_ocr_status_seen_at.clear()

    event_id = "CAM_001-20260514143000-highres"
    detected_at = datetime(2026, 5, 14, 14, 30, 0)
    stream_result = StreamProcessingResult(
        stream_status=STREAM_STATUS_FINALIZED,
        camera_code="CAM_001",
        event_id=event_id,
        best_candidate_frame=BufferedFrame(
            camera_code="CAM_001",
            captured_at=detected_at,
            content_type="image/jpeg",
            image_bytes=make_test_image_bytes(),
            frame_number=123,
            bbox=(10, 10, 80, 50),
            confidence_score=0.92,
        ),
    )
    detection_route.stream_finalized_results[event_id] = stream_result

    captured = {}

    async def return_highres_detection(stream_result_arg, *, high_res_crop_bytes):
        captured["stream_result"] = stream_result_arg
        captured["high_res_crop_bytes"] = high_res_crop_bytes
        return make_recognized_detection(detected_at=detected_at)

    async def record_backend_send(result, detection_status=None):
        captured["backend_result"] = result
        captured["backend_status"] = detection_status
        return {"data": {"status": "FLOW_EVENT_CREATED", "flowEventId": 301}}

    monkeypatch.setattr(
        detection_route,
        "analyze_stream_best_candidate_with_highres_crop",
        return_highres_detection,
    )
    monkeypatch.setattr(
        detection_route.backend_client,
        "send_detection",
        record_backend_send,
    )

    response = client.post(
        f"/api/detections/stream-events/{event_id}/highres-ocr",
        files={
            "highResCrop": ("crop.jpg", make_test_image_bytes(), "image/jpeg"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["analysisStatus"] == "FLOW_EVENT_CREATED"
    assert body["data"]["plateNumber"] == "123A4567"
    assert captured["stream_result"] is stream_result
    assert captured["high_res_crop_bytes"]
    assert captured["backend_status"] is None
    assert event_id not in detection_route.stream_finalized_results
    assert detection_route.stream_ocr_statuses[event_id]["analysisStatus"] == "FLOW_EVENT_CREATED"
    assert detection_route.stream_ocr_statuses[event_id]["plateNumber"] == "123A4567"

    detection_route.duplicate_detection_guard.clear()
    detection_route.stream_ocr_statuses.clear()
    detection_route.stream_ocr_status_seen_at.clear()


def test_stream_frame_endpoint_uses_speed_config_json_override(monkeypatch) -> None:
    captured_config = {}

    class FakeStreamService:
        async def process_frame(
            self,
            *,
            camera_code,
            captured_at,
            content_type,
            image_bytes,
            speed_camera_config=None,
        ):
            captured_config["value"] = speed_camera_config
            return StreamProcessingResult(
                stream_status=STREAM_STATUS_TRACKING,
                camera_code=camera_code,
                event_id="CAM_001-20260514143000-test",
                frame_count=2,
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
            "speedConfigJson": """
            [
              {
                "cameraCode": "CAM_001",
                "lineA": [10, 20, 100, 20],
                "lineB": [10, 80, 100, 80],
                "roi": [[10, 20], [100, 20], [100, 80], [10, 80]],
                "distanceMeters": 14.0,
                "speedLimitKmh": 50.0,
                "enabled": true
              }
            ]
            """,
        },
        files={
            "image": ("frame.jpg", make_test_image_bytes(), "image/jpeg"),
        },
    )

    assert response.status_code == 200
    config = captured_config["value"]
    assert config is not None
    assert config.camera_code == "CAM_001"
    assert config.line_a.start.x == 10
    assert config.line_b.start.y == 80
    assert config.roi is not None
    assert len(config.roi) == 4


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


def test_stream_frame_endpoint_queues_background_ocr_when_result_is_deferred(
    monkeypatch,
) -> None:
    detection_route.duplicate_detection_guard.clear()

    captured = {}
    captured_at = datetime(2026, 5, 14, 14, 30, 0)
    image_bytes = make_test_image_bytes()

    class FakeStreamService:
        async def process_frame(self, *, camera_code, captured_at, content_type, image_bytes):
            best_candidate = BufferedFrame(
                camera_code=camera_code,
                captured_at=captured_at,
                content_type=content_type,
                image_bytes=image_bytes,
                frame_number=7,
                bbox=(10, 20, 80, 50),
                confidence_score=0.93,
            )
            return StreamProcessingResult(
                stream_status=STREAM_STATUS_FINALIZED,
                camera_code=camera_code,
                event_id="CAM_001-20260514143000-test",
                frame_count=6,
                best_candidate_frame_number=7,
                best_candidate_bbox=(10, 20, 80, 50),
                best_candidate_captured_at=captured_at,
                best_candidate_frame=best_candidate,
            )

    def return_detection_from_best_candidate(
        *,
        camera_code,
        captured_at,
        image_bytes,
        vehicle_detection=None,
    ):
        captured["camera_code"] = camera_code
        captured["captured_at"] = captured_at
        captured["image_bytes"] = image_bytes
        captured["vehicle_detection"] = vehicle_detection
        return make_recognized_detection(detected_at=captured_at)

    async def record_backend_send(result, detection_status=None):
        captured["backend_result"] = result
        captured["backend_status"] = detection_status
        return {"data": {"status": "FLOW_EVENT_CREATED"}}

    monkeypatch.setattr(
        detection_route,
        "stream_detection_service",
        FakeStreamService(),
    )
    monkeypatch.setattr(
        detection_route.inference_service,
        "detect_from_image_bytes_sync",
        return_detection_from_best_candidate,
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
            "capturedAt": captured_at.isoformat(),
        },
        files={
            "image": ("frame.jpg", image_bytes, "image/jpeg"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["streamStatus"] == "FINALIZED"
    assert body["message"] == "Vehicle event finalized; OCR and backend save queued"
    assert body["analysisStatus"] is None
    assert body["data"] is None
    assert captured["camera_code"] == "CAM_001"
    assert captured["captured_at"] == captured_at
    assert captured["image_bytes"] == image_bytes
    assert captured["vehicle_detection"].bbox == (10, 20, 80, 50)
    assert captured["backend_result"].plate_number == "123A4567"
    assert captured["backend_status"] is None

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
    assert body["speedViolation"]["isEstimated"] is True
    assert body["speedViolation"]["accuracyLevel"] == "ESTIMATED"
    assert body["speedViolationSent"] is True
    assert len(speed_payloads) == 1
    assert speed_payloads[0].flow_event_id == 301
    assert speed_payloads[0].plate_number == "123A4567"
    assert speed_payloads[0].measured_speed == 72.35

    detection_route.duplicate_detection_guard.clear()


def test_stream_frame_endpoint_keeps_detection_success_when_speed_violation_fails(
    monkeypatch,
    caplog,
) -> None:
    detection_route.duplicate_detection_guard.clear()

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

    async def raise_speed_send(request):
        raise httpx.ConnectError("speed backend unavailable")

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
        raise_speed_send,
    )
    caplog.set_level(logging.WARNING, logger="app.api.routes.detection")

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
    assert body["analysisStatus"] == "FLOW_EVENT_CREATED"
    assert body["speedViolation"]["measuredSpeed"] == 72.35
    assert body["speedViolationSent"] is False
    assert body["speedViolationSendError"] == (
        "Spring Boot speed violation API is not reachable"
    )
    assert "speed violation send failed after detection save" in caplog.text

    detection_route.duplicate_detection_guard.clear()


def test_stream_frame_endpoint_sends_duplicate_speed_violation_with_existing_flow_event(
    monkeypatch,
) -> None:
    detection_route.duplicate_detection_guard.clear()

    speed_payloads = []
    captured_at = datetime(2026, 5, 14, 14, 30, 5)
    result = make_recognized_detection(detected_at=captured_at)
    detection_route.duplicate_detection_guard.remember(result)
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
                event_id="CAM_001-20260514143005-test",
                frame_count=6,
                result=result,
                speed_measurements=[speed_violation],
                speed_violation=speed_violation,
            )

    async def record_duplicate_detection_send(result, detection_status=None):
        assert detection_status == "DUPLICATE_SKIPPED"
        return {
            "data": {
                "status": "DUPLICATE_SKIPPED",
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
        record_duplicate_detection_send,
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
    assert body["analysisStatus"] == "DUPLICATE_SKIPPED"
    assert body["speedViolationSent"] is True
    assert len(speed_payloads) == 1
    assert speed_payloads[0].flow_event_id == 301
    assert speed_payloads[0].plate_number == "123A4567"

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
    assert payload["frameImagePath"] == payload["imagePath"]
    assert payload["frameImageUrl"] == payload["imageUrl"]
    assert payload["processingStatus"] == "OCR_COMPLETED"
    assert payload["plateCropImagePath"].endswith("_plate_crop.jpg")
    assert payload["plateCropImageUrl"].endswith("_plate_crop.jpg")
    assert payload["ocrImagePath"].endswith("_ocr.jpg")
    assert payload["ocrImageUrl"].endswith("_ocr.jpg")
    assert captured["headers"]["X-Internal-Api-Key"] == "test-key"


def test_backend_client_retries_detection_transient_failure(monkeypatch) -> None:
    captured = {"attempts": 0}

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
            captured["attempts"] += 1
            if captured["attempts"] == 1:
                raise httpx.ConnectError("temporary detection outage")
            captured["json"] = json
            return FakeResponse()

    monkeypatch.setattr("app.services.backend_client.BACKEND_INTERNAL_API_KEY", "test-key")
    monkeypatch.setattr("app.services.backend_client.httpx.AsyncClient", FakeAsyncClient)
    monkeypatch.setattr("app.services.backend_client.SPRING_SPEED_VIOLATION_RETRY_ATTEMPTS", 2)
    monkeypatch.setattr(
        "app.services.backend_client.SPRING_SPEED_VIOLATION_RETRY_DELAY_SECONDS",
        0.0,
    )

    asyncio.run(
        BackendClient().send_detection(
            make_recognized_detection(),
            "FLOW_EVENT_CREATED",
        )
    )

    assert captured["attempts"] == 2
    assert captured["json"]["status"] == "FLOW_EVENT_CREATED"


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


def test_backend_client_retries_speed_violation_transient_failure(monkeypatch) -> None:
    captured = {"attempts": 0}

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
            captured["attempts"] += 1
            if captured["attempts"] == 1:
                raise httpx.ConnectError("temporary speed violation outage")
            captured["json"] = json
            return FakeResponse()

    monkeypatch.setattr("app.services.backend_client.BACKEND_INTERNAL_API_KEY", "test-key")
    monkeypatch.setattr("app.services.backend_client.httpx.AsyncClient", FakeAsyncClient)
    monkeypatch.setattr("app.services.backend_client.SPRING_SPEED_VIOLATION_RETRY_ATTEMPTS", 2)
    monkeypatch.setattr(
        "app.services.backend_client.SPRING_SPEED_VIOLATION_RETRY_DELAY_SECONDS",
        0.0,
    )

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

    assert captured["attempts"] == 2
    assert captured["json"]["flowEventId"] == 301


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
