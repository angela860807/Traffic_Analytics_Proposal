package com.example.traffic.service;

import com.example.traffic.common.enums.DataSourceType;
import com.example.traffic.dto.response.DemoScriptRunResponse;
import com.example.traffic.etc.BusinessException;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.Duration;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class DemoScriptService {

    private static final ZoneId SERVICE_ZONE = ZoneId.of("Asia/Seoul");

    private static final Map<String, String> SCRIPT_LABELS = Map.of(
            "RESET_HEALTH_DEMO", "Reset demo data",
            "IMPORT_HEALTH_SAMPLES", "Import time-series samples",
            "CHECK_HEALTH_DEMO", "Prepare and verify demo"
    );

    private static final String HEALTH_SAMPLE_CSV = """
            scenario,camera_id,fps_avg,frame_drop_rate,latency_p95_ms,blur_score_avg,ocr_fail_rate,cpu_usage_pct,memory_usage_pct,network_rtt_ms,quality_status
            normal_1,5,28.0,0.01,120,0.05,0.03,34.0,50.0,38,COMPLETE
            normal_2,5,28.2,0.01,118,0.05,0.03,35.0,51.0,39,COMPLETE
            normal_3,5,27.9,0.02,125,0.06,0.04,36.0,51.0,40,COMPLETE
            normal_4,5,28.4,0.01,121,0.05,0.03,35.0,52.0,38,COMPLETE
            blur_1,17,27.0,0.02,140,0.88,0.08,45.0,58.0,42,COMPLETE
            blur_2,17,26.8,0.02,145,0.91,0.09,46.0,59.0,43,COMPLETE
            blur_3,17,26.5,0.03,150,0.94,0.10,47.0,60.0,44,COMPLETE
            blur_4,17,26.2,0.03,155,0.96,0.11,48.0,61.0,45,COMPLETE
            dropout_1,11,24.0,0.62,180,0.08,0.06,48.0,62.0,45,COMPLETE
            dropout_2,11,23.5,0.68,190,0.08,0.06,49.0,63.0,46,COMPLETE
            dropout_3,11,22.8,0.74,205,0.09,0.07,50.0,64.0,48,COMPLETE
            dropout_4,11,22.0,0.82,220,0.09,0.07,52.0,65.0,50,COMPLETE
            low_fps_1,10,8.8,0.06,160,0.08,0.06,44.0,57.0,41,COMPLETE
            low_fps_2,10,7.4,0.07,165,0.08,0.06,45.0,58.0,42,COMPLETE
            low_fps_3,10,5.8,0.08,175,0.09,0.07,46.0,59.0,43,COMPLETE
            low_fps_4,10,3.2,0.09,185,0.09,0.07,47.0,60.0,44,COMPLETE
            latency_1,12,24.8,0.04,2300,0.10,0.05,49.0,62.0,80,COMPLETE
            latency_2,12,24.2,0.05,2600,0.10,0.05,51.0,63.0,85,COMPLETE
            latency_3,12,23.7,0.05,3100,0.11,0.06,53.0,64.0,88,COMPLETE
            latency_4,12,23.1,0.06,3600,0.11,0.06,55.0,65.0,90,COMPLETE
            network_1,13,25.2,0.05,420,0.12,0.06,48.0,60.0,620,COMPLETE
            network_2,13,24.9,0.05,450,0.12,0.06,49.0,61.0,710,COMPLETE
            network_3,13,24.4,0.06,480,0.13,0.07,50.0,62.0,820,COMPLETE
            network_4,13,24.0,0.06,520,0.13,0.07,51.0,63.0,930,COMPLETE
            resource_1,14,23.8,0.05,180,0.10,0.06,88.0,89.0,70,COMPLETE
            resource_2,14,23.5,0.05,190,0.10,0.06,91.0,92.0,72,COMPLETE
            resource_3,14,23.2,0.06,205,0.11,0.07,94.0,95.0,75,COMPLETE
            resource_4,14,22.9,0.06,220,0.11,0.07,96.0,96.0,78,COMPLETE
            """;

    private final NamedParameterJdbcTemplate jdbcTemplate;
    private final PredictiveRuleEvaluationOrchestrationService ruleEvaluationOrchestrationService;

    public DemoScriptRunResponse run(String scriptId, String dataSource) {
        String normalizedScriptId = normalizeScriptId(scriptId);
        DataSourceType normalizedDataSource = normalizeDataSource(dataSource);
        String label = SCRIPT_LABELS.get(normalizedScriptId);
        if (label == null) {
            throw new BusinessException("Unsupported demo script: " + scriptId, HttpStatus.BAD_REQUEST);
        }

        OffsetDateTime startedAt = OffsetDateTime.now(SERVICE_ZONE);
        List<String> outputLines = switch (normalizedScriptId) {
            case "RESET_HEALTH_DEMO" -> resetDemoData(normalizedDataSource);
            case "IMPORT_HEALTH_SAMPLES" -> importHealthSamples(normalizedDataSource);
            case "CHECK_HEALTH_DEMO" -> prepareAndVerify(normalizedDataSource);
            default -> throw new BusinessException("Unsupported demo script: " + scriptId, HttpStatus.BAD_REQUEST);
        };
        OffsetDateTime finishedAt = OffsetDateTime.now(SERVICE_ZONE);

        return new DemoScriptRunResponse(
                normalizedScriptId,
                label,
                "SUCCESS",
                0,
                normalizedDataSource.name(),
                startedAt,
                finishedAt,
                outputLines,
                Duration.between(startedAt, finishedAt).toSeconds()
        );
    }

    private String normalizeScriptId(String scriptId) {
        if (scriptId == null || scriptId.isBlank()) {
            throw new BusinessException("Script id is required.", HttpStatus.BAD_REQUEST);
        }
        return scriptId.trim().toUpperCase(Locale.ROOT);
    }

    private DataSourceType normalizeDataSource(String dataSource) {
        String value = dataSource == null || dataSource.isBlank() ? "REAL" : dataSource.trim().toUpperCase(Locale.ROOT);
        try {
            return DataSourceType.valueOf(value);
        } catch (IllegalArgumentException ex) {
            throw new BusinessException("Unsupported data source: " + dataSource, HttpStatus.BAD_REQUEST);
        }
    }

    private List<String> prepareAndVerify(DataSourceType dataSource) {
        List<String> output = new ArrayList<>();
        output.addAll(resetDemoData(dataSource));
        output.addAll(importHealthSamples(dataSource));
        output.addAll(countRows(dataSource));
        return output;
    }

    private List<String> resetDemoData(DataSourceType dataSource) {
        MapSqlParameterSource params = new MapSqlParameterSource("dataSource", dataSource.name());
        jdbcTemplate.update("""
                DELETE FROM maintenance_ticket_histories
                WHERE maintenance_ticket_id IN (
                    SELECT mt.id
                    FROM maintenance_tickets mt
                    JOIN anomaly_events ae ON ae.id = mt.anomaly_event_id
                    WHERE ae.data_source = :dataSource
                )
                """, params);
        jdbcTemplate.update("""
                DELETE FROM maintenance_tickets
                WHERE anomaly_event_id IN (
                    SELECT id FROM anomaly_events WHERE data_source = :dataSource
                )
                """, params);
        jdbcTemplate.update("""
                DELETE FROM anomaly_event_evidence
                WHERE anomaly_event_id IN (
                    SELECT id FROM anomaly_events WHERE data_source = :dataSource
                )
                """, params);
        jdbcTemplate.update("DELETE FROM anomaly_events WHERE data_source = :dataSource", params);
        jdbcTemplate.update("DELETE FROM model_prediction_logs WHERE data_source = :dataSource", params);
        jdbcTemplate.update("DELETE FROM camera_health_samples WHERE data_source = :dataSource", params);
        int baselineRows = jdbcTemplate.update("""
                INSERT INTO camera_health_samples (
                    camera_id, sampled_at, sample_window_seconds, fps_avg, frame_drop_rate,
                    latency_p95_ms, blur_score_avg, brightness_score_avg, ocr_fail_rate,
                    cpu_usage_pct, memory_usage_pct, disk_usage_pct, network_rtt_ms,
                    detection_count, ocr_attempt_count, ocr_failure_count, quality_status,
                    is_late_sample, is_imputed, processor_code, data_source, idempotency_key
                )
                SELECT
                    c.camera_id, CURRENT_TIMESTAMP, 60, 25.00, 0.010000,
                    120, 0.120000, 0.650000, 0.020000,
                    35.00, 42.00, 48.00, 30,
                    24, 20, 0, 'COMPLETE',
                    FALSE, FALSE, 'predictive-demo-reset', :dataSource,
                    'demo-reset-normal-' || :dataSource || '-' || c.camera_id
                FROM cameras c
                """, params);

        return List.of(
                "Reset dataSource=" + dataSource.name(),
                "Inserted normal baseline samples=" + baselineRows
        );
    }

    private List<String> importHealthSamples(DataSourceType dataSource) {
        String runId = String.valueOf(System.currentTimeMillis());
        List<DemoSample> samples = parseSamples();
        List<String> output = new ArrayList<>();
        int rowIndex = 0;
        int savedCandidates = 0;
        for (DemoSample sample : samples) {
            OffsetDateTime sampledAt = OffsetDateTime.now(SERVICE_ZONE).plusMinutes(rowIndex * 5L);
            insertSample(sample, dataSource, runId, rowIndex, sampledAt);
            savedCandidates += ruleEvaluationOrchestrationService.evaluateLatestRuleSamples(sample.cameraId(), dataSource);
            output.add("Imported scenario=" + sample.scenario() + " cameraId=" + sample.cameraId());
            rowIndex += 1;
        }
        int shadowRows = insertShadowLogs(runId);
        output.add("Imported samples=" + samples.size());
        output.add("Saved rule candidates=" + savedCandidates);
        output.add("Upserted AI Shadow logs=" + shadowRows);
        return output;
    }

    private void insertSample(DemoSample sample, DataSourceType dataSource, String runId, int rowIndex, OffsetDateTime sampledAt) {
        int ocrAttemptCount = 100;
        int detectionCount = 25;
        int ocrFailureCount = sample.ocrFailRate().multiply(BigDecimal.valueOf(ocrAttemptCount)).setScale(0, java.math.RoundingMode.HALF_UP).intValue();
        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("idempotencyKey", "demo-" + runId + "-" + sample.scenario() + "-" + sample.cameraId() + "-" + rowIndex)
                .addValue("cameraId", sample.cameraId())
                .addValue("sampledAt", sampledAt.toLocalDateTime())
                .addValue("sampleWindowSeconds", 300)
                .addValue("fpsAvg", sample.fpsAvg())
                .addValue("frameDropRate", sample.frameDropRate())
                .addValue("latencyP95Ms", sample.latencyP95Ms())
                .addValue("blurScoreAvg", sample.blurScoreAvg())
                .addValue("brightnessScoreAvg", BigDecimal.valueOf(0.5))
                .addValue("detectionCount", detectionCount)
                .addValue("ocrAttemptCount", ocrAttemptCount)
                .addValue("ocrFailureCount", ocrFailureCount)
                .addValue("ocrFailRate", sample.ocrFailRate())
                .addValue("cpuUsagePct", sample.cpuUsagePct())
                .addValue("memoryUsagePct", sample.memoryUsagePct())
                .addValue("diskUsagePct", BigDecimal.valueOf(50))
                .addValue("networkRttMs", sample.networkRttMs())
                .addValue("lastFrameAt", sampledAt.toLocalDateTime())
                .addValue("dataSource", dataSource.name())
                .addValue("qualityStatus", sample.qualityStatus());

        jdbcTemplate.update("""
                INSERT INTO camera_health_samples (
                    idempotency_key, camera_id, processor_code, sampled_at, sample_window_seconds,
                    fps_avg, frame_drop_rate, latency_p95_ms, blur_score_avg, brightness_score_avg,
                    detection_count, ocr_attempt_count, ocr_failure_count, ocr_fail_rate,
                    cpu_usage_pct, memory_usage_pct, disk_usage_pct, network_rtt_ms, last_frame_at,
                    data_source, quality_status, is_imputed, is_late_sample, created_at
                ) VALUES (
                    :idempotencyKey, :cameraId, 'predictive-demo-video', :sampledAt, :sampleWindowSeconds,
                    :fpsAvg, :frameDropRate, :latencyP95Ms, :blurScoreAvg, :brightnessScoreAvg,
                    :detectionCount, :ocrAttemptCount, :ocrFailureCount, :ocrFailRate,
                    :cpuUsagePct, :memoryUsagePct, :diskUsagePct, :networkRttMs, :lastFrameAt,
                    :dataSource, :qualityStatus, FALSE, FALSE, CURRENT_TIMESTAMP
                )
                ON CONFLICT (idempotency_key)
                DO UPDATE SET
                    sampled_at = EXCLUDED.sampled_at,
                    fps_avg = EXCLUDED.fps_avg,
                    frame_drop_rate = EXCLUDED.frame_drop_rate,
                    latency_p95_ms = EXCLUDED.latency_p95_ms,
                    blur_score_avg = EXCLUDED.blur_score_avg,
                    ocr_fail_rate = EXCLUDED.ocr_fail_rate,
                    cpu_usage_pct = EXCLUDED.cpu_usage_pct,
                    memory_usage_pct = EXCLUDED.memory_usage_pct,
                    network_rtt_ms = EXCLUDED.network_rtt_ms,
                    last_frame_at = EXCLUDED.last_frame_at
                """, params);
    }

    private int insertShadowLogs(String runId) {
        return jdbcTemplate.update("""
                WITH detector AS (
                  UPDATE detector_versions
                     SET operating_mode = 'SHADOW', active = FALSE
                   WHERE detector_name = 'camera-lstm-autoencoder' AND version = '1.0.0'
                  RETURNING id
                ),
                fallback_detector AS (
                  SELECT id FROM detector_versions
                   WHERE detector_name = 'camera-lstm-autoencoder' AND version = '1.0.0'
                   LIMIT 1
                ),
                imported AS (
                  SELECT
                    camera_id, data_source, MAX(sampled_at) AS evaluated_at, MIN(sampled_at) AS first_sampled_at,
                    AVG(fps_avg) AS fps_avg, MAX(frame_drop_rate) AS frame_drop_rate,
                    MAX(latency_p95_ms) AS latency_p95_ms, MAX(blur_score_avg) AS blur_score_avg,
                    MAX(ocr_fail_rate) AS ocr_fail_rate, MAX(cpu_usage_pct) AS cpu_usage_pct,
                    MAX(memory_usage_pct) AS memory_usage_pct, MAX(network_rtt_ms) AS network_rtt_ms
                  FROM camera_health_samples
                  WHERE idempotency_key LIKE :runPattern
                  GROUP BY camera_id, data_source
                ),
                scored AS (
                  SELECT
                    i.*,
                    LEAST(0.980000, GREATEST(
                      0.180000,
                      (1 - LEAST(COALESCE(i.fps_avg, 30) / 30.0, 1)) * 0.90,
                      COALESCE(i.frame_drop_rate, 0),
                      COALESCE(i.latency_p95_ms, 0) / 1000.0,
                      COALESCE(i.blur_score_avg, 0),
                      COALESCE(i.ocr_fail_rate, 0),
                      COALESCE(i.cpu_usage_pct, 0) / 100.0,
                      COALESCE(i.memory_usage_pct, 0) / 100.0,
                      COALESCE(i.network_rtt_ms, 0) / 500.0
                    ))::NUMERIC(7,6) AS anomaly_score
                  FROM imported i
                )
                INSERT INTO model_prediction_logs (
                  camera_id, detector_version_id, evaluated_at, input_window_from, input_window_to,
                  anomaly_score, warning_threshold, critical_threshold, predicted_anomaly,
                  predicted_severity, data_source, quality_status, feature_schema_version, top_features_json
                )
                SELECT
                  s.camera_id,
                  COALESCE((SELECT id FROM detector), (SELECT id FROM fallback_detector)),
                  s.evaluated_at,
                  LEAST(s.first_sampled_at, s.evaluated_at - INTERVAL '60 minutes'),
                  s.evaluated_at,
                  s.anomaly_score,
                  0.410734,
                  0.462065,
                  s.anomaly_score >= 0.410734,
                  CASE
                    WHEN s.anomaly_score >= 0.462065 THEN 'CRITICAL'
                    WHEN s.anomaly_score >= 0.410734 THEN 'WARNING'
                    ELSE NULL
                  END,
                  s.data_source,
                  'COMPLETE',
                  'camera-health-sequence-v1',
                  jsonb_build_array(
                    jsonb_build_object('featureName', 'fps_avg', 'featureValue', ROUND(((1 - LEAST(COALESCE(s.fps_avg, 30) / 30.0, 1)) * 0.90)::NUMERIC, 2)),
                    jsonb_build_object('featureName', 'frame_drop_rate', 'featureValue', ROUND(COALESCE(s.frame_drop_rate, 0)::NUMERIC, 2)),
                    jsonb_build_object('featureName', 'latency_p95_ms', 'featureValue', ROUND((COALESCE(s.latency_p95_ms, 0) / 1000.0)::NUMERIC, 2)),
                    jsonb_build_object('featureName', 'blur_score_avg', 'featureValue', ROUND(COALESCE(s.blur_score_avg, 0)::NUMERIC, 2)),
                    jsonb_build_object('featureName', 'cpu_usage_pct', 'featureValue', ROUND((COALESCE(s.cpu_usage_pct, 0) / 100.0)::NUMERIC, 2))
                  )
                FROM scored s
                WHERE COALESCE((SELECT id FROM detector), (SELECT id FROM fallback_detector)) IS NOT NULL
                ON CONFLICT (camera_id, detector_version_id, evaluated_at)
                DO UPDATE SET
                  anomaly_score = EXCLUDED.anomaly_score,
                  warning_threshold = EXCLUDED.warning_threshold,
                  critical_threshold = EXCLUDED.critical_threshold,
                  predicted_anomaly = EXCLUDED.predicted_anomaly,
                  predicted_severity = EXCLUDED.predicted_severity,
                  quality_status = EXCLUDED.quality_status,
                  feature_schema_version = EXCLUDED.feature_schema_version,
                  top_features_json = EXCLUDED.top_features_json,
                  created_at = CURRENT_TIMESTAMP
                """, new MapSqlParameterSource("runPattern", "demo-" + runId + "-%"));
    }

    private List<String> countRows(DataSourceType dataSource) {
        MapSqlParameterSource params = new MapSqlParameterSource("dataSource", dataSource.name());
        Map<String, Long> counts = new LinkedHashMap<>();
        counts.put("camera_health_samples", count("SELECT COUNT(*) FROM camera_health_samples WHERE data_source = :dataSource", params));
        counts.put("anomaly_events", count("SELECT COUNT(*) FROM anomaly_events WHERE data_source = :dataSource", params));
        counts.put("maintenance_tickets", count("""
                SELECT COUNT(*)
                FROM maintenance_tickets mt
                JOIN anomaly_events ae ON ae.id = mt.anomaly_event_id
                WHERE ae.data_source = :dataSource
                """, params));
        counts.put("model_prediction_logs", count("SELECT COUNT(*) FROM model_prediction_logs WHERE data_source = :dataSource", params));
        return counts.entrySet().stream()
                .map(entry -> entry.getKey() + "=" + entry.getValue())
                .toList();
    }

    private long count(String sql, MapSqlParameterSource params) {
        Long value = jdbcTemplate.queryForObject(sql, params, Long.class);
        return value == null ? 0L : value;
    }

    private List<DemoSample> parseSamples() {
        return HEALTH_SAMPLE_CSV.lines()
                .skip(1)
                .filter(line -> !line.isBlank())
                .map(line -> {
                    String[] columns = line.split(",");
                    return new DemoSample(
                            columns[0],
                            Long.parseLong(columns[1]),
                            new BigDecimal(columns[2]),
                            new BigDecimal(columns[3]),
                            Integer.parseInt(columns[4]),
                            new BigDecimal(columns[5]),
                            new BigDecimal(columns[6]),
                            new BigDecimal(columns[7]),
                            new BigDecimal(columns[8]),
                            Integer.parseInt(columns[9]),
                            columns[10]
                    );
                })
                .toList();
    }

    private record DemoSample(
            String scenario,
            Long cameraId,
            BigDecimal fpsAvg,
            BigDecimal frameDropRate,
            Integer latencyP95Ms,
            BigDecimal blurScoreAvg,
            BigDecimal ocrFailRate,
            BigDecimal cpuUsagePct,
            BigDecimal memoryUsagePct,
            Integer networkRttMs,
            String qualityStatus
    ) {
    }
}