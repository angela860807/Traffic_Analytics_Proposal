from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SpeedMeasurementResult(BaseModel):
    track_id: int = Field(alias="trackId")
    measured_speed: float = Field(alias="measuredSpeed", ge=0)
    speed_limit: float = Field(alias="speedLimit", gt=0)
    distance_meters: float = Field(alias="distanceMeters", gt=0)
    elapsed_seconds: float = Field(alias="elapsedSeconds", gt=0)
    is_violation: bool = Field(alias="isViolation")
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
