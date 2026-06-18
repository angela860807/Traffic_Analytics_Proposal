from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


DataSource = Literal["REAL", "OPEN_DATA", "SIMULATED", "FAULT_INJECTED", "MOCK"]
QualityStatus = Literal["COMPLETE", "PARTIAL", "INSUFFICIENT"]


class CameraHealthSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class CameraHealthObservation(CameraHealthSchema):
    sampled_at: AwareDatetime = Field(alias="sampledAt")
    fps_avg: float | None = Field(default=None, alias="fpsAvg", ge=0)
    frame_drop_rate: float | None = Field(
        default=None,
        alias="frameDropRate",
        ge=0,
        le=1,
    )
    latency_p95_ms: float | None = Field(
        default=None,
        alias="latencyP95Ms",
        ge=0,
    )
    blur_score_avg: float | None = Field(
        default=None,
        alias="blurScoreAvg",
        ge=0,
        le=1,
    )
    brightness_score_avg: float | None = Field(
        default=None,
        alias="brightnessScoreAvg",
        ge=0,
        le=1,
    )
    detection_count: int | None = Field(
        default=None,
        alias="detectionCount",
        ge=0,
    )
    ocr_attempt_count: int | None = Field(
        default=None,
        alias="ocrAttemptCount",
        ge=0,
    )
    ocr_failure_count: int | None = Field(
        default=None,
        alias="ocrFailureCount",
        ge=0,
    )
    ocr_fail_rate: float | None = Field(
        default=None,
        alias="ocrFailRate",
        ge=0,
        le=1,
    )
    cpu_usage_pct: float | None = Field(
        default=None,
        alias="cpuUsagePct",
        ge=0,
        le=100,
    )
    memory_usage_pct: float | None = Field(
        default=None,
        alias="memoryUsagePct",
        ge=0,
        le=100,
    )
    disk_usage_pct: float | None = Field(
        default=None,
        alias="diskUsagePct",
        ge=0,
        le=100,
    )
    network_rtt_ms: float | None = Field(
        default=None,
        alias="networkRttMs",
        ge=0,
    )
    last_frame_at: AwareDatetime | None = Field(
        default=None,
        alias="lastFrameAt",
    )
    quality_status: QualityStatus = Field(alias="qualityStatus")
    is_imputed: bool = Field(default=False, alias="isImputed")

    @model_validator(mode="after")
    def validate_ocr_counts(self) -> "CameraHealthObservation":
        if (
            self.ocr_attempt_count is not None
            and self.ocr_failure_count is not None
            and self.ocr_failure_count > self.ocr_attempt_count
        ):
            raise ValueError("ocrFailureCount cannot exceed ocrAttemptCount")

        if self.ocr_attempt_count == 0 and self.ocr_fail_rate is not None:
            raise ValueError("ocrFailRate must be null when ocrAttemptCount is 0")

        return self


class CameraHealthSampleRequest(CameraHealthObservation):
    idempotency_key: str = Field(
        alias="idempotencyKey",
        min_length=1,
        max_length=160,
    )
    camera_id: int = Field(alias="cameraId", gt=0)
    processor_code: str = Field(
        alias="processorCode",
        min_length=1,
        max_length=100,
    )
    sample_window_seconds: int = Field(
        alias="sampleWindowSeconds",
        gt=0,
        le=3600,
    )
    data_source: DataSource = Field(default="REAL", alias="dataSource")


class CameraHealthSampleResponse(CameraHealthSchema):
    sample_id: int = Field(alias="sampleId", gt=0)
    created: bool
