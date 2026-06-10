import json
import os

from dotenv import load_dotenv

load_dotenv()


def _load_camera_id_map(raw_value: str) -> dict[str, int]:
    if not raw_value.strip():
        return {}

    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise ValueError("CAMERA_ID_MAP_JSON must be valid JSON") from exc

    if not isinstance(parsed, dict):
        raise ValueError("CAMERA_ID_MAP_JSON must be a JSON object")

    camera_ids: dict[str, int] = {}
    for camera_code, camera_id in parsed.items():
        if not isinstance(camera_code, str) or not camera_code.strip():
            raise ValueError("CAMERA_ID_MAP_JSON keys must be camera code strings")
        if isinstance(camera_id, bool) or not isinstance(camera_id, int) or camera_id <= 0:
            raise ValueError("CAMERA_ID_MAP_JSON values must be positive integers")
        camera_ids[camera_code.strip()] = camera_id

    return camera_ids


APP_NAME = os.getenv("APP_NAME", "traffic-ai-server")
APP_ENV = os.getenv("APP_ENV", "local")

SPRING_BACKEND_BASE_URL = os.getenv(
    "SPRING_BACKEND_BASE_URL",
    "http://127.0.0.1:8080",
)

SPRING_DETECTION_PATH = os.getenv(
    "SPRING_DETECTION_PATH",
    "/api/v1/detection-logs",
)
SPRING_SPEED_VIOLATION_PATH = os.getenv(
    "SPRING_SPEED_VIOLATION_PATH",
    "/api/speed-violations",
)
SPRING_SPEED_VIOLATION_RETRY_ATTEMPTS = int(
    os.getenv("SPRING_SPEED_VIOLATION_RETRY_ATTEMPTS", "2")
)
SPRING_SPEED_VIOLATION_RETRY_DELAY_SECONDS = float(
    os.getenv("SPRING_SPEED_VIOLATION_RETRY_DELAY_SECONDS", "0.2")
)
SPRING_CAMERA_HEALTH_PATH = os.getenv(
    "SPRING_CAMERA_HEALTH_PATH",
    "/internal/v1/camera-health-samples",
)
SPRING_CAMERA_HEALTH_TIMEOUT_SECONDS = float(
    os.getenv("SPRING_CAMERA_HEALTH_TIMEOUT_SECONDS", "3")
)
SPRING_CAMERA_HEALTH_RETRY_ATTEMPTS = int(
    os.getenv("SPRING_CAMERA_HEALTH_RETRY_ATTEMPTS", "3")
)
SPRING_CAMERA_HEALTH_RETRY_BASE_DELAY_SECONDS = float(
    os.getenv("SPRING_CAMERA_HEALTH_RETRY_BASE_DELAY_SECONDS", "0.5")
)

BACKEND_INTERNAL_API_KEY = os.getenv(
    "BACKEND_INTERNAL_API_KEY",
    ""
)

DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Seoul")

CAMERA_HEALTH_WINDOW_SECONDS = int(
    os.getenv("CAMERA_HEALTH_WINDOW_SECONDS", "60")
)
CAMERA_HEALTH_DELIVERY_QUEUE_MAX_SIZE = int(
    os.getenv("CAMERA_HEALTH_DELIVERY_QUEUE_MAX_SIZE", "1000")
)
CAMERA_HEALTH_DELIVERY_ENABLED = (
    os.getenv("CAMERA_HEALTH_DELIVERY_ENABLED", "false").lower() == "true"
)
CAMERA_HEALTH_DELIVERY_POLL_SECONDS = float(
    os.getenv("CAMERA_HEALTH_DELIVERY_POLL_SECONDS", "1")
)
CAMERA_HEALTH_SHUTDOWN_TIMEOUT_SECONDS = float(
    os.getenv("CAMERA_HEALTH_SHUTDOWN_TIMEOUT_SECONDS", "5")
)
CAMERA_PROCESSOR_CODE = os.getenv("CAMERA_PROCESSOR_CODE", "edge-01")
CAMERA_ID_MAP = _load_camera_id_map(os.getenv("CAMERA_ID_MAP_JSON", ""))
PREDICTIVE_MODEL_DIR = os.getenv(
    "PREDICTIVE_MODEL_DIR",
    "models/predictive",
)

DETECTION_CONFIDENCE_THRESHOLD = float(
    os.getenv("DETECTION_CONFIDENCE_THRESHOLD", "0.7")
)

DUPLICATE_WINDOW_SECONDS = int(
    os.getenv("DUPLICATE_WINDOW_SECONDS", "10")
)

IMAGE_STORAGE_DIR = os.getenv(
    "IMAGE_STORAGE_DIR",
    "storage/detections",
)

STATIC_DETECTIONS_URL_PREFIX = os.getenv(
    "STATIC_DETECTIONS_URL_PREFIX",
    "/static/detections",
)

MODEL_PATH = os.getenv("MODEL_PATH", "")
PLATE_MODEL_PATH = os.getenv("PLATE_MODEL_PATH") or MODEL_PATH
OCR_LANG = os.getenv("OCR_LANG", "korean")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")

YOLO_CONF_THRESHOLD = float(os.getenv("YOLO_CONF_THRESHOLD", "0.5"))
YOLO_IOU_THRESHOLD = float(os.getenv("YOLO_IOU_THRESHOLD", "0.4"))
YOLO_MAX_DET = int(os.getenv("YOLO_MAX_DET", "5"))
VEHICLE_MODEL_PATH = os.getenv("VEHICLE_MODEL_PATH", "")
VEHICLE_MODEL_NAME = os.getenv("VEHICLE_MODEL_NAME", "")
VEHICLE_MODEL_SOURCE = VEHICLE_MODEL_PATH or VEHICLE_MODEL_NAME
VEHICLE_YOLO_CONF_THRESHOLD = float(
    os.getenv("VEHICLE_YOLO_CONF_THRESHOLD", "0.35")
)
VEHICLE_YOLO_IOU_THRESHOLD = float(
    os.getenv("VEHICLE_YOLO_IOU_THRESHOLD", "0.45")
)
VEHICLE_YOLO_MAX_DET = int(os.getenv("VEHICLE_YOLO_MAX_DET", "10"))
VEHICLE_CLASS_NAMES = tuple(
    class_name.strip().lower()
    for class_name in os.getenv(
        "VEHICLE_CLASS_NAMES",
        "car,bus,truck,motorcycle",
    ).split(",")
    if class_name.strip()
)
DETECTION_PREPROCESS_MODE = os.getenv("DETECTION_PREPROCESS_MODE", "none").lower()
PLATE_CROP_PADDING_RATIO = float(os.getenv("PLATE_CROP_PADDING_RATIO", "0.10"))
OCR_MIN_CONFIDENCE = float(os.getenv("OCR_MIN_CONFIDENCE", "0.5"))
OCR_PREPROCESS_SCALE = float(os.getenv("OCR_PREPROCESS_SCALE", "2.0"))
OCR_ADAPTIVE_BLOCK_SIZE = int(os.getenv("OCR_ADAPTIVE_BLOCK_SIZE", "31"))
OCR_ADAPTIVE_C = int(os.getenv("OCR_ADAPTIVE_C", "5"))
SAVE_PLATE_CROP = os.getenv("SAVE_PLATE_CROP", "true").lower() == "true"
SAVE_VEHICLE_CROP = os.getenv("SAVE_VEHICLE_CROP", "false").lower() == "true"
SAVE_OCR_PREPROCESSED_IMAGE = (
    os.getenv("SAVE_OCR_PREPROCESSED_IMAGE", "false").lower() == "true"
)

STREAM_FPS = int(os.getenv("STREAM_FPS", "5"))
PRE_BUFFER_SECONDS = float(os.getenv("PRE_BUFFER_SECONDS", "2"))
POST_MISS_FRAMES = int(os.getenv("POST_MISS_FRAMES", "5"))
MAX_EVENT_SECONDS = float(os.getenv("MAX_EVENT_SECONDS", "4"))
TOP_N_OCR_FRAMES = int(os.getenv("TOP_N_OCR_FRAMES", "1"))
SAVE_EVENT_DEBUG = os.getenv("SAVE_EVENT_DEBUG", "false").lower() == "true"
STREAM_TRACK_TTL_SECONDS = float(os.getenv("STREAM_TRACK_TTL_SECONDS", "2.0"))
STREAM_TRACK_MIN_IOU = float(os.getenv("STREAM_TRACK_MIN_IOU", "0.10"))
STREAM_TRACK_MAX_CENTER_DISTANCE_PIXELS = float(
    os.getenv("STREAM_TRACK_MAX_CENTER_DISTANCE_PIXELS", "180.0")
)
STREAM_BBOX_MIN_AREA_RATIO = float(os.getenv("STREAM_BBOX_MIN_AREA_RATIO", "0.002"))
STREAM_BBOX_MAX_AREA_RATIO = float(os.getenv("STREAM_BBOX_MAX_AREA_RATIO", "0.40"))
STREAM_BBOX_MIN_ASPECT_RATIO = float(os.getenv("STREAM_BBOX_MIN_ASPECT_RATIO", "0.45"))
STREAM_BBOX_MAX_ASPECT_RATIO = float(os.getenv("STREAM_BBOX_MAX_ASPECT_RATIO", "4.50"))
STREAM_BBOX_MIN_EDGE_MARGIN_RATIO = float(
    os.getenv("STREAM_BBOX_MIN_EDGE_MARGIN_RATIO", "0.0")
)
STREAM_BBOX_ROI_NORMALIZED = os.getenv("STREAM_BBOX_ROI_NORMALIZED", "").strip()

SPEED_DETECTION_ENABLED = os.getenv("SPEED_DETECTION_ENABLED", "false").lower() == "true"
SPEED_DEFAULT_DISTANCE_METERS = float(
    os.getenv("SPEED_DEFAULT_DISTANCE_METERS", "10.0")
)
SPEED_DEFAULT_LIMIT_KMH = float(os.getenv("SPEED_DEFAULT_LIMIT_KMH", "70.0"))
SPEED_DEFAULT_LINE_A = os.getenv("SPEED_DEFAULT_LINE_A", "320,360,960,360")
SPEED_DEFAULT_LINE_B = os.getenv("SPEED_DEFAULT_LINE_B", "320,520,960,520")
SPEED_CAMERA_CONFIGS_JSON = os.getenv("SPEED_CAMERA_CONFIGS_JSON", "")
SPEED_DEFAULT_MODE = os.getenv("SPEED_DEFAULT_MODE", "TRACK_DELTA")
SPEED_TRACK_MAX_DISTANCE_PIXELS = float(
    os.getenv("SPEED_TRACK_MAX_DISTANCE_PIXELS", "120.0")
)
SPEED_TRACK_TTL_SECONDS = float(os.getenv("SPEED_TRACK_TTL_SECONDS", "2.0"))
SPEED_MIN_ELAPSED_SECONDS = float(os.getenv("SPEED_MIN_ELAPSED_SECONDS", "0.05"))
SPEED_MAX_REASONABLE_KMH = float(os.getenv("SPEED_MAX_REASONABLE_KMH", "220.0"))
SPEED_TRACK_DELTA_WINDOW_SECONDS = float(
    os.getenv("SPEED_TRACK_DELTA_WINDOW_SECONDS", "1.0")
)
SPEED_TRACK_DELTA_MIN_ELAPSED_SECONDS = float(
    os.getenv("SPEED_TRACK_DELTA_MIN_ELAPSED_SECONDS", "0.3")
)
