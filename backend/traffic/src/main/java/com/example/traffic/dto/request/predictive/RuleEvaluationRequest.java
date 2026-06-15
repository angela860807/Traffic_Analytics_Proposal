package com.example.traffic.dto.request.predictive;

import com.example.traffic.common.enums.QualityStatus;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.List;

@Getter
@NoArgsConstructor
public class RuleEvaluationRequest {

    @NotNull
    private Long cameraId;

    @NotNull
    private OffsetDateTime evaluatedAt;

    @NotEmpty
    @Valid
    private List<HealthSample> samples;

    @NotEmpty
    @Valid
    private List<Policy> policies;

    @Getter
    @NoArgsConstructor
    public static class HealthSample {
        @NotNull
        private OffsetDateTime sampledAt;
        @PositiveOrZero
        private BigDecimal fpsAvg;
        @DecimalMin("0")
        @DecimalMax("1")
        private BigDecimal frameDropRate;
        @PositiveOrZero
        private Integer latencyP95Ms;
        @DecimalMin("0")
        @DecimalMax("1")
        private BigDecimal blurScoreAvg;
        @DecimalMin("0")
        @DecimalMax("1")
        private BigDecimal ocrFailRate;
        @PositiveOrZero
        private Integer ocrAttemptCount;
        @DecimalMin("0")
        @DecimalMax("100")
        private BigDecimal cpuUsagePct;
        @DecimalMin("0")
        @DecimalMax("100")
        private BigDecimal memoryUsagePct;
        @PositiveOrZero
        private Integer networkRttMs;
        private OffsetDateTime lastFrameAt;
        @NotNull
        private QualityStatus qualityStatus;
    }

    @Getter
    @NoArgsConstructor
    public static class Policy {
        @NotBlank
        private String policyCode;
        private BigDecimal warningThreshold;
        private BigDecimal criticalThreshold;
        @Positive
        private Integer warningConsecutiveWindows;
        @Positive
        private Integer criticalConsecutiveWindows;
    }
}
