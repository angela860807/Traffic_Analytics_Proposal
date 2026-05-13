from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import requests

from config import (
    CAMERA_CODE,
    DETECTION_IMAGE_SEND_URL,
    LIVE_FRAME_URL,
    REQUEST_TIMEOUT_SECONDS,
)

class FastApiClientError(RuntimeError):
    pass


def summarize_detection_response(result: dict[str, Any]) -> str:
    data = result.get("data") or {}
    message = result.get("message", "")
    analysis_status = result.get("analysisStatus") or _infer_analysis_status(message)

    return (
        "upload result: "
        f"accepted={result.get('accepted')}, "
        f"analysisStatus={analysis_status}, "
        f"cameraCode={data.get('cameraCode')}, "
        f"plateNumber={data.get('plateNumber') or '-'}, "
        f"detectionType={data.get('detectionType')}, "
        f"confidenceScore={data.get('confidenceScore')}, "
        f"detectedAt={data.get('detectedAt')}, "
        f"imageUrl={data.get('imageUrl') or '-'}, "
        f"plateCropImageUrl={data.get('plateCropImageUrl') or '-'}, "
        f"ocrImageUrl={data.get('ocrImageUrl') or '-'}, "
        f"message={message}"
    )


def _infer_analysis_status(message: str) -> str:
    if "OCR_FAILED" in message:
        return "OCR_FAILED"

    if "DUPLICATE_SKIPPED" in message:
        return "DUPLICATE_SKIPPED"

    if "sent to backend" in message:
        return "SENT_TO_BACKEND"

    return "ANALYSIS_ONLY"


def _captured_at_text(captured_at: datetime) -> str:
    return captured_at.replace(microsecond=0).isoformat()


def _raise_for_upload_error(response: requests.Response, url: str) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        body = response.text[:500]
        raise FastApiClientError(
            f"request failed: url={url}, "
            f"status={response.status_code}, body={body}"
        ) from exc


def _post_image(
    *,
    url: str,
    image_bytes: bytes,
    captured_at: datetime,
    filename: str,
) -> requests.Response:
    data = {
        "cameraCode": CAMERA_CODE,
        "capturedAt": _captured_at_text(captured_at),
    }
    files = {
        "image": (filename, image_bytes, "image/jpeg"),
    }

    try:
        response = requests.post(
            url,
            data=data,
            files=files,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise FastApiClientError(f"request failed: url={url}, error={exc}") from exc

    _raise_for_upload_error(response, url)
    return response


def upload_detection_image(
    image_bytes: bytes,
    captured_at: Optional[datetime] = None,
    filename: str = "capture.jpg",
) -> dict[str, Any]:
    response = _post_image(
        url=DETECTION_IMAGE_SEND_URL,
        image_bytes=image_bytes,
        captured_at=captured_at or datetime.now(),
        filename=filename,
    )
    return response.json()


def upload_live_frame(
    image_bytes: bytes,
    captured_at: Optional[datetime] = None,
    filename: str = "frame.jpg",
) -> None:
    _post_image(
        url=LIVE_FRAME_URL,
        image_bytes=image_bytes,
        captured_at=captured_at or datetime.now(),
        filename=filename,
    )


def upload_detection_image_file(
    image_path: Path,
    captured_at: Optional[datetime] = None,
) -> dict[str, Any]:
    return upload_detection_image(
        image_bytes=image_path.read_bytes(),
        captured_at=captured_at,
        filename=image_path.name,
    )
