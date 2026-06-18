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
    STREAM_BBOX_MAX_AREA_RATIO,
    STREAM_BBOX_MAX_ASPECT_RATIO,
    STREAM_BBOX_MIN_AREA_RATIO,
    STREAM_BBOX_MIN_ASPECT_RATIO,
    STREAM_BBOX_MIN_EDGE_MARGIN_RATIO,
    STREAM_BBOX_ROI_NORMALIZED,
)
from app.schemas.detection import DetectionResult
from app.schemas.speed import SpeedMeasurementResult
from app.services.bbox_tracker import BboxTracker
from app.services.camera_health_collector import CameraHealthCollector
from app.services.frame_buffer import BufferedFrame, FrameBuffer, frame_buffer
from app.services.image_decoder import ImageDecoder
from app.services.inference_service import InferenceService
from app.services.speed_tracker import SpeedTracker, VehicleTrackInput
from app.services.speed_config import SpeedCameraConfig
from app.services.vehicle_detector import VehicleDetection, VehicleDetectionBox


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
    track_id: int | None = None
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
    track_id: int | None = None
    best_candidate_frame_number: int | None = None
    best_candidate_bbox: tuple[int, int, int, int] | None = None
    best_candidate_captured_at: datetime | None = None
    event_age_seconds: float = 0.0
    speed_measurements: list[SpeedMeasurementResult] = field(default_factory=list)
    speed_violation: SpeedMeasurementResult | None = None
    speed_violation_sent: bool = False
    speed_violation_send_error: str | None = None
    processing_status: str | None = None
    result: DetectionResult | None = None
    best_candidate_frame: BufferedFrame | None = field(default=None, repr=False)


class StreamEventService:
    def __init__(
        self,
        *,
        buffer: FrameBuffer = frame_buffer,
        image_decoder: ImageDecoder | None = None,
        inference_service: InferenceService | None = None,
        speed_tracker: SpeedTracker | None = None,
        bbox_tracker: BboxTracker | None = None,
        health_collector: CameraHealthCollector | None = None,
    ) -> None:
        self.buffer = buffer
        self.image_decoder = image_decoder or ImageDecoder()
        self.inference_service = inference_service or InferenceService()
        self.speed_tracker = speed_tracker or SpeedTracker()
        self.bbox_tracker = bbox_tracker or BboxTracker()
        self.health_collector = health_collector
        self._events_by_camera: dict[str, StreamEvent] = {}
        self._stream_bbox_roi = self._parse_normalized_roi(STREAM_BBOX_ROI_NORMALIZED)

    async def process_frame(
        self,
        *,
        camera_code: str,
        captured_at: datetime,
        content_type: str,
        image_bytes: bytes,
        frame_number: int | None = None,
        high_res_crop_bytes: bytes | None = None,
        high_res_crop_content_type: str | None = None,
        high_res_crop_frame_number: int | None = None,
        speed_camera_config: SpeedCameraConfig | None = None,
        finalize_with_ocr: bool = True,
    ) -> StreamProcessingResult:
        received_monotonic = time.monotonic()
        image = self.image_decoder.decode_image_bytes(image_bytes)
        raw_detection = self.inference_service.detect_vehicle_bbox_from_image(image)
        detection = self._postprocess_vehicle_detection(raw_detection, image)
        bboxes = [box.bbox for box in detection.boxes]
        tracked_bboxes = self.bbox_tracker.update(
            camera_code=camera_code,
            captured_at=captured_at,
            boxes=detection.boxes,
        )
        event = self._events_by_camera.get(camera_code)
        primary_track = self._select_primary_track(
            tracked_bboxes=tracked_bboxes,
            event_track_id=event.track_id if event is not None else None,
        )
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
            frame_number=frame_number,
            high_res_crop_bytes=(
                high_res_crop_bytes
                if high_res_crop_frame_number is None
                or high_res_crop_frame_number == frame_number
                else None
            ),
            high_res_crop_content_type=(
                high_res_crop_content_type
                if high_res_crop_frame_number is None
                or high_res_crop_frame_number == frame_number
                else None
            ),
            image=image,
            bbox=primary_track.bbox if primary_track is not None else detection.bbox,
            bboxes=bboxes,
            track_id=primary_track.track_id if primary_track is not None else None,
            confidence_score=(
                primary_track.confidence_score
                if primary_track is not None
                else detection.confidence_score
            ),
        )
        self._record_frame_health(
            camera_code=camera_code,
            captured_at=captured_at,
            received_monotonic=received_monotonic,
            image=image,
            frame=frame,
            detection_count=len(bboxes),
            frame_number=frame_number,
        )
        self.buffer.add_frame(frame)

        has_detection_trigger = (
            frame.bbox is not None
            and frame.confidence_score >= DETECTION_CONFIDENCE_THRESHOLD
        )
        has_trigger = (
            has_detection_trigger
            if event is None
            else has_detection_trigger and frame.track_id == event.track_id
        )

        if (
            event is not None
            and high_res_crop_bytes is not None
            and high_res_crop_frame_number is not None
        ):
            self._attach_high_res_crop_to_event_frame(
                event=event,
                frame_number=high_res_crop_frame_number,
                high_res_crop_bytes=high_res_crop_bytes,
                high_res_crop_content_type=high_res_crop_content_type,
            )

        if event is None:
            if not has_detection_trigger:
                return StreamProcessingResult(
                    stream_status=STREAM_STATUS_IDLE,
                    camera_code=camera_code,
                    bbox=frame.bbox,
                    bboxes=frame.bboxes,
                    bbox_confidence_score=frame.confidence_score,
                    track_id=frame.track_id,
                    processing_status="NO_VEHICLE",
                    speed_measurements=speed_measurements,
                    speed_violation=speed_violation,
                )

            event = self._start_event(
                camera_code,
                captured_at,
                received_monotonic,
                frame.track_id,
            )

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
            result, best_candidate = await self._finalize_event(
                event,
                run_ocr=finalize_with_ocr,
            )
            del self._events_by_camera[camera_code]
            logger.info(
                "vehicle event finalized: eventId=%s cameraCode=%s trackId=%s frames=%s ageSeconds=%.2f ocrQueued=%s resultPlate=%s resultType=%s",
                event.event_id,
                camera_code,
                event.track_id,
                len(event.frames),
                event_age_seconds,
                not finalize_with_ocr and best_candidate is not None,
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
                track_id=frame.track_id,
                best_candidate_frame_number=(
                    best_candidate.frame_number if best_candidate is not None else None
                ),
                best_candidate_bbox=(
                    best_candidate.bbox if best_candidate is not None else None
                ),
                best_candidate_captured_at=(
                    best_candidate.captured_at if best_candidate is not None else None
                ),
                event_age_seconds=event_age_seconds,
                processing_status=(
                    "OCR_COMPLETED" if result is not None else "OCR_QUEUED"
                ),
                speed_measurements=self._build_event_speed_measurements(
                    event,
                    speed_measurements,
                ),
                speed_violation=event.speed_violation or speed_violation,
                result=result,
                best_candidate_frame=best_candidate,
            )

        return StreamProcessingResult(
            stream_status=STREAM_STATUS_TRACKING,
            camera_code=camera_code,
            event_id=event.event_id,
            frame_count=len(event.frames),
            bbox=frame.bbox,
            bboxes=frame.bboxes,
            bbox_confidence_score=frame.confidence_score,
            track_id=frame.track_id,
            event_age_seconds=event_age_seconds,
            processing_status="TRACKING",
            speed_measurements=self._build_event_speed_measurements(
                event,
                speed_measurements,
            ),
            speed_violation=event.speed_violation or speed_violation,
        )

    def clear(self) -> None:
        self._events_by_camera.clear()
        self.speed_tracker.clear()
        self.bbox_tracker.clear()

    def _record_frame_health(
        self,
        *,
        camera_code: str,
        captured_at: datetime,
        received_monotonic: float,
        image: np.ndarray,
        frame: BufferedFrame,
        detection_count: int,
        frame_number: int | None,
    ) -> None:
        if self.health_collector is None:
            return

        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            self.health_collector.record_frame(
                camera_code=camera_code,
                captured_at=captured_at,
                processing_latency_ms=(
                    time.monotonic() - received_monotonic
                ) * 1000,
                blur_variance=frame.blur_score,
                brightness_score=float(np.mean(gray) / 255.0),
                detection_count=detection_count,
                frame_number=frame_number,
            )
        except Exception:
            logger.exception(
                "camera health frame collection failed; "
                "video analysis continues: cameraCode=%s frameNumber=%s",
                camera_code,
                frame_number,
            )

    def _attach_high_res_crop_to_event_frame(
        self,
        *,
        event: StreamEvent,
        frame_number: int,
        high_res_crop_bytes: bytes,
        high_res_crop_content_type: str | None,
    ) -> None:
        for frame in event.frames:
            if frame.frame_number == frame_number:
                frame.high_res_crop_bytes = high_res_crop_bytes
                frame.high_res_crop_content_type = high_res_crop_content_type
                return

        logger.debug(
            "high-res crop target frame not found: eventId=%s cameraCode=%s frameNumber=%s",
            event.event_id,
            event.camera_code,
            frame_number,
        )

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

    def _select_primary_track(
        self,
        *,
        tracked_bboxes,
        event_track_id: int | None,
    ):
        if not tracked_bboxes:
            return None

        if event_track_id is not None:
            for tracked_bbox in tracked_bboxes:
                if tracked_bbox.track_id == event_track_id:
                    return tracked_bbox

        return tracked_bboxes[0]

    def _postprocess_vehicle_detection(
        self,
        detection: VehicleDetection,
        image: np.ndarray,
    ) -> VehicleDetection:
        frame_h, frame_w = image.shape[:2]
        boxes = detection.boxes
        if not boxes and detection.bbox is not None:
            boxes = [
                VehicleDetectionBox(
                    bbox=detection.bbox,
                    confidence_score=detection.confidence_score,
                    class_name="vehicle",
                )
            ]

        filtered_boxes = [
            box
            for box in boxes
            if self._is_usable_vehicle_bbox(
                bbox=box.bbox,
                frame_width=frame_w,
                frame_height=frame_h,
            )
        ]

        if not filtered_boxes:
            if boxes:
                logger.debug(
                    "all vehicle bboxes filtered: total=%s frameWidth=%s frameHeight=%s",
                    len(boxes),
                    frame_w,
                    frame_h,
                )
            return VehicleDetection(
                detection_type="UNKNOWN",
                confidence_score=0.0,
                bbox=None,
                boxes=[],
            )

        filtered_boxes = sorted(
            filtered_boxes,
            key=lambda box: box.confidence_score,
            reverse=True,
        )
        primary = filtered_boxes[0]
        return VehicleDetection(
            detection_type="VEHICLE",
            confidence_score=primary.confidence_score,
            bbox=primary.bbox,
            boxes=filtered_boxes,
        )

    def _is_usable_vehicle_bbox(
        self,
        *,
        bbox: tuple[int, int, int, int],
        frame_width: int,
        frame_height: int,
    ) -> bool:
        x1, y1, x2, y2 = bbox
        bbox_w = max(0, x2 - x1)
        bbox_h = max(0, y2 - y1)
        if bbox_w == 0 or bbox_h == 0:
            return False

        frame_area = max(frame_width * frame_height, 1)
        area_ratio = (bbox_w * bbox_h) / frame_area
        if (
            area_ratio < STREAM_BBOX_MIN_AREA_RATIO
            or area_ratio > STREAM_BBOX_MAX_AREA_RATIO
        ):
            return False

        aspect_ratio = bbox_w / max(bbox_h, 1)
        if (
            aspect_ratio < STREAM_BBOX_MIN_ASPECT_RATIO
            or aspect_ratio > STREAM_BBOX_MAX_ASPECT_RATIO
        ):
            return False

        min_edge_margin = min(x1, y1, frame_width - x2, frame_height - y2)
        min_edge_margin_ratio = min_edge_margin / max(min(frame_width, frame_height), 1)
        if min_edge_margin_ratio < STREAM_BBOX_MIN_EDGE_MARGIN_RATIO:
            return False

        if self._stream_bbox_roi is not None:
            roi_x1, roi_y1, roi_x2, roi_y2 = self._stream_bbox_roi
            center_x = x1 + (bbox_w / 2)
            center_y = y1 + (bbox_h / 2)
            norm_x = center_x / max(frame_width, 1)
            norm_y = center_y / max(frame_height, 1)
            if not (roi_x1 <= norm_x <= roi_x2 and roi_y1 <= norm_y <= roi_y2):
                return False

        return True

    def _parse_normalized_roi(
        self,
        raw_roi: str,
    ) -> tuple[float, float, float, float] | None:
        if not raw_roi:
            return None

        try:
            values = [float(value.strip()) for value in raw_roi.split(",")]
        except ValueError:
            logger.warning("STREAM_BBOX_ROI_NORMALIZED is invalid: %s", raw_roi)
            return None

        if len(values) != 4:
            logger.warning("STREAM_BBOX_ROI_NORMALIZED must have 4 values: %s", raw_roi)
            return None

        x1, y1, x2, y2 = values
        if x1 < 0 or y1 < 0 or x2 > 1 or y2 > 1 or x1 >= x2 or y1 >= y2:
            logger.warning("STREAM_BBOX_ROI_NORMALIZED is out of range: %s", raw_roi)
            return None

        return x1, y1, x2, y2

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
        track_id: int | None = None,
    ) -> StreamEvent:
        event = StreamEvent(
            event_id=f"{camera_code}-{captured_at:%Y%m%d%H%M%S}-{uuid4().hex[:8]}",
            camera_code=camera_code,
            started_at=captured_at,
            started_monotonic=received_monotonic,
            track_id=track_id,
            frames=self.buffer.get_recent_frames(camera_code),
        )
        self._events_by_camera[camera_code] = event
        logger.info(
            "vehicle event started: eventId=%s cameraCode=%s trackId=%s preBufferFrames=%s",
            event.event_id,
            camera_code,
            track_id,
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
        *,
        run_ocr: bool = True,
    ) -> tuple[DetectionResult | None, BufferedFrame | None]:
        candidates = [
            frame
            for frame in event.frames
            if frame.bbox is not None
            and (event.track_id is None or frame.track_id == event.track_id)
            and frame.confidence_score >= DETECTION_CONFIDENCE_THRESHOLD
        ]

        if not candidates:
            logger.info(
                "vehicle event has no OCR candidates: eventId=%s cameraCode=%s frames=%s",
                event.event_id,
                event.camera_code,
                len(event.frames),
            )
            return None, None

        sorted_candidates = sorted(
            candidates,
            key=lambda frame: frame.candidate_score,
            reverse=True,
        )
        best_candidate = sorted_candidates[0]

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

        if not run_ocr:
            return None, best_candidate

        best_result: DetectionResult | None = None

        detection_kwargs = {
            "camera_code": best_candidate.camera_code,
            "captured_at": best_candidate.captured_at,
            "image_bytes": best_candidate.image_bytes,
            "vehicle_detection": VehicleDetection(
                detection_type="VEHICLE",
                confidence_score=best_candidate.confidence_score,
                bbox=best_candidate.bbox,
            ),
        }
        if best_candidate.high_res_crop_bytes is not None:
            detection_kwargs["high_res_crop_bytes"] = best_candidate.high_res_crop_bytes

        best_result = await self.inference_service.detect_from_image_bytes(
            **detection_kwargs,
        )

        return best_result, best_candidate

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
        frame_number: int | None,
        high_res_crop_bytes: bytes | None,
        high_res_crop_content_type: str | None,
        image: np.ndarray,
        bbox: tuple[int, int, int, int] | None,
        bboxes: list[tuple[int, int, int, int]],
        track_id: int | None,
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
            frame_number=frame_number,
            bbox=bbox,
            bboxes=bboxes,
            track_id=track_id,
            high_res_crop_bytes=high_res_crop_bytes,
            high_res_crop_content_type=high_res_crop_content_type,
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
