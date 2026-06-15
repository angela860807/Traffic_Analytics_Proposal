package com.example.traffic.dto.response.predictive;

import com.example.traffic.common.enums.QualityStatus;
import lombok.Builder;
import lombok.Getter;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.List;

@Getter
@Builder
public class CameraHealthHistoryResponse {
    private final Long cameraId;
    private final List<Sample> samples;

    @Getter
    @Builder
    public static class Sample {
        private final OffsetDateTime sampledAt;
        private final BigDecimal fpsAvg;
        private final BigDecimal frameDropRate;
        private final Integer latencyP95Ms;
        private final BigDecimal blurScoreAvg;
        private final BigDecimal ocrFailRate;
        private final BigDecimal cpuUsagePct;
        private final BigDecimal memoryUsagePct;
        private final Integer networkRttMs;
        private final BigDecimal healthScore;
        private final QualityStatus qualityStatus;
    }
}
