package com.example.traffic.dto.response.predictive;

import com.example.traffic.common.enums.DataSourceType;
import com.example.traffic.common.enums.QualityStatus;
import lombok.Builder;
import lombok.Getter;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.List;

@Getter
@Builder
public class TrafficContextHistoryResponse {
    private final Long cameraId;
    private final Long zoneId;
    private final List<Sample> samples;

    @Getter
    @Builder
    public static class Sample {
        private final OffsetDateTime sampledAt;
        private final Integer windowMinutes;
        private final Integer vehicleCount;
        private final BigDecimal avgSpeedKmh;
        private final Integer speedViolationCount;
        private final Integer ocrAttemptCount;
        private final Integer ocrSuccessCount;
        private final Integer ocrFailureCount;
        private final QualityStatus qualityStatus;
        private final DataSourceType dataSource;
    }
}
