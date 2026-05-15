import os

from dotenv import load_dotenv

load_dotenv()

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

BACKEND_INTERNAL_API_KEY = os.getenv(
    "BACKEND_INTERNAL_API_KEY",
    ""
)

DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Seoul")

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
SAVE_OCR_PREPROCESSED_IMAGE = (
    os.getenv("SAVE_OCR_PREPROCESSED_IMAGE", "true").lower() == "true"
)

STREAM_FPS = int(os.getenv("STREAM_FPS", "5"))
PRE_BUFFER_SECONDS = float(os.getenv("PRE_BUFFER_SECONDS", "2"))
POST_MISS_FRAMES = int(os.getenv("POST_MISS_FRAMES", "5"))
MAX_EVENT_SECONDS = float(os.getenv("MAX_EVENT_SECONDS", "4"))
TOP_N_OCR_FRAMES = int(os.getenv("TOP_N_OCR_FRAMES", "1"))
SAVE_EVENT_DEBUG = os.getenv("SAVE_EVENT_DEBUG", "false").lower() == "true"
