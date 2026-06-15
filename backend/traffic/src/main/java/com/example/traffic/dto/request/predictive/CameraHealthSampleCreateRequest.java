package com.example.traffic.dto.request.predictive;

import com.example.traffic.common.enums.DataSourceType;
import com.example.traffic.common.enums.QualityStatus;
import jakarta.validation.constraints.*;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.OffsetDateTime;

@Getter
@NoArgsConstructor
public class CameraHealthSampleCreateRequest {

    @NotBlank
    private String idempotencyKey;

    @NotNull
    private Long cameraId;

    private String processorCode;

    @NotNull
    private OffsetDateTime sampledAt;

    @NotNull
    @Positive
    private Integer sampleWindowSeconds;

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
    private BigDecimal brightnessScoreAvg;

    @PositiveOrZero
    private Integer detectionCount;

    @PositiveOrZero
    private Integer ocrAttemptCount;

    @PositiveOrZero
    private Integer ocrFailureCount;

    @DecimalMin("0")
    @DecimalMax("1")
    private BigDecimal ocrFailRate;

    @DecimalMin("0")
    @DecimalMax("100")
    private BigDecimal cpuUsagePct;

    @DecimalMin("0")
    @DecimalMax("100")
    private BigDecimal memoryUsagePct;

    @DecimalMin("0")
    @DecimalMax("100")
    private BigDecimal diskUsagePct;

    @PositiveOrZero
    private Integer networkRttMs;

    private OffsetDateTime lastFrameAt;

    @NotNull
    private DataSourceType dataSource;

    @NotNull
    private QualityStatus qualityStatus;

    private boolean isImputed;
}
