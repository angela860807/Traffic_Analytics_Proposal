package com.example.traffic.client;

import com.example.traffic.dto.request.predictive.DegradationEvaluationRequest;
import com.example.traffic.dto.request.predictive.RuleEvaluationRequest;
import com.example.traffic.dto.response.predictive.DetectionEvaluationResponse;
import com.example.traffic.dto.response.predictive.DetectorHealthResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

import java.util.Map;

@Component
@RequiredArgsConstructor
public class PredictiveDetectionClient {

    private static final String INTERNAL_API_KEY_HEADER = "X-Internal-Api-Key";
    private static final String CAMERA_HEALTH_EVALUATE_PATH = "/internal/v1/anomaly-detection/camera-health/evaluate";
    private static final String CAMERA_DEGRADATION_EVALUATE_PATH = "/internal/v1/anomaly-detection/camera-degradation/evaluate";
    private static final String DETECTOR_HEALTH_PATH = "/internal/v1/anomaly-detection/health";

    private final RestClient.Builder restClientBuilder;

    @Value("${app.fastapi.base-url}")
    private String fastApiBaseUrl;

    @Value("${app.api.internal-key}")
    private String internalApiKey;

    public DetectionEvaluationResponse evaluateCameraHealth(RuleEvaluationRequest request) {
        return restClient()
                .post()
                .uri(CAMERA_HEALTH_EVALUATE_PATH)
                .contentType(MediaType.APPLICATION_JSON)
                .header(INTERNAL_API_KEY_HEADER, internalApiKey)
                .body(request)
                .retrieve()
                .body(DetectionEvaluationResponse.class);
    }

    public DetectionEvaluationResponse evaluateCameraHealth(Map<String, Object> request) {
        return restClient()
                .post()
                .uri(CAMERA_HEALTH_EVALUATE_PATH)
                .contentType(MediaType.APPLICATION_JSON)
                .header(INTERNAL_API_KEY_HEADER, internalApiKey)
                .body(request)
                .retrieve()
                .body(DetectionEvaluationResponse.class);
    }

    public DetectionEvaluationResponse evaluateCameraDegradation(DegradationEvaluationRequest request) {
        return restClient()
                .post()
                .uri(CAMERA_DEGRADATION_EVALUATE_PATH)
                .contentType(MediaType.APPLICATION_JSON)
                .header(INTERNAL_API_KEY_HEADER, internalApiKey)
                .body(request)
                .retrieve()
                .body(DetectionEvaluationResponse.class);
    }

    public DetectionEvaluationResponse evaluateCameraDegradation(Map<String, Object> request) {
        return restClient()
                .post()
                .uri(CAMERA_DEGRADATION_EVALUATE_PATH)
                .contentType(MediaType.APPLICATION_JSON)
                .header(INTERNAL_API_KEY_HEADER, internalApiKey)
                .body(request)
                .retrieve()
                .body(DetectionEvaluationResponse.class);
    }

    public DetectorHealthResponse getDetectorHealth() {
        return restClient()
                .get()
                .uri(DETECTOR_HEALTH_PATH)
                .header(INTERNAL_API_KEY_HEADER, internalApiKey)
                .retrieve()
                .body(DetectorHealthResponse.class);
    }

    private RestClient restClient() {
        return restClientBuilder
                .baseUrl(fastApiBaseUrl)
                .requestFactory(new SimpleClientHttpRequestFactory())
                .build();
    }
}
