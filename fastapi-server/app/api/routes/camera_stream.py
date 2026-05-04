import time
from datetime import datetime
from typing import Generator

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response, StreamingResponse

from app.services.frame_buffer import LatestFrame, frame_buffer

router = APIRouter(prefix="/api/camera", tags=["camera"])


@router.post("/frame", status_code=status.HTTP_204_NO_CONTENT)
async def receive_camera_frame(
    camera_code: str = Form(..., alias="cameraCode"),
    captured_at: datetime = Form(..., alias="capturedAt"),
    image: UploadFile = File(...),
) -> Response:
    if image.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="image must be jpeg or png",
        )

    image_bytes = await image.read()

    frame_buffer.set_frame(
        LatestFrame(
            camera_code=camera_code,
            captured_at=captured_at,
            content_type=image.content_type,
            image_bytes=image_bytes,
        )
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/latest.jpg")
async def get_latest_frame() -> Response:
    latest_frame = frame_buffer.get_frame()

    if latest_frame is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="camera frame is not available yet",
        )

    return Response(
        content=latest_frame.image_bytes,
        media_type=latest_frame.content_type,
        headers={
            "X-Camera-Code": latest_frame.camera_code,
            "X-Captured-At": latest_frame.captured_at.isoformat(),
        },
    )


def generate_mjpeg_stream() -> Generator[bytes, None, None]:
    last_frame_bytes: bytes | None = None

    while True:
        latest_frame = frame_buffer.get_frame()

        if latest_frame is not None and latest_frame.image_bytes != last_frame_bytes:
            last_frame_bytes = latest_frame.image_bytes

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + latest_frame.image_bytes
                + b"\r\n"
            )

        time.sleep(0.05)


@router.get("/live")
async def live_camera_stream() -> StreamingResponse:
    return StreamingResponse(
        generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
