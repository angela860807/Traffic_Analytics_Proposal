from datetime import datetime
import logging

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.schemas.detection import (
    DetectionResponse,
    RaspberryFrameRequest,
    StreamFrameResponse,
)
from app.schemas.speed import SpeedViolationCreateRequest
from app.services.backend_client import BackendClient
from app.services.duplicate_detection_guard import DuplicateDetectionGuard
from app.services.inference_service import InferenceService
from app.services.speed_config import SpeedCameraConfig, load_speed_camera_configs
from app.services.stream_event_service import (
    STREAM_STATUS_FINALIZED,
    STREAM_STATUS_IDLE,
    STREAM_STATUS_TRACKING,
    StreamEventService,
    StreamProcessingResult,
)
from app.services.vehicle_detector import VehicleDetection

router = APIRouter(prefix="/api/detections", tags=["detections"])
logger = logging.getLogger(__name__)
SPRING_ERROR_BODY_LIMIT = 500

inference_service = InferenceService()
backend_client = BackendClient()
duplicate_detection_guard = DuplicateDetectionGuard()
stream_detection_service = StreamEventService(inference_service=inference_service)


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


def extract_backend_flow_event_id(
    backend_response: dict | None,
) -> int | None:
    if not isinstance(backend_response, dict):
        return None

    data = backend_response.get("data")
    if not isinstance(data, dict):
        return None

    flow_event_id = data.get("flowEventId")
    if isinstance(flow_event_id, int):
        return flow_event_id
    if isinstance(flow_event_id, str) and flow_event_id.isdigit():
        return int(flow_event_id)

    return None


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


def build_stream_frame_response(
    stream_result: StreamProcessingResult,
    *,
    message: str,
    analysis_status: str | None = None,
) -> StreamFrameResponse:
    return StreamFrameResponse(
        accepted=True,
        message=message,
        stream_status=stream_result.stream_status,
        event_id=stream_result.event_id,
        camera_code=stream_result.camera_code,
        frame_count=stream_result.frame_count,
        bbox=list(stream_result.bbox) if stream_result.bbox is not None else None,
        bboxes=[
            list(bbox)
            for bbox in (stream_result.bboxes or [])
        ],
        bbox_confidence_score=stream_result.bbox_confidence_score,
        best_candidate_frame_number=stream_result.best_candidate_frame_number,
        best_candidate_bbox=(
            list(stream_result.best_candidate_bbox)
            if stream_result.best_candidate_bbox is not None
            else None
        ),
        best_candidate_captured_at=stream_result.best_candidate_captured_at,
        event_age_seconds=stream_result.event_age_seconds,
        speed_measurements=stream_result.speed_measurements,
        speed_violation=stream_result.speed_violation,
        speed_violation_sent=stream_result.speed_violation_sent,
        speed_violation_send_error=stream_result.speed_violation_send_error,
        analysis_status=analysis_status,
        data=stream_result.result,
    )


async def send_speed_violation_if_ready(
    *,
    stream_result: StreamProcessingResult,
    backend_response: dict | None,
) -> None:
    measurement = stream_result.speed_violation
    result = stream_result.result

    if measurement is None or result is None or not result.plate_number:
        return

    flow_event_id = extract_backend_flow_event_id(backend_response)
    if flow_event_id is None:
        logger.info(
            "speed violation not sent because flowEventId is missing: cameraCode=%s plateNumber=%s speed=%.2f",
            result.camera_code,
            result.plate_number,
            measurement.measured_speed,
        )
        return

    request = SpeedViolationCreateRequest(
        flow_event_id=flow_event_id,
        plate_number=result.plate_number,
        camera_code=result.camera_code,
        measured_speed=measurement.measured_speed,
        speed_limit=measurement.speed_limit,
        violation_image_path=result.image_path,
        violation_image_url=result.image_url,
        violated_at=measurement.measured_at,
    )
    try:
        await backend_client.send_speed_violation(request)
        stream_result.speed_violation_sent = True
    except httpx.HTTPStatusError as exc:
        stream_result.speed_violation_send_error = build_spring_error_detail(exc)
        logger.warning(
            "speed violation send failed after detection save: cameraCode=%s plateNumber=%s flowEventId=%s error=%s",
            result.camera_code,
            result.plate_number,
            flow_event_id,
            stream_result.speed_violation_send_error,
        )
    except httpx.RequestError as exc:
        stream_result.speed_violation_send_error = (
            "Spring Boot speed violation API is not reachable"
        )
        logger.warning(
            "speed violation send failed after detection save: cameraCode=%s plateNumber=%s flowEventId=%s error=%s",
            result.camera_code,
            result.plate_number,
            flow_event_id,
            exc,
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


def parse_speed_camera_config_override(
    *,
    camera_code: str,
    raw_speed_config_json: str | None,
) -> SpeedCameraConfig | None:
    if raw_speed_config_json is None or not raw_speed_config_json.strip():
        return None

    try:
        configs = load_speed_camera_configs(raw_speed_config_json)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"speedConfigJson is invalid: {exc}",
        ) from exc

    config = configs.get(camera_code)
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"speedConfigJson must include cameraCode {camera_code}",
        )

    return config


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


@router.post(
    "/stream-frame",
    response_model=StreamFrameResponse,
    status_code=status.HTTP_200_OK,
)
async def process_stream_frame(
    camera_code: str = Form(..., alias="cameraCode"),
    captured_at: datetime = Form(..., alias="capturedAt"),
    speed_config_json: str | None = Form(default=None, alias="speedConfigJson"),
    frame_number: int | None = Form(default=None, alias="frameNumber"),
    high_res_crop_frame_number: int | None = Form(
        default=None,
        alias="highResCropFrameNumber",
    ),
    image: UploadFile = File(...),
    high_res_crop: UploadFile | None = File(default=None, alias="highResCrop"),
) -> StreamFrameResponse:
    if image.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="image must be jpeg or png",
        )

    if (
        high_res_crop is not None
        and high_res_crop.content_type not in {"image/jpeg", "image/png"}
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="highResCrop must be jpeg or png",
        )

    image_bytes = await image.read()
    high_res_crop_bytes = (
        await high_res_crop.read()
        if high_res_crop is not None
        else None
    )
    speed_camera_config = parse_speed_camera_config_override(
        camera_code=camera_code,
        raw_speed_config_json=speed_config_json,
    )

    try:
        process_frame_kwargs = {
            "camera_code": camera_code,
            "captured_at": captured_at,
            "content_type": image.content_type,
            "image_bytes": image_bytes,
        }
        if frame_number is not None:
            process_frame_kwargs["frame_number"] = frame_number
        if high_res_crop_bytes is not None:
            process_frame_kwargs["high_res_crop_bytes"] = high_res_crop_bytes
            process_frame_kwargs["high_res_crop_content_type"] = (
                high_res_crop.content_type
            )
            if high_res_crop_frame_number is not None:
                process_frame_kwargs["high_res_crop_frame_number"] = (
                    high_res_crop_frame_number
                )
        if speed_camera_config is not None:
            process_frame_kwargs["speed_camera_config"] = speed_camera_config

        stream_result = await stream_detection_service.process_frame(
            **process_frame_kwargs,
        )

        if stream_result.stream_status == STREAM_STATUS_IDLE:
            return build_stream_frame_response(
                stream_result,
                message="Stream frame accepted; no vehicle event is active",
            )

        if stream_result.stream_status == STREAM_STATUS_TRACKING:
            return build_stream_frame_response(
                stream_result,
                message="Vehicle event is tracking",
            )

        if stream_result.stream_status != STREAM_STATUS_FINALIZED:
            return build_stream_frame_response(
                stream_result,
                message="Stream frame accepted",
            )

        result = stream_result.result

        if result is None:
            return build_stream_frame_response(
                stream_result,
                message="Vehicle event finalized without OCR candidate",
            )

        if not should_send_to_backend(result):
            await backend_client.send_detection(result, "OCR_FAILED")
            return build_stream_frame_response(
                stream_result,
                message="Vehicle event finalized and sent to backend as OCR_FAILED",
                analysis_status="OCR_FAILED",
            )

        if duplicate_detection_guard.is_duplicate(result):
            backend_response = await backend_client.send_detection(
                result,
                "DUPLICATE_SKIPPED",
            )
            await send_speed_violation_if_ready(
                stream_result=stream_result,
                backend_response=backend_response,
            )
            return build_stream_frame_response(
                stream_result,
                message="Vehicle event finalized and sent to backend as DUPLICATE_SKIPPED",
                analysis_status="DUPLICATE_SKIPPED",
            )

        backend_response = await backend_client.send_detection(result)
        duplicate_detection_guard.remember(result)
        await send_speed_violation_if_ready(
            stream_result=stream_result,
            backend_response=backend_response,
        )
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

    analysis_status = extract_backend_analysis_status(
        backend_response,
        "FLOW_EVENT_CREATED",
    )
    return build_stream_frame_response(
        stream_result,
        message=f"Vehicle event finalized and saved as {analysis_status}",
        analysis_status=analysis_status,
    )


@router.post(
    "/stream-frame/highres-ocr",
    response_model=DetectionResponse,
    status_code=status.HTTP_200_OK,
)
async def process_high_res_stream_ocr(
    camera_code: str = Form(..., alias="cameraCode"),
    captured_at: datetime = Form(..., alias="capturedAt"),
    frame_number: int = Form(..., alias="frameNumber"),
    high_res_crop: UploadFile = File(..., alias="highResCrop"),
) -> DetectionResponse:
    if high_res_crop.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="highResCrop must be jpeg or png",
        )

    high_res_crop_bytes = await high_res_crop.read()

    try:
        result = await inference_service.detect_from_image_bytes(
            camera_code=camera_code,
            captured_at=captured_at,
            image_bytes=high_res_crop_bytes,
            vehicle_detection=VehicleDetection(
                detection_type="VEHICLE",
                confidence_score=1.0,
                bbox=(0, 0, 1, 1),
            ),
        )
        if not should_send_to_backend(result):
            await backend_client.send_detection(result, "OCR_FAILED")
            return DetectionResponse(
                accepted=True,
                message=(
                    "High-resolution OCR result sent to backend as OCR_FAILED "
                    f"for frame {frame_number}"
                ),
                analysis_status="OCR_FAILED",
                data=result,
            )
        if duplicate_detection_guard.is_duplicate(result):
            await backend_client.send_detection(result, "DUPLICATE_SKIPPED")
            return build_duplicate_detection_response(result)
        backend_response = await backend_client.send_detection(result)
        duplicate_detection_guard.remember(result)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="highResCrop must be a valid jpg or png",
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
