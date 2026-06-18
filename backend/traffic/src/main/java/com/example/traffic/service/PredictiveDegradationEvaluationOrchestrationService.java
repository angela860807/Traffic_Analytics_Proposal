package com.example.traffic.service;

import com.example.traffic.client.PredictiveDetectionClient;
import com.example.traffic.common.enums.DataSourceType;
import com.example.traffic.domain.AnomalyPolicy;
import com.example.traffic.domain.Camera;
import com.example.traffic.dto.response.predictive.DetectionEvaluationResponse;
import com.example.traffic.repository.AnomalyPolicyRepository;
import com.example.traffic.repository.CameraRepository;
import com.example.traffic.util.PredictiveTimeUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
public class PredictiveDegradationEvaluationOrchestrationService {

    private static final List<String> METRICS = List.of(
            "fps_avg",
            "frame_drop_rate",
            "latency_p95_ms",
            "blur_score_avg",
            "ocr_fail_rate",
            "cpu_usage_pct",
            "memory_usage_pct",
            "network_rtt_ms"
    );

    private final CameraRepository cameraRepository;
    private final AnomalyPolicyRepository anomalyPolicyRepository;
    private final NamedParameterJdbcTemplate jdbcTemplate;
    private final PredictiveDetectionClient predictiveDetectionClient;
    private final PredictiveAnomalyEventIngestionService anomalyEventIngestionService;
    private final PredictiveShadowPredictionService shadowPredictionService;

    public void evaluateAllActiveCameras(DataSourceType dataSource) {
        for (Camera camera : cameraRepository.findByIsActiveTrueOrderByCameraIdAsc()) {
            try {
                int saved = evaluateCamera(camera.getCameraId(), dataSource, LocalDateTime.now(PredictiveTimeUtils.SERVICE_ZONE));
                log.info("predictive degradation evaluation completed: cameraId={} savedRecords={}", camera.getCameraId(), saved);
            } catch (Exception exc) {
                log.warn("predictive degradation evaluation failed: cameraId={} error={}", camera.getCameraId(), exc.getMessage());
            }
        }
    }

    public int evaluateCamera(Long cameraId, DataSourceType dataSource, LocalDateTime evaluatedAt) {
        List<Map<String, Object>> recentSamples = findRecentHealthSamples(cameraId, dataSource, evaluatedAt.minusMinutes(60), evaluatedAt);
        if (recentSamples.isEmpty()) {
            return 0;
        }

        Optional<AnomalyPolicy> trendPolicy = anomalyPolicyRepository.findByPolicyCode("CAMERA_TREND_PROJECTION_V1");
        if (trendPolicy.isEmpty()) {
            return 0;
        }

        Map<String, Object> request = new LinkedHashMap<>();
        request.put("cameraId", cameraId);
        request.put("evaluatedAt", PredictiveTimeUtils.toSeoulOffset(evaluatedAt));
        request.put("recentHealthSamples", recentSamples);
        request.put("baseline", buildBaseline(cameraId, dataSource, evaluatedAt));
        request.put("trafficContext", buildTrafficContext(cameraId, dataSource, evaluatedAt));
        request.put("policy", buildPolicy(trendPolicy.get()));

        DetectionEvaluationResponse response = predictiveDetectionClient.evaluateCameraDegradation(request);
        if (response == null) {
            return 0;
        }
        int activeSaved = anomalyEventIngestionService.saveActiveCandidates(response, dataSource);
        int shadowSaved = shadowPredictionService.saveShadowCandidates(response, dataSource);
        return activeSaved + shadowSaved;
    }

    private List<Map<String, Object>> findRecentHealthSamples(
            Long cameraId,
            DataSourceType dataSource,
            LocalDateTime from,
            LocalDateTime to
    ) {
        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("cameraId", cameraId)
                .addValue("dataSource", dataSource.name())
                .addValue("from", from)
                .addValue("to", to);

        return jdbcTemplate.query("""
                SELECT
                    sampled_at,
                    fps_avg,
                    frame_drop_rate,
                    latency_p95_ms,
                    blur_score_avg,
                    brightness_score_avg,
                    detection_count,
                    ocr_attempt_count,
                    ocr_failure_count,
                    ocr_fail_rate,
                    cpu_usage_pct,
                    memory_usage_pct,
                    disk_usage_pct,
                    network_rtt_ms,
                    last_frame_at,
                    quality_status,
                    is_imputed
                FROM camera_health_samples
                WHERE camera_id = :cameraId
                  AND data_source = :dataSource
                  AND is_late_sample = FALSE
                  AND sampled_at >= :from
                  AND sampled_at <= :to
                ORDER BY sampled_at ASC
                """, params, (rs, rowNum) -> {
            Map<String, Object> sample = new LinkedHashMap<>();
            sample.put("sampledAt", PredictiveTimeUtils.toSeoulOffset(rs.getTimestamp("sampled_at").toLocalDateTime()));
            sample.put("fpsAvg", rs.getBigDecimal("fps_avg"));
            sample.put("frameDropRate", rs.getBigDecimal("frame_drop_rate"));
            sample.put("latencyP95Ms", rs.getObject("latency_p95_ms"));
            sample.put("blurScoreAvg", rs.getBigDecimal("blur_score_avg"));
            sample.put("brightnessScoreAvg", rs.getBigDecimal("brightness_score_avg"));
            sample.put("detectionCount", rs.getObject("detection_count"));
            sample.put("ocrAttemptCount", rs.getObject("ocr_attempt_count"));
            sample.put("ocrFailureCount", rs.getObject("ocr_failure_count"));
            sample.put("ocrFailRate", rs.getBigDecimal("ocr_fail_rate"));
            sample.put("cpuUsagePct", rs.getBigDecimal("cpu_usage_pct"));
            sample.put("memoryUsagePct", rs.getBigDecimal("memory_usage_pct"));
            sample.put("diskUsagePct", rs.getBigDecimal("disk_usage_pct"));
            sample.put("networkRttMs", rs.getObject("network_rtt_ms"));
            sample.put("lastFrameAt", rs.getTimestamp("last_frame_at") == null
                    ? null
                    : PredictiveTimeUtils.toSeoulOffset(rs.getTimestamp("last_frame_at").toLocalDateTime()));
            sample.put("qualityStatus", rs.getString("quality_status"));
            sample.put("isImputed", rs.getBoolean("is_imputed"));
            return sample;
        });
    }

    private Map<String, Object> buildBaseline(Long cameraId, DataSourceType dataSource, LocalDateTime evaluatedAt) {
        LocalDateTime from = evaluatedAt.minusDays(14);
        LocalDateTime to = evaluatedAt.minusMinutes(60);
        Map<String, List<BigDecimal>> values = new LinkedHashMap<>();
        for (String metric : METRICS) {
            values.put(metric, new ArrayList<>());
        }

        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("cameraId", cameraId)
                .addValue("dataSource", dataSource.name())
                .addValue("from", from)
                .addValue("to", to);

        jdbcTemplate.query("""
                SELECT
                    fps_avg,
                    frame_drop_rate,
                    latency_p95_ms,
                    blur_score_avg,
                    ocr_fail_rate,
                    cpu_usage_pct,
                    memory_usage_pct,
                    network_rtt_ms
                FROM camera_health_samples
                WHERE camera_id = :cameraId
                  AND data_source = :dataSource
                  AND quality_status = 'COMPLETE'
                  AND is_imputed = FALSE
                  AND is_late_sample = FALSE
                  AND sampled_at >= :from
                  AND sampled_at < :to
                """, params, rs -> {
            addMetric(values, "fps_avg", rs.getBigDecimal("fps_avg"));
            addMetric(values, "frame_drop_rate", rs.getBigDecimal("frame_drop_rate"));
            addMetric(values, "latency_p95_ms", toBigDecimal(rs.getObject("latency_p95_ms")));
            addMetric(values, "blur_score_avg", rs.getBigDecimal("blur_score_avg"));
            addMetric(values, "ocr_fail_rate", rs.getBigDecimal("ocr_fail_rate"));
            addMetric(values, "cpu_usage_pct", rs.getBigDecimal("cpu_usage_pct"));
            addMetric(values, "memory_usage_pct", rs.getBigDecimal("memory_usage_pct"));
            addMetric(values, "network_rtt_ms", toBigDecimal(rs.getObject("network_rtt_ms")));
        });

        Map<String, Object> metrics = new LinkedHashMap<>();
        int sampleCount = 0;
        for (Map.Entry<String, List<BigDecimal>> entry : values.entrySet()) {
            if (entry.getValue().isEmpty()) {
                continue;
            }
            sampleCount = Math.max(sampleCount, entry.getValue().size());
            BigDecimal median = median(entry.getValue());
            metrics.put(entry.getKey(), Map.of(
                    "median", median,
                    "mad", mad(entry.getValue(), median)
            ));
        }

        Map<String, Object> baseline = new LinkedHashMap<>();
        baseline.put("source", "CAMERA_30_MINUTE_BUCKET_14D");
        baseline.put("from", PredictiveTimeUtils.toSeoulOffset(from));
        baseline.put("to", PredictiveTimeUtils.toSeoulOffset(to));
        baseline.put("sampleCount", sampleCount);
        baseline.put("metrics", metrics);
        return baseline;
    }

    private Map<String, Object> buildTrafficContext(Long cameraId, DataSourceType dataSource, LocalDateTime evaluatedAt) {
        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("cameraId", cameraId)
                .addValue("dataSource", dataSource.name())
                .addValue("from", evaluatedAt.minusMinutes(10))
                .addValue("to", evaluatedAt);
        Integer currentCount = jdbcTemplate.query("""
                SELECT vehicle_count
                FROM traffic_context_samples
                WHERE camera_id = :cameraId
                  AND data_source = :dataSource
                  AND sampled_at >= :from
                  AND sampled_at <= :to
                ORDER BY sampled_at DESC
                LIMIT 1
                """, params, rs -> rs.next() ? (Integer) rs.getObject("vehicle_count") : null);

        Map<String, Object> trafficContext = new LinkedHashMap<>();
        trafficContext.put("currentCameraVehicleCount", currentCount);
        trafficContext.put("adjacentCameraVehicleCounts", Map.of());
        trafficContext.put("qualityStatus", currentCount == null ? "INSUFFICIENT" : "COMPLETE");
        return trafficContext;
    }

    private Map<String, Object> buildPolicy(AnomalyPolicy policy) {
        Map<String, Object> config = policy.getConfigJson() != null ? policy.getConfigJson() : Map.of();
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("policyCode", policy.getPolicyCode());
        payload.put("windowMinutes", numberFromConfig(config, "windowMinutes", 15));
        payload.put("minimumValidSamples", policy.getMinimumSampleCount() != null
                ? policy.getMinimumSampleCount()
                : numberFromConfig(config, "minimumValidSamples", 12));
        payload.put("ewmaAlpha", decimalFromConfig(config, "ewmaAlpha", new BigDecimal("0.3")));
        payload.put("minimumTrendConfidence", decimalFromConfig(config, "minimumTrendConfidence", new BigDecimal("0.6")));
        payload.put("predictionHorizonMinutes", policy.getPredictionHorizonMinutes() != null
                ? policy.getPredictionHorizonMinutes()
                : numberFromConfig(config, "predictionHorizonMinutes", 10));
        return payload;
    }

    private void addMetric(Map<String, List<BigDecimal>> values, String metric, BigDecimal value) {
        if (value != null) {
            values.get(metric).add(value);
        }
    }

    private BigDecimal median(List<BigDecimal> values) {
        List<BigDecimal> sorted = values.stream().sorted().toList();
        int mid = sorted.size() / 2;
        if (sorted.size() % 2 == 1) {
            return sorted.get(mid);
        }
        return sorted.get(mid - 1).add(sorted.get(mid)).divide(new BigDecimal("2"), 6, RoundingMode.HALF_UP);
    }

    private BigDecimal mad(List<BigDecimal> values, BigDecimal median) {
        List<BigDecimal> deviations = values.stream()
                .map(value -> value.subtract(median).abs())
                .sorted()
                .toList();
        if (deviations.isEmpty()) {
            return BigDecimal.ZERO;
        }
        return median(deviations);
    }

    private BigDecimal toBigDecimal(Object value) {
        if (value == null) {
            return null;
        }
        return new BigDecimal(value.toString());
    }

    private int numberFromConfig(Map<String, Object> config, String key, int defaultValue) {
        Object value = config.get(key);
        return value == null ? defaultValue : Integer.parseInt(value.toString());
    }

    private BigDecimal decimalFromConfig(Map<String, Object> config, String key, BigDecimal defaultValue) {
        Object value = config.get(key);
        return value == null ? defaultValue : new BigDecimal(value.toString());
    }
}
