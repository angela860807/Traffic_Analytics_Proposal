from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import logging
from pathlib import Path
import threading
from typing import Mapping
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import numpy as np
import psutil

from app.core.config import (
    CAMERA_HEALTH_WINDOW_SECONDS,
    CAMERA_PROCESSOR_CODE,
    DEFAULT_TIMEZONE,
    STREAM_FPS,
)
from app.schemas.camera_health import CameraHealthSampleRequest, QualityStatus


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SystemResourceSnapshot:
    cpu_usage_pct: float | None
    memory_usage_pct: float | None
    disk_usage_pct: float | None


class SystemResourceSampler:
    def sample(self) -> SystemResourceSnapshot:
        return SystemResourceSnapshot(
            cpu_usage_pct=round(psutil.cpu_percent(interval=None), 2),
            memory_usage_pct=round(psutil.virtual_memory().percent, 2),
            disk_usage_pct=round(
                psutil.disk_usage(str(Path.cwd())).percent,
                2,
            ),
        )


@dataclass
class _CameraHealthAccumulator:
    window_start: datetime
    frame_count: int = 0
    frame_numbers: set[int] = field(default_factory=set)
    latency_ms_values: list[float] = field(default_factory=list)
    blur_scores: list[float] = field(default_factory=list)
    brightness_scores: list[float] = field(default_factory=list)
    detection_count: int = 0
    ocr_attempt_count: int = 0
    ocr_failure_count: int = 0
    first_frame_at: datetime | None = None
    last_frame_at: datetime | None = None
    resources: SystemResourceSnapshot | None = None


@dataclass(frozen=True)
class CameraHealthWindowSnapshot:
    camera_code: str
    sampled_at: datetime
    sample_window_seconds: int
    fps_avg: float
    frame_drop_rate: float
    latency_p95_ms: float | None
    blur_score_avg: float | None
    brightness_score_avg: float | None
    detection_count: int
    ocr_attempt_count: int
    ocr_failure_count: int
    ocr_fail_rate: float | None
    cpu_usage_pct: float | None
    memory_usage_pct: float | None
    disk_usage_pct: float | None
    network_rtt_ms: float | None
    last_frame_at: datetime | None
    quality_status: QualityStatus

    def to_request(
        self,
        *,
        camera_id: int,
        processor_code: str = CAMERA_PROCESSOR_CODE,
    ) -> CameraHealthSampleRequest:
        idempotency_key = (
            f"camera-{camera_id}-"
            f"{self.sampled_at.strftime('%Y%m%dT%H%M%S%z')}"
        )
        return CameraHealthSampleRequest(
            idempotency_key=idempotency_key,
            camera_id=camera_id,
            processor_code=processor_code,
            sampled_at=self.sampled_at,
            sample_window_seconds=self.sample_window_seconds,
            fps_avg=self.fps_avg,
            frame_drop_rate=self.frame_drop_rate,
            latency_p95_ms=self.latency_p95_ms,
            blur_score_avg=self.blur_score_avg,
            brightness_score_avg=self.brightness_score_avg,
            detection_count=self.detection_count,
            ocr_attempt_count=self.ocr_attempt_count,
            ocr_failure_count=self.ocr_failure_count,
            ocr_fail_rate=self.ocr_fail_rate,
            cpu_usage_pct=self.cpu_usage_pct,
            memory_usage_pct=self.memory_usage_pct,
            disk_usage_pct=self.disk_usage_pct,
            network_rtt_ms=self.network_rtt_ms,
            last_frame_at=self.last_frame_at,
            data_source="REAL",
            quality_status=self.quality_status,
            is_imputed=False,
        )


class CameraHealthCollector:
    def __init__(
        self,
        *,
        window_seconds: int = CAMERA_HEALTH_WINDOW_SECONDS,
        expected_fps: int = STREAM_FPS,
        timezone_name: str = DEFAULT_TIMEZONE,
        resource_sampler: SystemResourceSampler | None = None,
    ) -> None:
        if window_seconds <= 0:
            raise ValueError("window_seconds must be greater than 0")
        if expected_fps <= 0:
            raise ValueError("expected_fps must be greater than 0")

        self.window_seconds = window_seconds
        self.expected_fps = expected_fps
        self.timezone = self._load_timezone(timezone_name)
        self.resource_sampler = resource_sampler or SystemResourceSampler()
        self._accumulators: dict[
            tuple[str, datetime],
            _CameraHealthAccumulator,
        ] = {}
        self._next_emit_at: dict[str, datetime] = {}
        self._lock = threading.RLock()

    def record_frame(
        self,
        *,
        camera_code: str,
        captured_at: datetime,
        processing_latency_ms: float,
        blur_variance: float,
        brightness_score: float,
        detection_count: int,
        frame_number: int | None = None,
    ) -> None:
        normalized_at = self._normalize_datetime(captured_at)
        window_start = self._floor_window(normalized_at)

        with self._lock:
            next_emit_at = self._next_emit_at.get(camera_code)
            if next_emit_at is not None and window_start < next_emit_at:
                logger.warning(
                    "late camera health frame ignored: cameraCode=%s capturedAt=%s",
                    camera_code,
                    normalized_at.isoformat(),
                )
                return

            if next_emit_at is None:
                self._next_emit_at[camera_code] = window_start

            key = (camera_code, window_start)
            accumulator = self._accumulators.get(key)
            if accumulator is None:
                accumulator = _CameraHealthAccumulator(
                    window_start=window_start,
                    resources=self.resource_sampler.sample(),
                )
                self._accumulators[key] = accumulator

            accumulator.frame_count += 1
            if frame_number is not None:
                accumulator.frame_numbers.add(frame_number)
            accumulator.latency_ms_values.append(max(0.0, processing_latency_ms))
            accumulator.blur_scores.append(
                self.normalize_blur_score(blur_variance)
            )
            accumulator.brightness_scores.append(
                min(1.0, max(0.0, brightness_score))
            )
            accumulator.detection_count += max(0, detection_count)
            if (
                accumulator.first_frame_at is None
                or normalized_at < accumulator.first_frame_at
            ):
                accumulator.first_frame_at = normalized_at
            if (
                accumulator.last_frame_at is None
                or normalized_at > accumulator.last_frame_at
            ):
                accumulator.last_frame_at = normalized_at

    def record_ocr_result(
        self,
        *,
        camera_code: str,
        captured_at: datetime,
        failed: bool,
    ) -> None:
        normalized_at = self._normalize_datetime(captured_at)
        window_start = self._floor_window(normalized_at)

        with self._lock:
            next_emit_at = self._next_emit_at.get(camera_code)
            if next_emit_at is not None and window_start < next_emit_at:
                logger.warning(
                    "late camera health OCR result ignored: "
                    "cameraCode=%s capturedAt=%s",
                    camera_code,
                    normalized_at.isoformat(),
                )
                return

            key = (camera_code, window_start)
            accumulator = self._accumulators.get(key)
            if accumulator is None:
                accumulator = _CameraHealthAccumulator(
                    window_start=window_start,
                    resources=self.resource_sampler.sample(),
                )
                self._accumulators[key] = accumulator
                self._next_emit_at.setdefault(camera_code, window_start)

            accumulator.ocr_attempt_count += 1
            if failed:
                accumulator.ocr_failure_count += 1

    def pop_ready_snapshots(
        self,
        *,
        now: datetime,
    ) -> list[CameraHealthWindowSnapshot]:
        normalized_now = self._normalize_datetime(now)
        snapshots: list[CameraHealthWindowSnapshot] = []

        with self._lock:
            for camera_code in sorted(self._next_emit_at):
                next_window = self._next_emit_at[camera_code]
                while (
                    next_window + timedelta(seconds=self.window_seconds)
                    <= normalized_now
                ):
                    accumulator = self._accumulators.pop(
                        (camera_code, next_window),
                        None,
                    )
                    snapshots.append(
                        self._build_snapshot(
                            camera_code=camera_code,
                            window_start=next_window,
                            accumulator=accumulator,
                        )
                    )
                    next_window += timedelta(seconds=self.window_seconds)

                self._next_emit_at[camera_code] = next_window

        return snapshots

    def pop_ready_requests(
        self,
        *,
        now: datetime,
        camera_ids: Mapping[str, int],
    ) -> list[CameraHealthSampleRequest]:
        with self._lock:
            missing_camera_codes = sorted(
                set(self._next_emit_at).difference(camera_ids)
            )
        if missing_camera_codes:
            raise ValueError(
                "cameraId mapping is missing for: "
                + ", ".join(missing_camera_codes)
            )

        requests: list[CameraHealthSampleRequest] = []
        for snapshot in self.pop_ready_snapshots(now=now):
            requests.append(
                snapshot.to_request(
                    camera_id=camera_ids[snapshot.camera_code],
                )
            )

        return requests

    def clear(self) -> None:
        with self._lock:
            self._accumulators.clear()
            self._next_emit_at.clear()

    @staticmethod
    def normalize_blur_score(blur_variance: float) -> float:
        return round(min(1.0, max(0.0, blur_variance) / 500.0), 6)

    def _build_snapshot(
        self,
        *,
        camera_code: str,
        window_start: datetime,
        accumulator: _CameraHealthAccumulator | None,
    ) -> CameraHealthWindowSnapshot:
        if accumulator is None or accumulator.frame_count == 0:
            resources = self.resource_sampler.sample()
            return CameraHealthWindowSnapshot(
                camera_code=camera_code,
                sampled_at=window_start,
                sample_window_seconds=self.window_seconds,
                fps_avg=0.0,
                frame_drop_rate=1.0,
                latency_p95_ms=None,
                blur_score_avg=None,
                brightness_score_avg=None,
                detection_count=0,
                ocr_attempt_count=0,
                ocr_failure_count=0,
                ocr_fail_rate=None,
                cpu_usage_pct=resources.cpu_usage_pct,
                memory_usage_pct=resources.memory_usage_pct,
                disk_usage_pct=resources.disk_usage_pct,
                network_rtt_ms=None,
                last_frame_at=None,
                quality_status="INSUFFICIENT",
            )

        resources = accumulator.resources or self.resource_sampler.sample()
        ocr_fail_rate = (
            accumulator.ocr_failure_count / accumulator.ocr_attempt_count
            if accumulator.ocr_attempt_count > 0
            else None
        )
        expected_frames = self.expected_fps * self.window_seconds
        if accumulator.frame_numbers:
            sequence_span = (
                max(accumulator.frame_numbers)
                - min(accumulator.frame_numbers)
                + 1
            )
            expected_frames = max(expected_frames, sequence_span)
            received_frames = len(accumulator.frame_numbers)
        else:
            received_frames = accumulator.frame_count

        frame_drop_rate = (
            max(0, expected_frames - received_frames) / expected_frames
            if expected_frames > 0
            else 0.0
        )
        quality_status = self._resolve_quality_status(accumulator, resources)

        return CameraHealthWindowSnapshot(
            camera_code=camera_code,
            sampled_at=window_start,
            sample_window_seconds=self.window_seconds,
            fps_avg=round(accumulator.frame_count / self.window_seconds, 4),
            frame_drop_rate=round(min(1.0, frame_drop_rate), 6),
            latency_p95_ms=round(
                float(np.percentile(accumulator.latency_ms_values, 95)),
                3,
            ),
            blur_score_avg=round(float(np.mean(accumulator.blur_scores)), 6),
            brightness_score_avg=round(
                float(np.mean(accumulator.brightness_scores)),
                6,
            ),
            detection_count=accumulator.detection_count,
            ocr_attempt_count=accumulator.ocr_attempt_count,
            ocr_failure_count=accumulator.ocr_failure_count,
            ocr_fail_rate=(
                round(ocr_fail_rate, 6)
                if ocr_fail_rate is not None
                else None
            ),
            cpu_usage_pct=resources.cpu_usage_pct,
            memory_usage_pct=resources.memory_usage_pct,
            disk_usage_pct=resources.disk_usage_pct,
            network_rtt_ms=None,
            last_frame_at=accumulator.last_frame_at,
            quality_status=quality_status,
        )

    def _resolve_quality_status(
        self,
        accumulator: _CameraHealthAccumulator,
        resources: SystemResourceSnapshot,
    ) -> QualityStatus:
        window_end = accumulator.window_start + timedelta(
            seconds=self.window_seconds
        )
        allowed_start_delay = timedelta(seconds=max(1.0, 2 / self.expected_fps))
        started_late = (
            accumulator.first_frame_at is None
            or accumulator.first_frame_at
            > accumulator.window_start + allowed_start_delay
        )
        ended_early = (
            accumulator.last_frame_at is None
            or accumulator.last_frame_at
            < window_end - allowed_start_delay
        )
        missing_resources = (
            resources.cpu_usage_pct is None
            or resources.memory_usage_pct is None
            or resources.disk_usage_pct is None
        )

        if started_late or ended_early or missing_resources:
            return "PARTIAL"
        return "COMPLETE"

    def _normalize_datetime(self, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=self.timezone)
        return value.astimezone(self.timezone)

    def _floor_window(self, value: datetime) -> datetime:
        epoch = int(value.timestamp())
        window_epoch = epoch - (epoch % self.window_seconds)
        return datetime.fromtimestamp(window_epoch, tz=self.timezone)

    @staticmethod
    def _load_timezone(timezone_name: str):
        try:
            return ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            if timezone_name == "Asia/Seoul":
                return timezone(timedelta(hours=9), name="Asia/Seoul")
            raise


camera_health_collector = CameraHealthCollector()
