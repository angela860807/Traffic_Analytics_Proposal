package com.example.traffic.dto.response.predictive;

import com.example.traffic.common.enums.*;
import lombok.Builder;
import lombok.Getter;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;

@Getter
@Builder
public class AnomalyEventDetailResponse {
    private final Long id;
    private final AnomalyTargetType targetType;
    private final Long cameraId;
    private final String cameraName;
    private final AnomalyType anomalyType;
    private final AnomalySeverity severity;
    private final AnomalyEventStatus status;
    private final DetectionMethod detectionMethod;
    private final Detector detector;
    private final String policyCode;
    private final Baseline baseline;
    private final Trend trend;
    private final List<SuspectedCause> suspectedCauses;
    private final List<Evidence> evidence;
    private final Ticket ticket;
    private final ShadowModel shadowModel;

    @Getter
    @Builder
    public static class Detector {
        private final String name;
        private final String version;
    }

    @Getter
    @Builder
    public static class Baseline {
        private final String source;
        private final OffsetDateTime from;
        private final OffsetDateTime to;
        private final Integer sampleCount;
    }

    @Getter
    @Builder
    public static class Trend {
        private final BigDecimal slope;
        private final BigDecimal confidence;
        private final Integer predictionHorizonMinutes;
        private final OffsetDateTime projectedThresholdCrossingAt;
    }

    @Getter
    @Builder
    public static class Evidence {
        private final String metricName;
        private final BigDecimal observedValue;
        private final BigDecimal baselineValue;
        private final BigDecimal thresholdValue;
        private final BigDecimal metricScore;
        private final String unit;
        private final OffsetDateTime sampledAt;
        private final Map<String, Object> context;
    }

    @Getter
    @Builder
    public static class Ticket {
        private final Long id;
        private final String ticketNumber;
        private final MaintenancePriority priority;
        private final MaintenanceStatus status;
    }

    @Getter
    @Builder
    public static class ShadowModel {
        private final String detectorName;
        private final String version;
        private final DetectorOperatingMode operatingMode;
        private final BigDecimal anomalyScore;
        private final BigDecimal warningThreshold;
        private final BigDecimal criticalThreshold;
        private final boolean predictedAnomaly;
        private final AnomalySeverity predictedSeverity;
        private final OffsetDateTime evaluatedAt;
        private final List<Object> topFeatures;
    }
}
