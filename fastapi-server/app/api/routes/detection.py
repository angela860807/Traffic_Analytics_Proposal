from datetime import datetime
import logging

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.schemas.detection import DetectionResponse, RaspberryFrameRequest
from app.services.backend_client import BackendClient
from app.services.duplicate_detection_guard import DuplicateDetectionGuard
from app.services.inference_service import InferenceService

router = APIRouter(prefix="/api/detections", tags=["detections"])
logger = logging.getLogger(__name__)
SPRING_ERROR_BODY_LIMIT = 500

inference_service = InferenceService()
backend_client = BackendClient()
duplicate_detection_guard = DuplicateDetectionGuard()


def should_send_to_backend(result) -> bool:
    return result.detection_type == "PLATE" and bool(result.plate_number)


def build_unrecognized_plate_response(result) -> DetectionResponse:
    return DetectionResponse(
        accepted=True,
        message="Detection result sent to backend as OCR_FAILED",
        analysis_status="OCR_FAILED",
        data=result,
    )


def build_duplicate_detection_response(result) -> DetectionResponse:
    return DetectionResponse(
        accepted=True,
        message="Duplicate detection sent to backend as DUPLICATE_SKIPPED",
        analysis_status="DUPLICATE_SKIPPED",
        data=result,
    )


def extract_backend_analysis_status(
    backend_response: dict | None,
    fallback: str,
) -> str:
    if not isinstance(backend_response, dict):
        return fallback

    data = backend_response.get("data")

    if isinstance(data, dict):
        status_value = data.get("status")
        if isinstance(status_value, str) and status_value:
            return status_value

    return fallback


def build_backend_success_response(
    result,
    backend_response: dict | None,
    fallback_status: str = "FLOW_EVENT_CREATED",
) -> DetectionResponse:
    analysis_status = extract_backend_analysis_status(
        backend_response,
        fallback_status,
    )
    return DetectionResponse(
        accepted=True,
        message=f"Detection result saved as {analysis_status}",
        analysis_status=analysis_status,
        data=result,
    )


def build_spring_error_detail(exc: httpx.HTTPStatusError) -> str:
    status_code = exc.response.status_code
    response_body = exc.response.text.strip()

    if not response_body:
        return f"Spring Boot API returned error: {status_code}"

    if len(response_body) > SPRING_ERROR_BODY_LIMIT:
        response_body = f"{response_body[:SPRING_ERROR_BODY_LIMIT]}..."

    return f"Spring Boot API returned error: {status_code}; body={response_body}"


def raise_spring_http_exception(exc: httpx.HTTPStatusError) -> None:
    detail = build_spring_error_detail(exc)
    logger.warning(detail)
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=detail,
    ) from exc


@router.post(
    "/mock",
    response_model=DetectionResponse,
    status_code=status.HTTP_200_OK,
)
async def create_mock_detection(
    request: RaspberryFrameRequest,
) -> DetectionResponse:
    try:
        result = await inference_service.detect_from_frame(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="imageBase64 must be valid image base64",
        ) from exc

    return DetectionResponse(
        accepted=True,
        message="Mock detection result created",
        analysis_status="ANALYSIS_ONLY",
        data=result,
    )


@router.post(
    "/image",
    response_model=DetectionResponse,
    status_code=status.HTTP_200_OK,
)
async def create_detection_from_image(
    camera_code: str = Form(..., alias="cameraCode"),
    captured_at: datetime = Form(..., alias="capturedAt"),
    image: UploadFile = File(...),
) -> DetectionResponse:
    if image.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="image must be jpeg or png",
        )

    image_bytes = await image.read()

    try:
        result = await inference_service.detect_from_image_bytes(
            camera_code=camera_code,
            captured_at=captured_at,
            image_bytes=image_bytes,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="image must be a valid jpg or png",
        ) from exc

    return DetectionResponse(
        accepted=True,
        message="Detection result created from image",
        analysis_status="ANALYSIS_ONLY",
        data=result,
    )


@router.post(
    "/mock/send",
    response_model=DetectionResponse,
    status_code=status.HTTP_200_OK,
)
async def create_and_send_mock_detection(
    request: RaspberryFrameRequest,
) -> DetectionResponse:
    try:
        result = await inference_service.detect_from_frame(request)
        if not should_send_to_backend(result):
            await backend_client.send_detection(result, "OCR_FAILED")
            return build_unrecognized_plate_response(result)
        if duplicate_detection_guard.is_duplicate(result):
            await backend_client.send_detection(result, "DUPLICATE_SKIPPED")
            return build_duplicate_detection_response(result)
        backend_response = await backend_client.send_detection(result)
        duplicate_detection_guard.remember(result)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="imageBase64 must be valid image base64",
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise_spring_http_exception(exc)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Spring Boot API is not reachable",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return build_backend_success_response(result, backend_response)

@router.post("/image/send", response_model=DetectionResponse)
async def create_and_send_detection_from_image(
    camera_code: str = Form(..., alias="cameraCode"),
    captured_at: datetime = Form(..., alias="capturedAt"),
    image: UploadFile = File(...),
) -> DetectionResponse:
    if image.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="image must be jpeg or png",
        )

    image_bytes = await image.read()

    try:
        result = await inference_service.detect_from_image_bytes(
            camera_code=camera_code,
            captured_at=captured_at,
            image_bytes=image_bytes,
        )
        if not should_send_to_backend(result):
            await backend_client.send_detection(result, "OCR_FAILED")
            return build_unrecognized_plate_response(result)
        if duplicate_detection_guard.is_duplicate(result):
            await backend_client.send_detection(result, "DUPLICATE_SKIPPED")
            return build_duplicate_detection_response(result)
        backend_response = await backend_client.send_detection(result)
        duplicate_detection_guard.remember(result)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="image must be a valid jpg or png",
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise_spring_http_exception(exc)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Spring Boot API is not reachable",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return build_backend_success_response(result, backend_response)
