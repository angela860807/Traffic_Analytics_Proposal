from fastapi import FastAPI

from app.api.routes import detection, health

app = FastAPI(
    title="Traffic AI Server",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(detection.router)
