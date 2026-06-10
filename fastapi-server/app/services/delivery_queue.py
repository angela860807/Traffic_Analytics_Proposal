import asyncio
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime, timezone
import logging

import httpx

from app.core.config import (
    CAMERA_HEALTH_DELIVERY_ENABLED,
    CAMERA_HEALTH_DELIVERY_POLL_SECONDS,
    CAMERA_HEALTH_DELIVERY_QUEUE_MAX_SIZE,
    CAMERA_HEALTH_SHUTDOWN_TIMEOUT_SECONDS,
    CAMERA_ID_MAP,
)
from app.schemas.camera_health import CameraHealthSampleRequest
from app.services.backend_health_client import BackendHealthClient
from app.services.camera_health_collector import (
    CameraHealthCollector,
    camera_health_collector,
)


logger = logging.getLogger(__name__)


@dataclass
class DeliveryMetrics:
    enqueued_count: int = 0
    delivered_count: int = 0
    retry_exhausted_count: int = 0
    dropped_count: int = 0


class CameraHealthDeliveryQueue:
    def __init__(
        self,
        *,
        client: BackendHealthClient,
        max_size: int = CAMERA_HEALTH_DELIVERY_QUEUE_MAX_SIZE,
        shutdown_timeout_seconds: float = CAMERA_HEALTH_SHUTDOWN_TIMEOUT_SECONDS,
    ) -> None:
        if max_size <= 0:
            raise ValueError("max_size must be greater than 0")
        if shutdown_timeout_seconds < 0:
            raise ValueError("shutdown_timeout_seconds cannot be negative")

        self.client = client
        self.queue: asyncio.Queue[CameraHealthSampleRequest] = asyncio.Queue(
            maxsize=max_size
        )
        self.shutdown_timeout_seconds = shutdown_timeout_seconds
        self.metrics = DeliveryMetrics()
        self._worker_task: asyncio.Task | None = None

    def enqueue(self, request: CameraHealthSampleRequest) -> bool:
        try:
            self.queue.put_nowait(request)
        except asyncio.QueueFull:
            self.metrics.dropped_count += 1
            logger.error(
                "camera health delivery queue is full; sample dropped: "
                "cameraId=%s sampledAt=%s idempotencyKey=%s",
                request.camera_id,
                request.sampled_at.isoformat(),
                request.idempotency_key,
            )
            return False

        self.metrics.enqueued_count += 1
        return True

    async def start(self) -> None:
        if self._worker_task is not None and not self._worker_task.done():
            return
        self._worker_task = asyncio.create_task(
            self._run(),
            name="camera-health-delivery-worker",
        )

    async def stop(self) -> None:
        if self._worker_task is None:
            return

        if self.shutdown_timeout_seconds > 0:
            try:
                await asyncio.wait_for(
                    self.queue.join(),
                    timeout=self.shutdown_timeout_seconds,
                )
            except TimeoutError:
                logger.warning(
                    "camera health queue shutdown timed out: pending=%s",
                    self.queue.qsize(),
                )

        self._worker_task.cancel()
        with suppress(asyncio.CancelledError):
            await self._worker_task
        self._worker_task = None

    async def _run(self) -> None:
        while True:
            request = await self.queue.get()
            try:
                response = await self.client.send_sample(request)
                self.metrics.delivered_count += 1
                logger.info(
                    "camera health sample delivered: "
                    "cameraId=%s sampledAt=%s sampleId=%s created=%s",
                    request.camera_id,
                    request.sampled_at.isoformat(),
                    response.sample_id,
                    response.created,
                )
            except (
                httpx.HTTPError,
                RuntimeError,
                ValueError,
            ) as exc:
                self.metrics.retry_exhausted_count += 1
                logger.exception(
                    "camera health sample delivery failed after retries: "
                    "cameraId=%s sampledAt=%s idempotencyKey=%s error=%s",
                    request.camera_id,
                    request.sampled_at.isoformat(),
                    request.idempotency_key,
                    exc,
                )
            finally:
                self.queue.task_done()


class CameraHealthDeliveryService:
    def __init__(
        self,
        *,
        collector: CameraHealthCollector,
        delivery_queue: CameraHealthDeliveryQueue,
        camera_ids: dict[str, int],
        enabled: bool = CAMERA_HEALTH_DELIVERY_ENABLED,
        poll_seconds: float = CAMERA_HEALTH_DELIVERY_POLL_SECONDS,
    ) -> None:
        if poll_seconds <= 0:
            raise ValueError("poll_seconds must be greater than 0")

        self.collector = collector
        self.delivery_queue = delivery_queue
        self.camera_ids = camera_ids
        self.enabled = enabled
        self.poll_seconds = poll_seconds
        self._collector_task: asyncio.Task | None = None

    async def start(self) -> None:
        if not self.enabled:
            logger.info("camera health delivery is disabled")
            return
        if not self.camera_ids:
            raise RuntimeError(
                "CAMERA_ID_MAP_JSON is required when camera health delivery is enabled"
            )
        if self._collector_task is not None and not self._collector_task.done():
            return

        await self.delivery_queue.start()
        self._collector_task = asyncio.create_task(
            self._collect_ready_samples(),
            name="camera-health-collector-worker",
        )

    async def stop(self) -> None:
        if not self.enabled:
            return

        if self._collector_task is not None:
            self._collector_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._collector_task
            self._collector_task = None

        await self.delivery_queue.stop()

    async def _collect_ready_samples(self) -> None:
        while True:
            try:
                requests = self.collector.pop_ready_requests(
                    now=datetime.now(timezone.utc),
                    camera_ids=self.camera_ids,
                )
                for request in requests:
                    if (
                        self.delivery_queue.client.metrics.last_network_rtt_ms
                        is not None
                    ):
                        request = request.model_copy(
                            update={
                                "network_rtt_ms": (
                                    self.delivery_queue.client.metrics
                                    .last_network_rtt_ms
                                )
                            }
                        )
                    self.delivery_queue.enqueue(request)
            except ValueError:
                logger.exception("camera health sample collection failed")

            await asyncio.sleep(self.poll_seconds)


backend_health_client = BackendHealthClient()
camera_health_delivery_queue = CameraHealthDeliveryQueue(
    client=backend_health_client
)
camera_health_delivery_service = CameraHealthDeliveryService(
    collector=camera_health_collector,
    delivery_queue=camera_health_delivery_queue,
    camera_ids=CAMERA_ID_MAP,
)
