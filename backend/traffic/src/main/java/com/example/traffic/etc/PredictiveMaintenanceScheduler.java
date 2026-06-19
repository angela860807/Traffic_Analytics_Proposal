package com.example.traffic.etc;

import com.example.traffic.common.enums.DataSourceType;
import com.example.traffic.service.PredictiveDegradationEvaluationOrchestrationService;
import com.example.traffic.service.TrafficContextAggregationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class PredictiveMaintenanceScheduler {

    private final TrafficContextAggregationService trafficContextAggregationService;
    private final PredictiveDegradationEvaluationOrchestrationService degradationEvaluationOrchestrationService;

    @Scheduled(cron = "10 */5 * * * *")
    public void aggregateTrafficContext() {
        int rows = trafficContextAggregationService.aggregatePreviousCompletedWindow(DataSourceType.REAL);
        log.info("traffic context aggregation completed: rows={}", rows);
    }

    @Scheduled(cron = "40 */5 * * * *")
    public void evaluateCameraDegradation() {
        degradationEvaluationOrchestrationService.evaluateAllActiveCameras(DataSourceType.REAL);
    }
}
