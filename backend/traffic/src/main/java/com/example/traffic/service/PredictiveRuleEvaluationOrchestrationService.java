package com.example.traffic.service;

import com.example.traffic.client.PredictiveDetectionClient;
import com.example.traffic.common.enums.DataSourceType;
import com.example.traffic.common.enums.DetectionMethod;
import com.example.traffic.domain.AnomalyPolicy;
import com.example.traffic.domain.CameraHealthSample;
import com.example.traffic.dto.response.predictive.DetectionEvaluationResponse;
import com.example.traffic.repository.AnomalyPolicyRepository;
import com.example.traffic.repository.CameraHealthSampleRepository;
import com.example.traffic.util.PredictiveTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class PredictiveRuleEvaluationOrchestrationService {

    private final CameraHealthSampleRepository cameraHealthSampleRepository;
    private final AnomalyPolicyRepository anomalyPolicyRepository;
    private final PredictiveDetectionClient predictiveDetectionClient;
    private final PredictiveAnomalyEventIngestionService anomalyEventIngestionService;

    @Transactional(readOnly = true)
    public int evaluateLatestRuleSamples(Long cameraId, DataSourceType dataSource) {
        List<CameraHealthSample> samples = cameraHealthSampleRepository
                .findRecentEligibleSamples(
                        cameraId,
                        dataSource,
                        PageRequest.of(0, 5)
                );
        if (samples.isEmpty()) {
            return 0;
        }

        List<AnomalyPolicy> policies = anomalyPolicyRepository
                .findByDetectionMethodAndEnabledOrderByPolicyCodeAsc(
                        DetectionMethod.RULE,
                        true
                );
        if (policies.isEmpty()) {
            return 0;
        }

        CameraHealthSample latest = samples.get(0);
        Map<String, Object> request = new LinkedHashMap<>();
        request.put("cameraId", cameraId);
        request.put("evaluatedAt", PredictiveTimeUtils.toSeoulOffset(latest.getSampledAt()));
        request.put("samples", samples.stream()
                .sorted((left, right) -> left.getSampledAt().compareTo(right.getSampledAt()))
                .map(this::toSamplePayload)
                .toList());
        request.put("policies", policies.stream()
                .map(this::toPolicyPayload)
                .toList());

        DetectionEvaluationResponse response = predictiveDetectionClient.evaluateCameraHealth(request);
        if (response == null) {
            return 0;
        }
        return anomalyEventIngestionService.saveActiveCandidates(response, dataSource);
    }

    private Map<String, Object> toSamplePayload(CameraHealthSample sample) {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("sampledAt", PredictiveTimeUtils.toSeoulOffset(sample.getSampledAt()));
        payload.put("fpsAvg", sample.getFpsAvg());
        payload.put("frameDropRate", sample.getFrameDropRate());
        payload.put("latencyP95Ms", sample.getLatencyP95Ms());
        payload.put("blurScoreAvg", sample.getBlurScoreAvg());
        payload.put("brightnessScoreAvg", sample.getBrightnessScoreAvg());
        payload.put("detectionCount", sample.getDetectionCount());
        payload.put("ocrAttemptCount", sample.getOcrAttemptCount());
        payload.put("ocrFailureCount", sample.getOcrFailureCount());
        payload.put("ocrFailRate", sample.getOcrFailRate());
        payload.put("cpuUsagePct", sample.getCpuUsagePct());
        payload.put("memoryUsagePct", sample.getMemoryUsagePct());
        payload.put("diskUsagePct", sample.getDiskUsagePct());
        payload.put("networkRttMs", sample.getNetworkRttMs());
        payload.put("lastFrameAt", PredictiveTimeUtils.toSeoulOffset(sample.getLastFrameAt()));
        payload.put("qualityStatus", sample.getQualityStatus().name());
        payload.put("isImputed", sample.isImputed());
        return payload;
    }

    private Map<String, Object> toPolicyPayload(AnomalyPolicy policy) {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("policyCode", policy.getPolicyCode());
        payload.put("warningThreshold", policy.getWarningThreshold());
        payload.put("criticalThreshold", policy.getCriticalThreshold());
        payload.put("warningConsecutiveWindows", policy.getWarningConsecutiveWindows());
        payload.put("criticalConsecutiveWindows", policy.getCriticalConsecutiveWindows());
        return payload;
    }
}
