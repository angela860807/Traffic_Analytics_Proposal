from datetime import datetime, timezone
import logging
import time
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse, Response

from app.core.config import INTERNAL_API_MAX_BODY_BYTES
from app.core.request_context import request_id_context
from app.schemas.common import ApiErrorResponse
from app.services.runtime_metrics import predictive_runtime_metrics


logger = logging.getLogger(__name__)
PREDICTIVE_PATH_PREFIX = "/internal/v1/anomaly-detection"


async def request_context_middleware(
    request: Request,
    call_next,
) -> Response:
    request_id = request.headers.get("X-Request-Id") or str(uuid4())
    request.state.request_id = request_id
    started_at = time.perf_counter()
    context_token = request_id_context.set(request_id)

    try:
        if request.url.path.startswith("/internal/v1/"):
            content_length = request.headers.get("content-length")
            if (
                content_length is not None
                and content_length.isdigit()
                and int(content_length) > INTERNAL_API_MAX_BODY_BYTES
            ):
                response = _request_too_large_response(request_id)
            else:
                body = await request.body()
                if len(body) > INTERNAL_API_MAX_BODY_BYTES:
                    response = _request_too_large_response(request_id)
                else:
                    async def receive():
                        return {
                            "type": "http.request",
                            "body": body,
                            "more_body": False,
                        }

                    request._receive = receive
                    response = await call_next(request)
        else:
            response = await call_next(request)

        response.headers["X-Request-Id"] = request_id

        if request.url.path.startswith(PREDICTIVE_PATH_PREFIX):
            duration_ms = (time.perf_counter() - started_at) * 1000
            predictive_runtime_metrics.record_endpoint(
                endpoint=f"{request.method} {request.url.path}",
                duration_ms=duration_ms,
                failed=response.status_code >= 400,
            )
            logger.info(
                "predictive request completed: "
                "requestId=%s method=%s path=%s status=%s durationMs=%.3f",
                request_id,
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
            )

        return response
    finally:
        request_id_context.reset(context_token)


def _request_too_large_response(request_id: str) -> JSONResponse:
    payload = ApiErrorResponse(
        timestamp=datetime.now(timezone.utc),
        status=413,
        code="INVALID_REQUEST",
        message="요청 본문 크기가 허용 범위를 초과했습니다.",
        request_id=request_id,
    )
    return JSONResponse(
        status_code=413,
        content=payload.model_dump(by_alias=True, mode="json"),
        headers={"X-Request-Id": request_id},
    )
