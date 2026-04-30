from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


DirectionType = Literal["IN", "OUT", "BOTH"]
DetectionType = Literal["VEHICLE", "PLATE"]


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
    detected_at: datetime = Field(
        alias="detectedAt",
        examples=["2026-04-30T10:30:00"],
    )

    model_config = ConfigDict(populate_by_name=True)


class DetectionResponse(BaseModel):
    accepted: bool = Field(examples=[True])
    message: str = Field(examples=["Detection result accepted"])
    data: DetectionResult | None = None
