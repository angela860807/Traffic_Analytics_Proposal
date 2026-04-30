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

MODEL_PATH = os.getenv("MODEL_PATH", "")
OCR_LANG = os.getenv("OCR_LANG", "korean")
