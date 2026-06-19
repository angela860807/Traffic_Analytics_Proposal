package com.example.traffic.dto.response.predictive;

import com.example.traffic.common.enums.AnomalyType;
import com.example.traffic.common.enums.DetectionMethod;
import lombok.Builder;
import lombok.Getter;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.Map;

@Getter
@Builder
public class AnomalyPolicyResponse {
    private final String policyCode;
    private final AnomalyType anomalyType;
    private final DetectionMethod detectionMethod;
    private final BigDecimal warningThreshold;
    private final BigDecimal criticalThreshold;
    private final Integer warningConsecutiveWindows;
    private final Integer criticalConsecutiveWindows;
    private final Integer minimumSampleCount;
    private final Integer predictionHorizonMinutes;
    private final Map<String, Object> config;
    private final boolean enabled;
    private final OffsetDateTime updatedAt;
}
