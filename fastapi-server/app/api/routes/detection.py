from datetime import datetime

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.schemas.detection import DetectionResponse, RaspberryFrameRequest
from app.services.backend_client import BackendClient
from app.services.inference_service import InferenceService

router = APIRouter(prefix="/api/detections", tags=["detections"])

inference_service = InferenceService()
backend_client = BackendClient()


def should_send_to_backend(result) -> bool:
    return result.detection_type == "PLATE" and bool(result.plate_number)


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
            return DetectionResponse(
                accepted=True,
                message="Detection result created but not sent to backend because plate was not recognized",
                data=result,
            )
        await backend_client.send_detection(result)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="imageBase64 must be valid image base64",
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Spring Boot API returned error: {exc.response.status_code}",
        ) from exc
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

    return DetectionResponse(
        accepted=True,
        message="Mock detection result sent to backend",
        data=result,
    )

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
            return DetectionResponse(
                accepted=True,
                message="Detection result created but not sent to backend because plate was not recognized",
                data=result,
            )
        await backend_client.send_detection(result)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="image must be a valid jpg or png",
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Spring Boot API returned error: {exc.response.status_code}",
        ) from exc
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

    return DetectionResponse(
        accepted=True,
        message="Detection result sent to backend",
        data=result,
    )
