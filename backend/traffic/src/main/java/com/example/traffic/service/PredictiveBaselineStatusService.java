package com.example.traffic.service;

import com.example.traffic.common.enums.BaselineStatus;
import com.example.traffic.common.enums.HealthStatus;
import org.springframework.stereotype.Service;

@Service
public class PredictiveBaselineStatusService {

    public boolean isLearning(BaselineStatus baselineStatus) {
        return BaselineStatus.LEARNING.equals(baselineStatus);
    }

    public HealthStatus toHealthStatus(BaselineStatus baselineStatus) {
        if (isLearning(baselineStatus)) {
            return HealthStatus.BASELINE_LEARNING;
        }
        return HealthStatus.NORMAL;
    }
}
