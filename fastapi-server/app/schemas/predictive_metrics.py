from pydantic import BaseModel, ConfigDict, Field


class MetricSummary(BaseModel):
    count: int = Field(ge=0)
    error_count: int = Field(alias="errorCount", ge=0)
    average_duration_ms: float = Field(alias="averageDurationMs", ge=0)
    max_duration_ms: float = Field(alias="maxDurationMs", ge=0)

    model_config = ConfigDict(populate_by_name=True)


class DeliveryMetricSummary(BaseModel):
    queue_size: int = Field(alias="queueSize", ge=0)
    enqueued_count: int = Field(alias="enqueuedCount", ge=0)
    delivered_count: int = Field(alias="deliveredCount", ge=0)
    retry_count: int = Field(alias="retryCount", ge=0)
    retry_exhausted_count: int = Field(alias="retryExhaustedCount", ge=0)
    dropped_count: int = Field(alias="droppedCount", ge=0)
    last_network_rtt_ms: float | None = Field(
        default=None,
        alias="lastNetworkRttMs",
        ge=0,
    )

    model_config = ConfigDict(populate_by_name=True)


class PredictiveMetricsResponse(BaseModel):
    endpoints: dict[str, MetricSummary] = Field(default_factory=dict)
    detectors: dict[str, MetricSummary] = Field(default_factory=dict)
    delivery: DeliveryMetricSummary

    model_config = ConfigDict(populate_by_name=True)
