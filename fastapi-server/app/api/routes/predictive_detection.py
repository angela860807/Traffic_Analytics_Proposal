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
from app.schemas.predictive_metrics import PredictiveMetricsResponse
from app.services.delivery_queue import camera_health_delivery_queue
from app.services.predictive_detector_adapter import (
    PredictiveDetectorAdapter,
    predictive_detector_adapter,
)
from app.services.runtime_metrics import predictive_runtime_metrics


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


@router.get(
    "/metrics",
    response_model=PredictiveMetricsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApiErrorResponse},
    },
)
async def get_predictive_metrics() -> PredictiveMetricsResponse:
    endpoints, detectors = predictive_runtime_metrics.snapshot()
    delivery_metrics = camera_health_delivery_queue.metrics
    client_metrics = camera_health_delivery_queue.client.metrics
    return PredictiveMetricsResponse.model_validate(
        {
            "endpoints": endpoints,
            "detectors": detectors,
            "delivery": {
                "queueSize": camera_health_delivery_queue.queue.qsize(),
                "enqueuedCount": delivery_metrics.enqueued_count,
                "deliveredCount": delivery_metrics.delivered_count,
                "retryCount": client_metrics.retry_count,
                "retryExhaustedCount": (
                    delivery_metrics.retry_exhausted_count
                ),
                "droppedCount": delivery_metrics.dropped_count,
                "lastNetworkRttMs": client_metrics.last_network_rtt_ms,
            },
        }
    )
