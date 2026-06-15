package com.example.traffic.dto.request.predictive;

import jakarta.validation.constraints.Positive;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.Map;

@Getter
@NoArgsConstructor
public class AnomalyPolicyUpdateRequest {

    @Positive
    private Integer predictionHorizonMinutes;

    @Positive
    private Integer minimumSampleCount;

    private Map<String, Object> config;

    private Boolean enabled;
}
