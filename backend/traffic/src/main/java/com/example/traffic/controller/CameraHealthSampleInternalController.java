package com.example.traffic.controller;

import com.example.traffic.dto.request.predictive.CameraHealthSampleCreateRequest;
import com.example.traffic.dto.response.predictive.CameraHealthSampleSaveResponse;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.service.CameraHealthSampleIngestionService;
import com.example.traffic.service.PredictiveRuleEvaluationOrchestrationService;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/internal/v1/camera-health-samples")
public class CameraHealthSampleInternalController {

    private final CameraHealthSampleIngestionService ingestionService;
    private final PredictiveRuleEvaluationOrchestrationService ruleEvaluationOrchestrationService;
    private final String internalApiKey;

    public CameraHealthSampleInternalController(
            CameraHealthSampleIngestionService ingestionService,
            PredictiveRuleEvaluationOrchestrationService ruleEvaluationOrchestrationService,
            @Value("${app.api.internal-key}") String internalApiKey) {
        this.ingestionService = ingestionService;
        this.ruleEvaluationOrchestrationService = ruleEvaluationOrchestrationService;
        this.internalApiKey = internalApiKey;
    }

    @PostMapping
    public CameraHealthSampleSaveResponse saveCameraHealthSample(
            @RequestHeader(value = "X-Internal-Api-Key", required = false) String apiKey,
            @Valid @RequestBody CameraHealthSampleCreateRequest request) {
        if (apiKey == null) {
            throw new BusinessException("API Key is missing.", HttpStatus.UNAUTHORIZED);
        }
        if (!internalApiKey.equals(apiKey)) {
            throw new BusinessException("Invalid API Key.", HttpStatus.FORBIDDEN);
        }
        CameraHealthSampleSaveResponse response = ingestionService.save(request);
        try {
            int savedCandidates = ruleEvaluationOrchestrationService.evaluateLatestRuleSamples(
                    request.getCameraId(),
                    request.getDataSource()
            );
            log.info(
                    "predictive rule evaluation completed after sample ingestion: cameraId={} sampleId={} savedCandidates={}",
                    request.getCameraId(),
                    response.getSampleId(),
                    savedCandidates
            );
        } catch (Exception exc) {
            log.warn(
                    "predictive rule evaluation failed after sample ingestion: cameraId={} sampleId={} error={}",
                    request.getCameraId(),
                    response.getSampleId(),
                    exc.getMessage()
            );
        }
        return response;
    }
}
