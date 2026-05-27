import asyncio
import logging

import httpx

from app.core.config import (
    BACKEND_INTERNAL_API_KEY,
    SPRING_BACKEND_BASE_URL,
    SPRING_DETECTION_PATH,
    SPRING_SPEED_VIOLATION_PATH,
    SPRING_SPEED_VIOLATION_RETRY_ATTEMPTS,
    SPRING_SPEED_VIOLATION_RETRY_DELAY_SECONDS,
)
from app.schemas.detection import DetectionResult
from app.schemas.speed import SpeedViolationCreateRequest


logger = logging.getLogger(__name__)


class BackendClient:
    async def send_detection(
        self,
        result: DetectionResult,
        analysis_status: str | None = None,
    ) -> dict:
        if not BACKEND_INTERNAL_API_KEY:
            raise RuntimeError("BACKEND_INTERNAL_API_KEY is not set")
        
        url = f"{SPRING_BACKEND_BASE_URL}{SPRING_DETECTION_PATH}"
        headers = {
            "X-Internal-Api-Key": BACKEND_INTERNAL_API_KEY,
            "Content-Type": "application/json",
        }

        payload = result.model_dump(
            by_alias=True,
            mode="json",
        )
        if analysis_status is not None:
            payload["status"] = analysis_status

        response = await self._post_with_retry(
            url=url,
            payload=payload,
            headers=headers,
            operation_name="detection send",
        )

        return self._parse_json_response(response)


    async def send_speed_violation(
        self,
        request: SpeedViolationCreateRequest,
    ) -> dict:
        if not BACKEND_INTERNAL_API_KEY:
            raise RuntimeError("BACKEND_INTERNAL_API_KEY is not set")

        url = f"{SPRING_BACKEND_BASE_URL}{SPRING_SPEED_VIOLATION_PATH}"
        headers = {
            "X-Internal-Api-Key": BACKEND_INTERNAL_API_KEY,
            "Content-Type": "application/json",
        }
        payload = request.model_dump(by_alias=True, mode="json")
        response = await self._post_with_retry(
            url=url,
            payload=payload,
            headers=headers,
            operation_name="speed violation send",
        )

        return self._parse_json_response(response)

    async def _post_with_retry(
        self,
        *,
        url: str,
        payload: dict,
        headers: dict[str, str],
        operation_name: str,
    ) -> httpx.Response:
        attempts = max(1, SPRING_SPEED_VIOLATION_RETRY_ATTEMPTS)

        for attempt in range(1, attempts + 1):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        url,
                        json=payload,
                        headers=headers,
                    )

                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                if not self._should_retry_status(exc.response.status_code) or attempt >= attempts:
                    raise

                await self._sleep_before_retry(
                    attempt,
                    attempts,
                    exc,
                    operation_name=operation_name,
                )
                continue
            except httpx.RequestError as exc:
                if attempt >= attempts:
                    raise

                await self._sleep_before_retry(
                    attempt,
                    attempts,
                    exc,
                    operation_name=operation_name,
                )
                continue

            return response

        raise RuntimeError(f"{operation_name} retry loop exited unexpectedly")

    def _parse_json_response(self, response: httpx.Response) -> dict:
        if not response.content:
            return {"status": "sent"}

        return response.json()

    def _should_retry_status(self, status_code: int) -> bool:
        return status_code == 429 or 500 <= status_code <= 599

    async def _sleep_before_retry(
        self,
        attempt: int,
        attempts: int,
        exc: Exception,
        *,
        operation_name: str,
    ) -> None:
        logger.warning(
            "%s failed; retrying attempt %s/%s: %s",
            operation_name,
            attempt + 1,
            attempts,
            exc,
        )
        if SPRING_SPEED_VIOLATION_RETRY_DELAY_SECONDS > 0:
            await asyncio.sleep(SPRING_SPEED_VIOLATION_RETRY_DELAY_SECONDS)

