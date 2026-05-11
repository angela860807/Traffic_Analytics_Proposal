import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()


FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://192.168.10.91:8000").rstrip("/")
CAMERA_CODE = os.getenv("CAMERA_CODE", "CAM_001")

HEALTH_URL = f"{FASTAPI_BASE_URL}/health"
DETECTION_IMAGE_URL = f"{FASTAPI_BASE_URL}/api/detections/image"
DETECTION_IMAGE_SEND_URL = f"{FASTAPI_BASE_URL}/api/detections/image/send"
LIVE_FRAME_URL = f"{FASTAPI_BASE_URL}/api/camera/frame"

REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
CAPTURE_INTERVAL_SECONDS = float(os.getenv("CAPTURE_INTERVAL_SECONDS", "5"))
LIVE_FRAME_INTERVAL_SECONDS = float(os.getenv("LIVE_FRAME_INTERVAL_SECONDS", "0.2"))
JPEG_QUALITY = int(os.getenv("JPEG_QUALITY", "80"))

CAMERA_WIDTH = int(os.getenv("CAMERA_WIDTH", "640"))
CAMERA_HEIGHT = int(os.getenv("CAMERA_HEIGHT", "480"))
