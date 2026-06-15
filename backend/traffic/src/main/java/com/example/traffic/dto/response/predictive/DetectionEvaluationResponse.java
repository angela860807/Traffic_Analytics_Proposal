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
public class DetectionEvaluationResponse {
    private final Detector detector;
    private final OffsetDateTime evaluatedAt;
    private final BaselineStatus baselineStatus;
    private final Integer requiredSampleCount;
    private final Integer currentSampleCount;
    private final List<Candidate> candidates;
    private final List<ShadowCandidate> shadowCandidates;

    @Getter
    @Builder
    public static class Detector {
        private final String name;
        private final String version;
        private final DetectionMethod method;
    }

    @Getter
    @Builder
    public static class Candidate {
        private final AnomalyTargetType targetType;
        private final Long cameraId;
        private final AnomalyType anomalyType;
        private final AnomalySeverity severity;
        private final BigDecimal anomalyScore;
        private final String policyCode;
        private final Trend trend;
        private final List<SuspectedCause> suspectedCauses;
        private final List<Evidence> evidence;
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
    public static class ShadowCandidate {
        private final AnomalyTargetType targetType;
        private final Long cameraId;
        private final DetectionMethod detectionMethod;
        private final DetectorOperatingMode operatingMode;
        private final BigDecimal anomalyScore;
        private final BigDecimal warningThreshold;
        private final BigDecimal criticalThreshold;
        private final boolean predictedAnomaly;
        private final AnomalySeverity predictedSeverity;
        private final OffsetDateTime inputWindowFrom;
        private final OffsetDateTime inputWindowTo;
        private final String featureSchemaVersion;
        private final List<TopFeature> topFeatures;
    }

    @Getter
    @Builder
    public static class TopFeature {
        private final String featureName;
        private final BigDecimal featureValue;
    }
}
