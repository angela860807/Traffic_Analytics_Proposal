package com.example.traffic.dto.response.predictive;

import com.example.traffic.common.enums.*;
import lombok.Builder;
import lombok.Getter;

import java.math.BigDecimal;
import java.time.OffsetDateTime;

@Getter
@Builder
public class AnomalyEventSummaryResponse {
    private final Long id;
    private final AnomalyTargetType targetType;
    private final Long cameraId;
    private final String cameraName;
    private final AnomalyType anomalyType;
    private final AnomalySeverity severity;
    private final AnomalyEventStatus status;
    private final DetectionMethod detectionMethod;
    private final BigDecimal anomalyScore;
    private final OffsetDateTime projectedThresholdCrossingAt;
    private final OffsetDateTime firstDetectedAt;
    private final OffsetDateTime lastDetectedAt;
    private final DataSourceType dataSource;
}
