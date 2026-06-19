package com.example.traffic.dto.response.predictive;

import lombok.Builder;
import lombok.Getter;

import java.math.BigDecimal;
import java.time.OffsetDateTime;

@Getter
@Builder
public class PredictiveSummaryResponse {
    private final long totalCameras;
    private final long normalCameras;
    private final long degradedCameras;
    private final long criticalCameras;
    private final long offlineCameras;
    private final long baselineLearningCameras;
    private final long openAnomalies;
    private final long predictedRisks;
    private final long overdueTickets;
    private final BigDecimal mttaMinutes;
    private final BigDecimal mttrMinutes;
    private final OffsetDateTime generatedAt;
}
