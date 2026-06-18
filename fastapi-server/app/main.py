from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from app.api.routes import camera_stream, detection, health, predictive_detection
from app.core.config import IMAGE_STORAGE_DIR, STATIC_DETECTIONS_URL_PREFIX
from app.core.exceptions import (
    InternalApiError,
    internal_api_error_handler,
    request_validation_error_handler,
)
from app.core.middleware import request_context_middleware
from app.services.delivery_queue import camera_health_delivery_service
from app.services.predictive_detector_adapter import predictive_detector_adapter
from app.services.speed_config import validate_speed_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_speed_settings()
    predictive_detector_adapter.initialize()
    await camera_health_delivery_service.start()
    app.state.camera_health_delivery_service = camera_health_delivery_service
    try:
        yield
    finally:
        await camera_health_delivery_service.stop()


app = FastAPI(
    title="Traffic AI Server",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_exception_handler(InternalApiError, internal_api_error_handler)
app.add_exception_handler(
    RequestValidationError,
    request_validation_error_handler,
)
app.middleware("http")(request_context_middleware)

Path(IMAGE_STORAGE_DIR).mkdir(parents=True, exist_ok=True)

app.mount(
    STATIC_DETECTIONS_URL_PREFIX,
    StaticFiles(directory=IMAGE_STORAGE_DIR),
    name="detection-images",
)

app.include_router(health.router)
app.include_router(detection.router)
app.include_router(camera_stream.router)
app.include_router(predictive_detection.router)
