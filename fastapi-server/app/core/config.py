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
    "/api/detections",
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
OCR_LANG = os.getenv("OCR_LANG", "korean")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")

YOLO_CONF_THRESHOLD = float(os.getenv("YOLO_CONF_THRESHOLD", "0.5"))
YOLO_IOU_THRESHOLD = float(os.getenv("YOLO_IOU_THRESHOLD", "0.4"))
YOLO_MAX_DET = int(os.getenv("YOLO_MAX_DET", "5"))
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
