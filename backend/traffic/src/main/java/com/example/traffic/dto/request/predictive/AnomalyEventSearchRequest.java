package com.example.traffic.dto.request.predictive;

import com.example.traffic.common.enums.*;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.OffsetDateTime;

@Getter
@NoArgsConstructor
public class AnomalyEventSearchRequest {
    private Long cameraId;
    private AnomalySeverity severity;
    private AnomalyEventStatus status;
    private AnomalyType anomalyType;
    private DetectionMethod detectionMethod;
    private DataSourceType dataSource = DataSourceType.REAL;
    private OffsetDateTime from;
    private OffsetDateTime to;
    @Min(0)
    private int page = 0;
    @Min(1)
    @Max(100)
    private int size = 20;
    private String sort = "firstDetectedAt,desc";
}
