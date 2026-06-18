import asyncio
from datetime import datetime, timedelta, timezone
import logging
from uuid import UUID

import httpx
import numpy as np

from app.schemas.camera_health import CameraHealthSampleRequest
from app.services.backend_health_client import BackendHealthClient
from app.services.camera_health_collector import (
    CameraHealthCollector,
    SystemResourceSnapshot,
)
from app.services.delivery_queue import CameraHealthDeliveryQueue
from app.services.frame_buffer import FrameBuffer
from app.services.inference_service import InferenceService
from app.services.stream_event_service import (
    STREAM_STATUS_IDLE,
    StreamEventService,
)
from app.services.vehicle_detector import VehicleDetection


KST = timezone(timedelta(hours=9))


class FixedResourceSampler:
    def sample(self) -> SystemResourceSnapshot:
        return SystemResourceSnapshot(
            cpu_usage_pct=30.0,
            memory_usage_pct=40.0,
            disk_usage_pct=50.0,
        )


class FailingHealthCollector:
    def record_frame(self, **kwargs) -> None:
        raise RuntimeError("frame health collection failed")

    def record_ocr_result(self, **kwargs) -> None:
        raise RuntimeError("OCR health collection failed")


def make_sample() -> CameraHealthSampleRequest:
    return CameraHealthSampleRequest(
        idempotencyKey="camera-1-20260614T120000+0900",
        cameraId=1,
        processorCode="edge-01",
        sampledAt="2026-06-14T12:00:00+09:00",
        sampleWindowSeconds=60,
        fpsAvg=1.0,
        frameDropRate=0.0,
        latencyP95Ms=12.0,
        blurScoreAvg=0.6,
        brightnessScoreAvg=0.5,
        detectionCount=3,
        ocrAttemptCount=0,
        ocrFailureCount=0,
        ocrFailRate=None,
        cpuUsagePct=30.0,
        memoryUsagePct=40.0,
        diskUsagePct=50.0,
        networkRttMs=None,
        lastFrameAt="2026-06-14T12:00:59+09:00",
        dataSource="REAL",
        qualityStatus="COMPLETE",
        isImputed=False,
    )


def test_collector_builds_complete_window_and_stable_idempotency_key() -> None:
    collector = CameraHealthCollector(
        window_seconds=60,
        expected_fps=1,
        timezone_name="Asia/Seoul",
        resource_sampler=FixedResourceSampler(),
    )
    window_start = datetime(2026, 6, 14, 12, 0, tzinfo=KST)

    for frame_number in range(60):
        collector.record_frame(
            camera_code="CAM_001",
            captured_at=window_start + timedelta(seconds=frame_number),
            processing_latency_ms=10 + frame_number,
            blur_variance=250,
            brightness_score=0.5,
            detection_count=1 if frame_number % 20 == 0 else 0,
            frame_number=frame_number,
        )

    snapshots = collector.pop_ready_snapshots(
        now=window_start + timedelta(seconds=60)
    )

    assert len(snapshots) == 1
    snapshot = snapshots[0]
    assert snapshot.quality_status == "COMPLETE"
    assert snapshot.fps_avg == 1.0
    assert snapshot.frame_drop_rate == 0.0
    assert snapshot.ocr_fail_rate is None

    first_request = snapshot.to_request(camera_id=1)
    second_request = snapshot.to_request(camera_id=1)
    assert first_request.idempotency_key == second_request.idempotency_key
    assert first_request.idempotency_key == "camera-1-20260614T120000+0900"


def test_collector_emits_insufficient_window_after_frames_stop() -> None:
    collector = CameraHealthCollector(
        window_seconds=60,
        expected_fps=1,
        timezone_name="Asia/Seoul",
        resource_sampler=FixedResourceSampler(),
    )
    window_start = datetime(2026, 6, 14, 12, 0, tzinfo=KST)
    collector.record_frame(
        camera_code="CAM_001",
        captured_at=window_start,
        processing_latency_ms=10,
        blur_variance=250,
        brightness_score=0.5,
        detection_count=0,
        frame_number=0,
    )

    snapshots = collector.pop_ready_snapshots(
        now=window_start + timedelta(seconds=120)
    )

    assert [item.quality_status for item in snapshots] == [
        "PARTIAL",
        "INSUFFICIENT",
    ]
    assert snapshots[1].fps_avg == 0.0
    assert snapshots[1].last_frame_at is None


def test_backend_client_retries_with_stable_headers_and_payload() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) == 1:
            return httpx.Response(500, json={"message": "temporary"})
        return httpx.Response(200, json={"sampleId": 9001, "created": True})

    client = BackendHealthClient(
        base_url="http://spring.test",
        api_key="secret",
        retry_attempts=2,
        retry_base_delay_seconds=0,
        transport=httpx.MockTransport(handler),
    )
    request_id = UUID("25e3259d-7bbf-41af-a81c-43ec67550867")

    response = asyncio.run(
        client.send_sample(make_sample(), request_id=request_id)
    )

    assert response.sample_id == 9001
    assert len(requests) == 2
    assert requests[0].headers["X-Request-Id"] == str(request_id)
    assert requests[1].headers["X-Request-Id"] == str(request_id)
    assert requests[0].content == requests[1].content
    assert client.metrics.retry_count == 1


def test_delivery_queue_counts_dropped_sample_when_full() -> None:
    client = BackendHealthClient(
        base_url="http://spring.test",
        api_key="secret",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={"sampleId": 1, "created": True},
            )
        ),
    )
    queue = CameraHealthDeliveryQueue(client=client, max_size=1)

    assert queue.enqueue(make_sample()) is True
    assert queue.enqueue(make_sample()) is False
    assert queue.metrics.enqueued_count == 1
    assert queue.metrics.dropped_count == 1


def test_frame_health_collection_failure_does_not_stop_video_analysis(
    caplog,
) -> None:
    class FakeImageDecoder:
        def decode_image_bytes(self, image_bytes):
            return np.zeros((80, 160, 3), dtype=np.uint8)

    class FakeInferenceService:
        def detect_vehicle_bbox_from_image(self, image):
            return VehicleDetection("UNKNOWN", 0.0, None)

    caplog.set_level(
        logging.ERROR,
        logger="app.services.stream_event_service",
    )
    service = StreamEventService(
        buffer=FrameBuffer(max_frames_per_camera=3),
        image_decoder=FakeImageDecoder(),
        inference_service=FakeInferenceService(),
        health_collector=FailingHealthCollector(),
    )

    result = asyncio.run(
        service.process_frame(
            camera_code="CAM_001",
            captured_at=datetime(2026, 6, 15, 12, 0, tzinfo=KST),
            content_type="image/jpeg",
            image_bytes=b"frame",
            frame_number=1,
        )
    )

    assert result.stream_status == STREAM_STATUS_IDLE
    assert "video analysis continues" in caplog.text


def test_ocr_health_collection_failure_is_isolated(caplog) -> None:
    caplog.set_level(
        logging.ERROR,
        logger="app.services.inference_service",
    )
    service = InferenceService(
        health_collector=FailingHealthCollector(),
    )

    service._record_ocr_result(
        camera_code="CAM_001",
        captured_at=datetime(2026, 6, 15, 12, 0, tzinfo=KST),
        failed=True,
    )

    assert "video analysis continues" in caplog.text
