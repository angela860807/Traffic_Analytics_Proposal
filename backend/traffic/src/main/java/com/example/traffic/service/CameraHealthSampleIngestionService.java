package com.example.traffic.service;

import com.example.traffic.dto.request.predictive.CameraHealthSampleCreateRequest;
import com.example.traffic.dto.response.predictive.CameraHealthSampleSaveResponse;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.repository.CameraRepository;
import com.example.traffic.util.PredictiveTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class CameraHealthSampleIngestionService {

    private static final Duration LATE_SAMPLE_THRESHOLD = Duration.ofMinutes(10);

    private final CameraRepository cameraRepository;
    private final NamedParameterJdbcTemplate jdbcTemplate;

    @Transactional
    public CameraHealthSampleSaveResponse save(CameraHealthSampleCreateRequest request) {
        if (!cameraRepository.existsById(request.getCameraId())) {
            throw new BusinessException(
                    "Camera not found: " + request.getCameraId(),
                    HttpStatus.NOT_FOUND
            );
        }

        LocalDateTime sampledAt = PredictiveTimeUtils.toLocalDateTime(request.getSampledAt());
        LocalDateTime lastFrameAt = PredictiveTimeUtils.toLocalDateTime(request.getLastFrameAt());
        boolean lateSample = Duration.between(sampledAt, LocalDateTime.now(PredictiveTimeUtils.SERVICE_ZONE))
                .compareTo(LATE_SAMPLE_THRESHOLD) > 0;

        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("cameraId", request.getCameraId())
                .addValue("processorCode", request.getProcessorCode())
                .addValue("sampledAt", sampledAt)
                .addValue("sampleWindowSeconds", request.getSampleWindowSeconds())
                .addValue("fpsAvg", request.getFpsAvg())
                .addValue("frameDropRate", request.getFrameDropRate())
                .addValue("latencyP95Ms", request.getLatencyP95Ms())
                .addValue("blurScoreAvg", request.getBlurScoreAvg())
                .addValue("brightnessScoreAvg", request.getBrightnessScoreAvg())
                .addValue("detectionCount", request.getDetectionCount())
                .addValue("ocrAttemptCount", request.getOcrAttemptCount())
                .addValue("ocrFailureCount", request.getOcrFailureCount())
                .addValue("ocrFailRate", request.getOcrFailRate())
                .addValue("cpuUsagePct", request.getCpuUsagePct())
                .addValue("memoryUsagePct", request.getMemoryUsagePct())
                .addValue("diskUsagePct", request.getDiskUsagePct())
                .addValue("networkRttMs", request.getNetworkRttMs())
                .addValue("lastFrameAt", lastFrameAt)
                .addValue("dataSource", request.getDataSource().name())
                .addValue("qualityStatus", request.getQualityStatus().name())
                .addValue("isImputed", request.isImputed())
                .addValue("isLateSample", lateSample)
                .addValue("idempotencyKey", request.getIdempotencyKey())
                .addValue("createdAt", LocalDateTime.now(PredictiveTimeUtils.SERVICE_ZONE));

        var existingRows = jdbcTemplate.queryForList("""
                UPDATE camera_health_samples
                SET
                    camera_id = :cameraId,
                    processor_code = :processorCode,
                    sampled_at = :sampledAt,
                    sample_window_seconds = :sampleWindowSeconds,
                    fps_avg = :fpsAvg,
                    frame_drop_rate = :frameDropRate,
                    latency_p95_ms = :latencyP95Ms,
                    blur_score_avg = :blurScoreAvg,
                    brightness_score_avg = :brightnessScoreAvg,
                    detection_count = :detectionCount,
                    ocr_attempt_count = :ocrAttemptCount,
                    ocr_failure_count = :ocrFailureCount,
                    ocr_fail_rate = :ocrFailRate,
                    cpu_usage_pct = :cpuUsagePct,
                    memory_usage_pct = :memoryUsagePct,
                    disk_usage_pct = :diskUsagePct,
                    network_rtt_ms = :networkRttMs,
                    last_frame_at = :lastFrameAt,
                    data_source = :dataSource,
                    quality_status = :qualityStatus,
                    is_imputed = :isImputed,
                    is_late_sample = :isLateSample,
                    idempotency_key = :idempotencyKey
                WHERE idempotency_key = :idempotencyKey
                   OR (camera_id = :cameraId AND sampled_at = :sampledAt)
                RETURNING id, FALSE AS created
                """, params);

        Map<String, Object> row = existingRows.isEmpty()
                ? jdbcTemplate.queryForMap("""
                INSERT INTO camera_health_samples (
                    camera_id,
                    processor_code,
                    sampled_at,
                    sample_window_seconds,
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
                    data_source,
                    quality_status,
                    is_imputed,
                    is_late_sample,
                    idempotency_key,
                    created_at
                )
                VALUES (
                    :cameraId,
                    :processorCode,
                    :sampledAt,
                    :sampleWindowSeconds,
                    :fpsAvg,
                    :frameDropRate,
                    :latencyP95Ms,
                    :blurScoreAvg,
                    :brightnessScoreAvg,
                    :detectionCount,
                    :ocrAttemptCount,
                    :ocrFailureCount,
                    :ocrFailRate,
                    :cpuUsagePct,
                    :memoryUsagePct,
                    :diskUsagePct,
                    :networkRttMs,
                    :lastFrameAt,
                    :dataSource,
                    :qualityStatus,
                    :isImputed,
                    :isLateSample,
                    :idempotencyKey,
                    :createdAt
                )
                RETURNING id, (xmax = 0) AS created
                """, params)
                : existingRows.get(0);

        return CameraHealthSampleSaveResponse.builder()
                .sampleId(((Number) row.get("id")).longValue())
                .created(Boolean.TRUE.equals(row.get("created")))
                .build();
    }
}
