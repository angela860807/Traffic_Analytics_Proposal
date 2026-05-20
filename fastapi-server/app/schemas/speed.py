from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ESTIMATED_SPEED_ACCURACY_NOTE = (
    "Estimated from virtual line distance and bbox timing; calibrate distanceMeters, "
    "line coordinates, FPS, and camera perspective before enforcement use."
)
HOMOGRAPHY_SPEED_ACCURACY_NOTE = (
    "Estimated from homography-projected line crossing points and bbox timing; "
    "verify calibration points, FPS, and field measurements before enforcement use."
)


class SpeedMeasurementResult(BaseModel):
    track_id: int = Field(alias="trackId")
    measured_speed: float = Field(alias="measuredSpeed", ge=0)
    speed_limit: float = Field(alias="speedLimit", gt=0)
    distance_meters: float = Field(alias="distanceMeters", gt=0)
    elapsed_seconds: float = Field(alias="elapsedSeconds", gt=0)
    is_violation: bool = Field(alias="isViolation")
    is_estimated: bool = Field(default=True, alias="isEstimated")
    speed_mode: Literal["LINE_CROSSING", "TRACK_DELTA"] = Field(
        default="TRACK_DELTA",
        alias="speedMode",
    )
    accuracy_level: Literal["ESTIMATED", "HOMOGRAPHY_ESTIMATED"] = Field(
        default="ESTIMATED",
        alias="accuracyLevel",
    )
    accuracy_note: str = Field(
        default=ESTIMATED_SPEED_ACCURACY_NOTE,
        alias="accuracyNote",
    )
    measured_at: datetime = Field(alias="measuredAt")

    model_config = ConfigDict(populate_by_name=True)


class SpeedViolationCreateRequest(BaseModel):
    flow_event_id: int = Field(alias="flowEventId")
    plate_number: str = Field(alias="plateNumber", min_length=1)
    camera_code: str = Field(alias="cameraCode", min_length=1)
    measured_speed: float = Field(alias="measuredSpeed", gt=0)
    speed_limit: float = Field(alias="speedLimit", gt=0)
    violation_image_path: str | None = Field(
        default=None,
        alias="violationImagePath",
    )
    violation_image_url: str | None = Field(
        default=None,
        alias="violationImageUrl",
    )
    violated_at: datetime = Field(alias="violatedAt")

    model_config = ConfigDict(populate_by_name=True)
