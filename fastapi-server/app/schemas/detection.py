from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


DirectionType = Literal["IN", "OUT", "BOTH"]
DetectionType = Literal["VEHICLE", "PLATE"]


class RaspberryFrameRequest(BaseModel):
    camera_code: str = Field(alias="cameraCode")
    captured_at: datetime = Field(alias="capturedAt")
    image_base64: str = Field(alias="imageBase64")

    model_config = ConfigDict(populate_by_name=True)


class DetectionResult(BaseModel):
    camera_code: str = Field(alias="cameraCode")
    plate_number: str = Field(alias="plateNumber")
    detection_type: DetectionType = Field(alias="detectionType")
    direction_type: DirectionType = Field(alias="directionType")
    confidence_score: float = Field(alias="confidenceScore")
    image_path: str | None = Field(default=None, alias="imagePath")
    detected_at: datetime = Field(alias="detectedAt")

    model_config = ConfigDict(populate_by_name=True)


class DetectionResponse(BaseModel):
    accepted: bool
    message: str
