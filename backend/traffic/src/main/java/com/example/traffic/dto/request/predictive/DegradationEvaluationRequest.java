package com.example.traffic.dto.request.predictive;

import com.example.traffic.common.enums.QualityStatus;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;

@Getter
@NoArgsConstructor
public class DegradationEvaluationRequest {

    @NotNull
    private Long cameraId;

    @NotNull
    private OffsetDateTime evaluatedAt;

    @NotNull
    private List<Map<String, Object>> recentHealthSamples;

    @NotNull
    @Valid
    private Baseline baseline;

    @NotNull
    @Valid
    private TrafficContext trafficContext;

    @NotNull
    @Valid
    private Policy policy;

    @Getter
    @NoArgsConstructor
    public static class Baseline {
        @NotBlank
        private String source;
        @NotNull
        private OffsetDateTime from;
        @NotNull
        private OffsetDateTime to;
        @NotNull
        @PositiveOrZero
        private Integer sampleCount;
        @NotNull
        @Valid
        private Map<String, Metric> metrics;
    }

    @Getter
    @NoArgsConstructor
    public static class Metric {
        @NotNull
        private BigDecimal median;
        @NotNull
        @PositiveOrZero
        private BigDecimal mad;
    }

    @Getter
    @NoArgsConstructor
    public static class TrafficContext {
        @PositiveOrZero
        private Integer currentCameraVehicleCount;
        @NotNull
        private Map<String, Integer> adjacentCameraVehicleCounts;
        @NotNull
        private QualityStatus qualityStatus;
    }

    @Getter
    @NoArgsConstructor
    public static class Policy {
        @NotBlank
        private String policyCode;
        @Positive
        private Integer windowMinutes;
        @Positive
        private Integer minimumValidSamples;
        @DecimalMin("0")
        @DecimalMax("1")
        private BigDecimal ewmaAlpha;
        @DecimalMin("0")
        @DecimalMax("1")
        private BigDecimal minimumTrendConfidence;
        @Positive
        private Integer predictionHorizonMinutes;
    }
}
