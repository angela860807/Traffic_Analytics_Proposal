package com.example.traffic.dto.response.predictive;

import com.example.traffic.common.enums.BaselineStatus;
import com.example.traffic.common.enums.DataSourceType;
import com.example.traffic.common.enums.HealthStatus;
import lombok.Builder;
import lombok.Getter;

import java.math.BigDecimal;
import java.time.OffsetDateTime;

@Getter
@Builder
public class CameraOperatingStatusResponse {
    private final Long cameraId;
    private final String cameraName;
    private final Long zoneId;
    private final BigDecimal healthScore;
    private final HealthStatus healthStatus;
    private final BaselineStatus baselineStatus;
    private final long activeAnomalyCount;
    private final long predictedRiskCount;
    private final OffsetDateTime latestSampledAt;
    private final DataSourceType dataSource;
}
