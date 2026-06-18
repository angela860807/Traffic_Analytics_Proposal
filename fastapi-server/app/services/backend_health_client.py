import asyncio
from dataclasses import dataclass
import logging
import time
from uuid import UUID, uuid4

import httpx

from app.core.config import (
    BACKEND_INTERNAL_API_KEY,
    SPRING_BACKEND_BASE_URL,
    SPRING_CAMERA_HEALTH_PATH,
    SPRING_CAMERA_HEALTH_RETRY_ATTEMPTS,
    SPRING_CAMERA_HEALTH_RETRY_BASE_DELAY_SECONDS,
    SPRING_CAMERA_HEALTH_TIMEOUT_SECONDS,
)
from app.schemas.camera_health import (
    CameraHealthSampleRequest,
    CameraHealthSampleResponse,
)


logger = logging.getLogger(__name__)


@dataclass
class BackendHealthClientMetrics:
    retry_count: int = 0
    last_network_rtt_ms: float | None = None


class BackendHealthClient:
    def __init__(
        self,
        *,
        base_url: str = SPRING_BACKEND_BASE_URL,
        path: str = SPRING_CAMERA_HEALTH_PATH,
        api_key: str = BACKEND_INTERNAL_API_KEY,
        timeout_seconds: float = SPRING_CAMERA_HEALTH_TIMEOUT_SECONDS,
        retry_attempts: int = SPRING_CAMERA_HEALTH_RETRY_ATTEMPTS,
        retry_base_delay_seconds: float = (
            SPRING_CAMERA_HEALTH_RETRY_BASE_DELAY_SECONDS
        ),
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than 0")
        if retry_attempts <= 0:
            raise ValueError("retry_attempts must be greater than 0")
        if retry_base_delay_seconds < 0:
            raise ValueError("retry_base_delay_seconds cannot be negative")

        self.url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.retry_attempts = retry_attempts
        self.retry_base_delay_seconds = retry_base_delay_seconds
        self.transport = transport
        self.metrics = BackendHealthClientMetrics()

    async def send_sample(
        self,
        request: CameraHealthSampleRequest,
        *,
        request_id: UUID | None = None,
    ) -> CameraHealthSampleResponse:
        if not self.api_key:
            raise RuntimeError("BACKEND_INTERNAL_API_KEY is not set")

        stable_request_id = request_id or uuid4()
        headers = {
            "X-Internal-Api-Key": self.api_key,
            "X-Request-Id": str(stable_request_id),
            "Content-Type": "application/json",
        }
        payload = request.model_dump(by_alias=True, mode="json")

        for attempt in range(1, self.retry_attempts + 1):
            try:
                request_started_at = time.perf_counter()
                async with httpx.AsyncClient(
                    timeout=self.timeout_seconds,
                    transport=self.transport,
                ) as client:
                    response = await client.post(
                        self.url,
                        json=payload,
                        headers=headers,
                    )
                response.raise_for_status()
                self.metrics.last_network_rtt_ms = round(
                    (time.perf_counter() - request_started_at) * 1000,
                    3,
                )
                return CameraHealthSampleResponse.model_validate(
                    response.json()
                )
            except httpx.HTTPStatusError as exc:
                if (
                    not self._should_retry_status(exc.response.status_code)
                    or attempt >= self.retry_attempts
                ):
                    raise
                await self._sleep_before_retry(
                    attempt=attempt,
                    request=request,
                    exc=exc,
                )
            except httpx.RequestError as exc:
                if attempt >= self.retry_attempts:
                    raise
                await self._sleep_before_retry(
                    attempt=attempt,
                    request=request,
                    exc=exc,
                )

        raise RuntimeError("camera health retry loop exited unexpectedly")

    @staticmethod
    def _should_retry_status(status_code: int) -> bool:
        return status_code == 429 or 500 <= status_code <= 599

    async def _sleep_before_retry(
        self,
        *,
        attempt: int,
        request: CameraHealthSampleRequest,
        exc: Exception,
    ) -> None:
        self.metrics.retry_count += 1
        delay_seconds = self.retry_base_delay_seconds * (2 ** (attempt - 1))
        logger.warning(
            "camera health send failed; retrying: "
            "cameraId=%s sampledAt=%s attempt=%s/%s delaySeconds=%.3f error=%s",
            request.camera_id,
            request.sampled_at.isoformat(),
            attempt + 1,
            self.retry_attempts,
            delay_seconds,
            exc,
        )
        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)
