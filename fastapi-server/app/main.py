from fastapi import FastAPI

from app.api.routes import camera_stream, detection, health
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from app.core.config import IMAGE_STORAGE_DIR, STATIC_DETECTIONS_URL_PREFIX

app = FastAPI(
    title="Traffic AI Server",
    version="0.1.0",
)

Path(IMAGE_STORAGE_DIR).mkdir(parents=True, exist_ok=True)

app.mount(
    STATIC_DETECTIONS_URL_PREFIX,
    StaticFiles(directory=IMAGE_STORAGE_DIR),
    name="detection-images",
)

app.include_router(health.router)
app.include_router(detection.router)
app.include_router(camera_stream.router)
