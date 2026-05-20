from dataclasses import dataclass, field
from datetime import datetime
import logging
from pathlib import Path
import time
from uuid import uuid4

import cv2
import numpy as np

from app.core.config import (
    DETECTION_CONFIDENCE_THRESHOLD,
    IMAGE_STORAGE_DIR,
    MAX_EVENT_SECONDS,
    POST_MISS_FRAMES,
    SAVE_EVENT_DEBUG,
    TOP_N_OCR_FRAMES,
)
from app.schemas.detection import DetectionResult
from app.schemas.speed import SpeedMeasurementResult
from app.services.frame_buffer import BufferedFrame, FrameBuffer, frame_buffer
from app.services.image_decoder import ImageDecoder
from app.services.inference_service import InferenceService
from app.services.speed_tracker import SpeedTracker, VehicleTrackInput
from app.services.speed_config import SpeedCameraConfig
from app.services.vehicle_detector import VehicleDetection


STREAM_STATUS_IDLE = "IDLE"
STREAM_STATUS_TRACKING = "TRACKING"
STREAM_STATUS_FINALIZED = "FINALIZED"
DEBUG_EVENT_FRAME_LIMIT = 5

logger = logging.getLogger(__name__)


@dataclass
class StreamEvent:
    event_id: str
    camera_code: str
    started_at: datetime
    started_monotonic: float
    frames: list[BufferedFrame] = field(default_factory=list)
    miss_count: int = 0
    speed_measurement: SpeedMeasurementResult | None = None
    speed_violation: SpeedMeasurementResult | None = None


@dataclass
class StreamProcessingResult:
    stream_status: str
    camera_code: str
    event_id: str | None = None
    frame_count: int = 0
    bbox: tuple[int, int, int, int] | None = None
    bboxes: list[tuple[int, int, int, int]] | None = None
    bbox_confidence_score: float = 0.0
    event_age_seconds: float = 0.0
    speed_measurements: list[SpeedMeasurementResult] = field(default_factory=list)
    speed_violation: SpeedMeasurementResult | None = None
    speed_violation_sent: bool = False
    speed_violation_send_error: str | None = None
    result: DetectionResult | None = None


class StreamEventService:
    def __init__(
        self,
        *,
        buffer: FrameBuffer = frame_buffer,
        image_decoder: ImageDecoder | None = None,
        inference_service: InferenceService | None = None,
        speed_tracker: SpeedTracker | None = None,
    ) -> None:
        self.buffer = buffer
        self.image_decoder = image_decoder or ImageDecoder()
        self.inference_service = inference_service or InferenceService()
        self.speed_tracker = speed_tracker or SpeedTracker()
        self._events_by_camera: dict[str, StreamEvent] = {}

    async def process_frame(
        self,
        *,
        camera_code: str,
        captured_at: datetime,
        content_type: str,
        image_bytes: bytes,
        speed_camera_config: SpeedCameraConfig | None = None,
    ) -> StreamProcessingResult:
        received_monotonic = time.monotonic()
        image = self.image_decoder.decode_image_bytes(image_bytes)
        detection = self.inference_service.detect_vehicle_bbox_from_image(image)
        bboxes = [box.bbox for box in detection.boxes]
        track_inputs = self._build_track_inputs(detection)
        speed_measurements = self.speed_tracker.process_detections(
            camera_code=camera_code,
            captured_at=captured_at,
            detections=track_inputs,
            camera_config=speed_camera_config,
        )
        speed_violation = next(
            (
                measurement
                for measurement in speed_measurements
                if measurement.is_violation
            ),
            None,
        )

        frame = self._build_buffered_frame(
            camera_code=camera_code,
            captured_at=captured_at,
            content_type=content_type,
            image_bytes=image_bytes,
            image=image,
            bbox=detection.bbox,
            bboxes=bboxes,
            confidence_score=detection.confidence_score,
        )
        self.buffer.add_frame(frame)

        has_trigger = (
            frame.bbox is not None
            and frame.confidence_score >= DETECTION_CONFIDENCE_THRESHOLD
        )
        event = self._events_by_camera.get(camera_code)

        if event is None:
            if not has_trigger:
                return StreamProcessingResult(
                    stream_status=STREAM_STATUS_IDLE,
                    camera_code=camera_code,
                    bbox=frame.bbox,
                    bboxes=frame.bboxes,
                    bbox_confidence_score=frame.confidence_score,
                    speed_measurements=speed_measurements,
                    speed_violation=speed_violation,
                )

            event = self._start_event(camera_code, captured_at, received_monotonic)

        if has_trigger:
            event.miss_count = 0
        else:
            event.miss_count += 1

        if speed_measurements:
            event.speed_measurement = speed_measurements[0]

        if speed_violation is not None:
            event.speed_violation = speed_violation

        if event.frames and event.frames[-1] is not frame:
            event.frames.append(frame)

        event_age_seconds = self._calculate_event_age_seconds(event, received_monotonic)

        if self._should_finalize_event(event, event_age_seconds):
            result = await self._finalize_event(event)
            del self._events_by_camera[camera_code]
            logger.info(
                "vehicle event finalized: eventId=%s cameraCode=%s frames=%s ageSeconds=%.2f resultPlate=%s resultType=%s",
                event.event_id,
                camera_code,
                len(event.frames),
                event_age_seconds,
                result.plate_number if result else None,
                result.detection_type if result else None,
            )
            return StreamProcessingResult(
                stream_status=STREAM_STATUS_FINALIZED,
                camera_code=camera_code,
                event_id=event.event_id,
                frame_count=len(event.frames),
                bbox=frame.bbox,
                bboxes=frame.bboxes,
                bbox_confidence_score=frame.confidence_score,
                event_age_seconds=event_age_seconds,
                speed_measurements=self._build_event_speed_measurements(
                    event,
                    speed_measurements,
                ),
                speed_violation=event.speed_violation or speed_violation,
                result=result,
            )

        return StreamProcessingResult(
            stream_status=STREAM_STATUS_TRACKING,
            camera_code=camera_code,
            event_id=event.event_id,
            frame_count=len(event.frames),
            bbox=frame.bbox,
            bboxes=frame.bboxes,
            bbox_confidence_score=frame.confidence_score,
            event_age_seconds=event_age_seconds,
            speed_measurements=self._build_event_speed_measurements(
                event,
                speed_measurements,
            ),
            speed_violation=event.speed_violation or speed_violation,
        )

    def clear(self) -> None:
        self._events_by_camera.clear()
        self.speed_tracker.clear()

    def _build_event_speed_measurements(
        self,
        event: StreamEvent,
        current_measurements: list[SpeedMeasurementResult],
    ) -> list[SpeedMeasurementResult]:
        if current_measurements:
            return current_measurements
        if event.speed_measurement is not None:
            return [event.speed_measurement]
        return []

    def _build_track_inputs(
        self,
        detection,
    ) -> list[VehicleTrackInput]:
        if detection.boxes:
            return [
                VehicleTrackInput(
                    bbox=box.bbox,
                    confidence_score=box.confidence_score,
                )
                for box in detection.boxes
            ]

        if detection.bbox is None:
            return []

        return [
            VehicleTrackInput(
                bbox=detection.bbox,
                confidence_score=detection.confidence_score,
            )
        ]

    def _start_event(
        self,
        camera_code: str,
        captured_at: datetime,
        received_monotonic: float,
    ) -> StreamEvent:
        event = StreamEvent(
            event_id=f"{camera_code}-{captured_at:%Y%m%d%H%M%S}-{uuid4().hex[:8]}",
            camera_code=camera_code,
            started_at=captured_at,
            started_monotonic=received_monotonic,
            frames=self.buffer.get_recent_frames(camera_code),
        )
        self._events_by_camera[camera_code] = event
        logger.info(
            "vehicle event started: eventId=%s cameraCode=%s preBufferFrames=%s",
            event.event_id,
            camera_code,
            len(event.frames),
        )
        return event

    def _calculate_event_age_seconds(
        self,
        event: StreamEvent,
        received_monotonic: float,
    ) -> float:
        return max(0.0, received_monotonic - event.started_monotonic)

    def _should_finalize_event(
        self,
        event: StreamEvent,
        event_age_seconds: float,
    ) -> bool:
        return (
            event.miss_count >= POST_MISS_FRAMES
            or event_age_seconds >= MAX_EVENT_SECONDS
        )

    async def _finalize_event(
        self,
        event: StreamEvent,
    ) -> DetectionResult | None:
        candidates = [
            frame
            for frame in event.frames
            if frame.bbox is not None
            and frame.confidence_score >= DETECTION_CONFIDENCE_THRESHOLD
        ]

        if not candidates:
            logger.info(
                "vehicle event has no OCR candidates: eventId=%s cameraCode=%s frames=%s",
                event.event_id,
                event.camera_code,
                len(event.frames),
            )
            return None

        sorted_candidates = sorted(
            candidates,
            key=lambda frame: frame.candidate_score,
            reverse=True,
        )
        top_candidates = sorted_candidates[: max(1, TOP_N_OCR_FRAMES)]
        best_candidate = top_candidates[0]

        logger.info(
            "vehicle event OCR candidates selected: eventId=%s cameraCode=%s candidates=%s bestScore=%.4f bestConfidence=%.4f bestBlur=%.2f",
            event.event_id,
            event.camera_code,
            len(candidates),
            best_candidate.candidate_score,
            best_candidate.confidence_score,
            best_candidate.blur_score,
        )

        if SAVE_EVENT_DEBUG:
            self._save_debug_frames(
                event=event,
                frames=sorted_candidates[:DEBUG_EVENT_FRAME_LIMIT],
            )

        best_result: DetectionResult | None = None

        for candidate in top_candidates:
            result = await self.inference_service.detect_from_image_bytes(
                camera_code=candidate.camera_code,
                captured_at=candidate.captured_at,
                image_bytes=candidate.image_bytes,
                vehicle_detection=VehicleDetection(
                    detection_type="VEHICLE",
                    confidence_score=candidate.confidence_score,
                    bbox=candidate.bbox,
                ),
            )

            if best_result is None:
                best_result = result

            if result.detection_type == "PLATE" and result.plate_number:
                return result

        return best_result

    def _save_debug_frames(
        self,
        *,
        event: StreamEvent,
        frames: list[BufferedFrame],
    ) -> None:
        date_dir = event.started_at.strftime("%Y/%m/%d")
        debug_dir = Path(IMAGE_STORAGE_DIR) / "debug" / date_dir / event.event_id
        debug_dir.mkdir(parents=True, exist_ok=True)

        for index, frame in enumerate(frames, start=1):
            image_array = np.frombuffer(frame.image_bytes, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            if image is None:
                logger.warning(
                    "failed to decode debug frame: eventId=%s cameraCode=%s index=%s",
                    event.event_id,
                    event.camera_code,
                    index,
                )
                continue

            score_text = f"{frame.candidate_score:.4f}".replace(".", "_")
            file_path = debug_dir / f"{index:02d}_score_{score_text}.jpg"

            if not cv2.imwrite(str(file_path), image):
                logger.warning(
                    "failed to save debug frame: eventId=%s path=%s",
                    event.event_id,
                    file_path,
                )

    def _build_buffered_frame(
        self,
        *,
        camera_code: str,
        captured_at: datetime,
        content_type: str,
        image_bytes: bytes,
        image: np.ndarray,
        bbox: tuple[int, int, int, int] | None,
        bboxes: list[tuple[int, int, int, int]],
        confidence_score: float,
    ) -> BufferedFrame:
        frame_h, frame_w = image.shape[:2]
        blur_score = self._calculate_blur_score(image)
        candidate_score = 0.0

        if bbox is not None:
            candidate_score = self._score_candidate(
                bbox=bbox,
                confidence_score=confidence_score,
                blur_score=blur_score,
                frame_width=frame_w,
                frame_height=frame_h,
            )

        return BufferedFrame(
            camera_code=camera_code,
            captured_at=captured_at,
            content_type=content_type,
            image_bytes=image_bytes,
            bbox=bbox,
            bboxes=bboxes,
            confidence_score=confidence_score,
            candidate_score=candidate_score,
            blur_score=blur_score,
            frame_width=frame_w,
            frame_height=frame_h,
        )

    def _score_candidate(
        self,
        *,
        bbox: tuple[int, int, int, int],
        confidence_score: float,
        blur_score: float,
        frame_width: int,
        frame_height: int,
    ) -> float:
        x1, y1, x2, y2 = bbox
        bbox_w = max(0, x2 - x1)
        bbox_h = max(0, y2 - y1)

        if bbox_w == 0 or bbox_h == 0:
            return 0.0

        center_x = x1 + (bbox_w / 2)
        center_y = y1 + (bbox_h / 2)
        norm_dx = (center_x - (frame_width / 2)) / max(frame_width / 2, 1)
        norm_dy = (center_y - (frame_height / 2)) / max(frame_height / 2, 1)
        centrality_score = 1.0 - min(
            1.0,
            float(np.sqrt((norm_dx**2 + norm_dy**2) / 2)),
        )

        area_ratio = (bbox_w * bbox_h) / max(frame_width * frame_height, 1)
        size_score = min(1.0, area_ratio / 0.05)

        edge_margin = min(x1, y1, frame_width - x2, frame_height - y2)
        edge_limit = max(min(frame_width, frame_height) * 0.03, 1)
        edge_score = min(1.0, max(0.0, edge_margin) / edge_limit)

        blur_norm = min(1.0, blur_score / 500.0)

        return (
            (confidence_score * 0.35)
            + (centrality_score * 0.25)
            + (size_score * 0.20)
            + (blur_norm * 0.15)
            + (edge_score * 0.05)
        )

    def _calculate_blur_score(self, image: np.ndarray) -> float:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())
