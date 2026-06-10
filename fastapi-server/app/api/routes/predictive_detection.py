from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool

from app.core.security import require_internal_api_key
from app.schemas.common import ApiErrorResponse
from app.schemas.predictive_detection import (
    DegradationEvaluationRequest,
    DetectionEvaluationResponse,
    DetectorHealthResponse,
    RuleEvaluationRequest,
)
from app.services.predictive_detector_adapter import (
    PredictiveDetectorAdapter,
    predictive_detector_adapter,
)


router = APIRouter(
    prefix="/internal/v1/anomaly-detection",
    tags=["predictive-maintenance"],
    dependencies=[Depends(require_internal_api_key)],
)


def get_predictive_detector_adapter() -> PredictiveDetectorAdapter:
    return predictive_detector_adapter


@router.post(
    "/camera-health/evaluate",
    response_model=DetectionEvaluationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApiErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApiErrorResponse},
    },
)
async def evaluate_camera_health(
    request: RuleEvaluationRequest,
    adapter: PredictiveDetectorAdapter = Depends(
        get_predictive_detector_adapter
    ),
) -> DetectionEvaluationResponse:
    return await run_in_threadpool(adapter.evaluate_rules, request)


@router.post(
    "/camera-degradation/evaluate",
    response_model=DetectionEvaluationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApiErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApiErrorResponse},
    },
)
async def evaluate_camera_degradation(
    request: DegradationEvaluationRequest,
    adapter: PredictiveDetectorAdapter = Depends(
        get_predictive_detector_adapter
    ),
) -> DetectionEvaluationResponse:
    return await run_in_threadpool(adapter.evaluate_degradation, request)


@router.get(
    "/health",
    response_model=DetectorHealthResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApiErrorResponse},
    },
)
async def get_predictive_detector_health(
    adapter: PredictiveDetectorAdapter = Depends(
        get_predictive_detector_adapter
    ),
) -> DetectorHealthResponse:
    return await run_in_threadpool(adapter.get_health)
