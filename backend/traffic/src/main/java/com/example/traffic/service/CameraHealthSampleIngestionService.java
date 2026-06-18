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
                .addValue("idempotencyKey", request.getIdempotencyKey());

        Map<String, Object> row = jdbcTemplate.queryForMap("""
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
                    idempotency_key
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
                    :idempotencyKey
                )
                ON CONFLICT (camera_id, sampled_at)
                DO UPDATE SET
                    processor_code = EXCLUDED.processor_code,
                    sample_window_seconds = EXCLUDED.sample_window_seconds,
                    fps_avg = EXCLUDED.fps_avg,
                    frame_drop_rate = EXCLUDED.frame_drop_rate,
                    latency_p95_ms = EXCLUDED.latency_p95_ms,
                    blur_score_avg = EXCLUDED.blur_score_avg,
                    brightness_score_avg = EXCLUDED.brightness_score_avg,
                    detection_count = EXCLUDED.detection_count,
                    ocr_attempt_count = EXCLUDED.ocr_attempt_count,
                    ocr_failure_count = EXCLUDED.ocr_failure_count,
                    ocr_fail_rate = EXCLUDED.ocr_fail_rate,
                    cpu_usage_pct = EXCLUDED.cpu_usage_pct,
                    memory_usage_pct = EXCLUDED.memory_usage_pct,
                    disk_usage_pct = EXCLUDED.disk_usage_pct,
                    network_rtt_ms = EXCLUDED.network_rtt_ms,
                    last_frame_at = EXCLUDED.last_frame_at,
                    data_source = EXCLUDED.data_source,
                    quality_status = EXCLUDED.quality_status,
                    is_imputed = EXCLUDED.is_imputed,
                    is_late_sample = EXCLUDED.is_late_sample,
                    idempotency_key = EXCLUDED.idempotency_key
                RETURNING id, (xmax = 0) AS created
                """, params);

        return CameraHealthSampleSaveResponse.builder()
                .sampleId(((Number) row.get("id")).longValue())
                .created(Boolean.TRUE.equals(row.get("created")))
                .build();
    }
}
