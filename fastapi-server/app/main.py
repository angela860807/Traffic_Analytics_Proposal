from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import camera_stream, detection, health
from app.core.config import IMAGE_STORAGE_DIR, STATIC_DETECTIONS_URL_PREFIX
from app.services.speed_config import validate_speed_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_speed_settings()
    yield


app = FastAPI(
    title="Traffic AI Server",
    version="0.1.0",
    lifespan=lifespan,
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
