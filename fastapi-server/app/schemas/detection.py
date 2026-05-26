from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.speed import SpeedMeasurementResult


DirectionType = Literal["IN", "OUT", "BOTH"]
DetectionType = Literal["VEHICLE", "PLATE", "UNKNOWN"]
ProcessingStatus = Literal[
    "NO_VEHICLE",
    "TRACKING",
    "OCR_QUEUED",
    "PLATE_NOT_DETECTED",
    "OCR_FAILED",
    "OCR_COMPLETED",
]
AnalysisStatus = Literal[
    "ANALYSIS_ONLY",
    "SENT_TO_BACKEND",
    "RECEIVED",
    "OCR_FAILED",
    "FLOW_EVENT_CREATED",
    "DUPLICATE_SKIPPED",
]
StreamStatus = Literal["IDLE", "TRACKING", "FINALIZED"]


class RaspberryFrameRequest(BaseModel):
    camera_code: str = Field(
        alias="cameraCode",
        min_length=1,
        examples=["CAM_001"],
    )
    captured_at: datetime = Field(
        alias="capturedAt",
        examples=["2026-04-30T10:30:00"],
    )
    image_base64: str = Field(
        alias="imageBase64",
        min_length=1,
        examples=["/9j/4AAQSkZJRgABAQAAAQABAAD..."],
    )

    model_config = ConfigDict(populate_by_name=True)


class DetectionResult(BaseModel):
    camera_code: str = Field(
        alias="cameraCode",
        examples=["CAM_001"],
    )
    plate_number: str | None = Field(
        default=None,
        alias="plateNumber",
        examples=["123가4567"],
    )
    detection_type: DetectionType = Field(
        alias="detectionType",
        examples=["PLATE"],
    )
    direction_type: DirectionType = Field(
        alias="directionType",
        examples=["IN"],
    )
    confidence_score: float = Field(
        alias="confidenceScore",
        ge=0,
        le=1,
        examples=[0.9321],
    )
    image_path: str | None = Field(
        default=None,
        alias="imagePath",
        examples=["storage/detections/2026/04/30/CAM_001_103000_plate_01.jpg"],
    )
    image_url: str | None = Field(
        default=None,
        alias="imageUrl",
        examples=["/static/detections/2026/04/30/CAM_001_103000_frame.jpg"],
    )
    frame_image_path: str | None = Field(
        default=None,
        alias="frameImagePath",
        examples=["storage/detections/2026/04/30/CAM_001_103000_frame.jpg"],
    )
    frame_image_url: str | None = Field(
        default=None,
        alias="frameImageUrl",
        examples=["/static/detections/2026/04/30/CAM_001_103000_frame.jpg"],
    )
    vehicle_crop_image_path: str | None = Field(
        default=None,
        alias="vehicleCropImagePath",
        examples=["storage/detections/2026/04/30/CAM_001_103000_vehicle_crop.jpg"],
    )
    vehicle_crop_image_url: str | None = Field(
        default=None,
        alias="vehicleCropImageUrl",
        examples=["/static/detections/2026/04/30/CAM_001_103000_vehicle_crop.jpg"],
    )
    plate_crop_image_path: str | None = Field(
        default=None,
        alias="plateCropImagePath",
        examples=["storage/detections/2026/04/30/CAM_001_103000_plate_crop.jpg"],
    )
    plate_crop_image_url: str | None = Field(
        default=None,
        alias="plateCropImageUrl",
        examples=["/static/detections/2026/04/30/CAM_001_103000_plate_crop.jpg"],
    )
    ocr_image_path: str | None = Field(
        default=None,
        alias="ocrImagePath",
        examples=["storage/detections/2026/04/30/CAM_001_103000_ocr.jpg"],
    )
    ocr_image_url: str | None = Field(
        default=None,
        alias="ocrImageUrl",
        examples=["/static/detections/2026/04/30/CAM_001_103000_ocr.jpg"],
    )
    detected_at: datetime = Field(
        alias="detectedAt",
        examples=["2026-04-30T10:30:00"],
    )
    processing_status: ProcessingStatus = Field(
        default="OCR_COMPLETED",
        alias="processingStatus",
        examples=["OCR_COMPLETED"],
    )

    model_config = ConfigDict(populate_by_name=True)


class DetectionResponse(BaseModel):
    accepted: bool = Field(examples=[True])
    message: str = Field(examples=["Detection result accepted"])
    analysis_status: AnalysisStatus | None = Field(
        default=None,
        alias="analysisStatus",
        examples=["OCR_FAILED"],
    )
    data: DetectionResult | None = None

    model_config = ConfigDict(populate_by_name=True)


class StreamFrameResponse(BaseModel):
    accepted: bool = Field(examples=[True])
    message: str = Field(examples=["Stream frame accepted"])
    stream_status: StreamStatus = Field(
        alias="streamStatus",
        examples=["TRACKING"],
    )
    event_id: str | None = Field(
        default=None,
        alias="eventId",
        examples=["CAM_001-20260514143012-a1b2c3d4"],
    )
    camera_code: str = Field(
        alias="cameraCode",
        examples=["CAM_001"],
    )
    frame_count: int = Field(
        default=0,
        alias="frameCount",
        ge=0,
        examples=[6],
    )
    bbox: list[int] | None = Field(
        default=None,
        examples=[[120, 180, 240, 220]],
    )
    bboxes: list[list[int]] = Field(
        default_factory=list,
        examples=[[[120, 180, 240, 220], [420, 180, 540, 220]]],
    )
    bbox_confidence_score: float = Field(
        default=0.0,
        alias="bboxConfidenceScore",
        ge=0,
        le=1,
        examples=[0.9321],
    )
    track_id: int | None = Field(
        default=None,
        alias="trackId",
        examples=[1],
    )
    best_candidate_frame_number: int | None = Field(
        default=None,
        alias="bestCandidateFrameNumber",
        examples=[156],
    )
    best_candidate_bbox: list[int] | None = Field(
        default=None,
        alias="bestCandidateBbox",
        examples=[[120, 180, 240, 220]],
    )
    best_candidate_captured_at: datetime | None = Field(
        default=None,
        alias="bestCandidateCapturedAt",
        examples=["2026-04-30T10:30:00"],
    )
    event_age_seconds: float = Field(
        default=0.0,
        alias="eventAgeSeconds",
        ge=0,
        examples=[2.4],
    )
    speed_measurements: list[SpeedMeasurementResult] = Field(
        default_factory=list,
        alias="speedMeasurements",
    )
    speed_violation: SpeedMeasurementResult | None = Field(
        default=None,
        alias="speedViolation",
    )
    speed_violation_sent: bool = Field(
        default=False,
        alias="speedViolationSent",
    )
    speed_violation_send_error: str | None = Field(
        default=None,
        alias="speedViolationSendError",
    )
    analysis_status: AnalysisStatus | None = Field(
        default=None,
        alias="analysisStatus",
        examples=["FLOW_EVENT_CREATED"],
    )
    processing_status: ProcessingStatus | None = Field(
        default=None,
        alias="processingStatus",
        examples=["OCR_QUEUED"],
    )
    data: DetectionResult | None = None

    model_config = ConfigDict(populate_by_name=True)
