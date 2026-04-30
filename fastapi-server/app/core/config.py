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

MODEL_PATH = os.getenv("MODEL_PATH", "")
OCR_LANG = os.getenv("OCR_LANG", "korean")
