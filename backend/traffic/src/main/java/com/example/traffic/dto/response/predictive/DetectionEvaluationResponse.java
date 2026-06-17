package com.example.traffic.dto.response.predictive;

import com.example.traffic.common.enums.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DetectionEvaluationResponse {
    private Detector detector;
    private OffsetDateTime evaluatedAt;
    private BaselineStatus baselineStatus;
    private Integer requiredSampleCount;
    private Integer currentSampleCount;
    private List<Candidate> candidates;
    private List<ShadowCandidate> shadowCandidates;

    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Detector {
        private String name;
        private String version;
        private DetectionMethod method;
    }

    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Candidate {
        private AnomalyTargetType targetType;
        private Long cameraId;
        private AnomalyType anomalyType;
        private AnomalySeverity severity;
        private BigDecimal anomalyScore;
        private String policyCode;
        private Trend trend;
        private List<SuspectedCause> suspectedCauses;
        private List<Evidence> evidence;
    }

    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Trend {
        private BigDecimal slope;
        private BigDecimal confidence;
        private Integer predictionHorizonMinutes;
        private OffsetDateTime projectedThresholdCrossingAt;
    }

    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Evidence {
        private String metricName;
        private BigDecimal observedValue;
        private BigDecimal baselineValue;
        private BigDecimal thresholdValue;
        private BigDecimal metricScore;
        private String unit;
        private OffsetDateTime sampledAt;
        private Map<String, Object> context;
    }

    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ShadowCandidate {
        private AnomalyTargetType targetType;
        private Long cameraId;
        private DetectionMethod detectionMethod;
        private DetectorOperatingMode operatingMode;
        private BigDecimal anomalyScore;
        private BigDecimal warningThreshold;
        private BigDecimal criticalThreshold;
        private boolean predictedAnomaly;
        private AnomalySeverity predictedSeverity;
        private OffsetDateTime inputWindowFrom;
        private OffsetDateTime inputWindowTo;
        private String featureSchemaVersion;
        private List<TopFeature> topFeatures;
    }

    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TopFeature {
        private String featureName;
        private BigDecimal featureValue;
    }
}
