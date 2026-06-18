from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.common import ApiErrorResponse


class InternalApiError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


class InternalApiUnauthorizedError(InternalApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=401,
            code="UNAUTHORIZED",
            message="내부 API 인증 정보가 올바르지 않습니다.",
        )


class DetectorUnavailableError(InternalApiError):
    def __init__(self, message: str = "예지보전 탐지기를 사용할 수 없습니다.") -> None:
        super().__init__(
            status_code=503,
            code="INTERNAL_DETECTOR_UNAVAILABLE",
            message=message,
        )


async def internal_api_error_handler(
    request: Request,
    exc: InternalApiError,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    request_id = request_id or request.headers.get("X-Request-Id") or str(uuid4())
    payload = ApiErrorResponse(
        timestamp=datetime.now(timezone.utc),
        status=exc.status_code,
        code=exc.code,
        message=exc.message,
        request_id=request_id,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=payload.model_dump(by_alias=True, mode="json"),
        headers={"X-Request-Id": request_id},
    )


async def request_validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    request_id = request_id or request.headers.get("X-Request-Id") or str(uuid4())
    field_errors = []
    for error in exc.errors():
        location = [
            str(item)
            for item in error.get("loc", ())
            if item not in {"body", "query", "path", "header"}
        ]
        field_errors.append(
            {
                "field": ".".join(location) or "request",
                "reason": error.get("msg", "Invalid value"),
            }
        )

    payload = ApiErrorResponse(
        timestamp=datetime.now(timezone.utc),
        status=400,
        code="INVALID_REQUEST",
        message="요청값이 올바르지 않습니다.",
        request_id=request_id,
        field_errors=field_errors,
    )
    return JSONResponse(
        status_code=400,
        content=payload.model_dump(by_alias=True, mode="json"),
        headers={"X-Request-Id": request_id},
    )
