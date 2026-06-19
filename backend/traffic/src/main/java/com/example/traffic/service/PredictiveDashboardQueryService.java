package com.example.traffic.service;

import com.example.traffic.common.enums.*;
import com.example.traffic.dto.response.predictive.*;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.repository.AnomalyPolicyRepository;
import com.example.traffic.repository.CameraRepository;
import com.example.traffic.util.PredictiveTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PredictiveDashboardQueryService {

    private static final List<String> CAMERA_SORT_FIELDS = List.of(
            "cameraName",
            "healthScore",
            "latestSampledAt"
    );

    private final CameraRepository cameraRepository;
    private final AnomalyPolicyRepository anomalyPolicyRepository;
    private final NamedParameterJdbcTemplate jdbcTemplate;

    public PredictiveSummaryResponse getSummary(DataSourceType dataSource) {
        List<CameraOperatingStatusResponse> cameras = getCameraStatuses(
                null,
                null,
                dataSource,
                0,
                100,
                "cameraName,asc"
        ).getContent();

        long openAnomalies = countLong("""
                SELECT COUNT(*)
                FROM anomaly_events
                WHERE status IN ('OPEN', 'ACKNOWLEDGED')
                  AND data_source = :dataSource
                """, dataSource);
        long predictedRisks = countLong("""
                SELECT COUNT(*)
                FROM model_prediction_logs
                WHERE predicted_anomaly = TRUE
                  AND data_source = :dataSource
                """, dataSource);
        long overdueTickets = countLong("""
                SELECT COUNT(*)
                FROM maintenance_tickets
                WHERE status IN ('OPEN', 'ASSIGNED')
                  AND (
                    (due_ack_at IS NOT NULL AND due_ack_at < CURRENT_TIMESTAMP)
                    OR (due_start_at IS NOT NULL AND due_start_at < CURRENT_TIMESTAMP)
                  )
                """, dataSource);

        return PredictiveSummaryResponse.builder()
                .totalCameras(cameraRepository.count())
                .normalCameras(countByStatus(cameras, HealthStatus.NORMAL))
                .degradedCameras(countByStatus(cameras, HealthStatus.DEGRADED))
                .criticalCameras(countByStatus(cameras, HealthStatus.CRITICAL))
                .offlineCameras(countByStatus(cameras, HealthStatus.OFFLINE))
                .baselineLearningCameras(countLearningOrInsufficient(cameras))
                .openAnomalies(openAnomalies)
                .predictedRisks(predictedRisks)
                .overdueTickets(overdueTickets)
                .mttaMinutes(BigDecimal.ZERO.setScale(1))
                .mttrMinutes(BigDecimal.ZERO.setScale(1))
                .generatedAt(PredictiveTimeUtils.toSeoulOffset(java.time.LocalDateTime.now(PredictiveTimeUtils.SERVICE_ZONE)))
                .build();
    }

    public PageResponse<CameraOperatingStatusResponse> getCameraStatuses(
            Long zoneId,
            HealthStatus healthStatus,
            DataSourceType dataSource,
            int page,
            int size,
            String sort
    ) {
        validatePage(page, size);
        SortSpec sortSpec = parseSort(sort, CAMERA_SORT_FIELDS);

        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("zoneFilterDisabled", zoneId == null)
                .addValue("zoneId", zoneId)
                .addValue("dataSource", dataSource.name());

        List<CameraOperatingStatusResponse> rows = jdbcTemplate.query("""
                SELECT
                    c.camera_id,
                    c.camera_name,
                    c.zone_id,
                    s.sampled_at,
                    s.fps_avg,
                    s.frame_drop_rate,
                    s.latency_p95_ms,
                    s.blur_score_avg,
                    s.ocr_fail_rate,
                    s.cpu_usage_pct,
                    s.memory_usage_pct,
                    s.network_rtt_ms,
                    s.quality_status,
                    COALESCE(a.active_anomaly_count, 0) AS active_anomaly_count,
                    COALESCE(p.predicted_risk_count, 0) AS predicted_risk_count
                FROM cameras c
                LEFT JOIN LATERAL (
                    SELECT *
                    FROM camera_health_samples chs
                    WHERE chs.camera_id = c.camera_id
                      AND chs.data_source = :dataSource
                    ORDER BY chs.sampled_at DESC
                    LIMIT 1
                ) s ON TRUE
                LEFT JOIN LATERAL (
                    SELECT COUNT(*) AS active_anomaly_count
                    FROM anomaly_events ae
                    WHERE ae.target_camera_id = c.camera_id
                      AND ae.status IN ('OPEN', 'ACKNOWLEDGED', 'RECOVERED')
                      AND ae.data_source = :dataSource
                ) a ON TRUE
                LEFT JOIN LATERAL (
                    SELECT COUNT(*) AS predicted_risk_count
                    FROM model_prediction_logs mpl
                    WHERE mpl.camera_id = c.camera_id
                      AND mpl.predicted_anomaly = TRUE
                      AND mpl.data_source = :dataSource
                ) p ON TRUE
                WHERE (:zoneFilterDisabled = TRUE OR c.zone_id = :zoneId)
                """, params, (rs, rowNum) -> toCameraOperatingStatus(rs, dataSource));

        List<CameraOperatingStatusResponse> filtered = rows.stream()
                .filter(item -> healthStatus == null || item.getHealthStatus() == healthStatus)
                .sorted(cameraComparator(sortSpec))
                .toList();
        int fromIndex = Math.min(page * size, filtered.size());
        int toIndex = Math.min(fromIndex + size, filtered.size());
        List<CameraOperatingStatusResponse> content = filtered.subList(fromIndex, toIndex);

        return PageResponse.<CameraOperatingStatusResponse>builder()
                .content(content)
                .page(page)
                .size(size)
                .totalElements(filtered.size())
                .totalPages((int) Math.ceil((double) filtered.size() / size))
                .sort(sortSpec.field() + "," + sortSpec.direction())
                .build();
    }

    public CameraHealthHistoryResponse getCameraHealthHistory(
            Long cameraId,
            OffsetDateTime from,
            OffsetDateTime to,
            DataSourceType dataSource
    ) {
        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("cameraId", cameraId)
                .addValue("from", PredictiveTimeUtils.toLocalDateTime(from))
                .addValue("to", PredictiveTimeUtils.toLocalDateTime(to))
                .addValue("dataSource", dataSource.name());

        List<CameraHealthHistoryResponse.Sample> samples = jdbcTemplate.query("""
                SELECT
                    sampled_at,
                    fps_avg,
                    frame_drop_rate,
                    latency_p95_ms,
                    blur_score_avg,
                    ocr_fail_rate,
                    cpu_usage_pct,
                    memory_usage_pct,
                    network_rtt_ms,
                    quality_status
                FROM camera_health_samples
                WHERE camera_id = :cameraId
                  AND data_source = :dataSource
                  AND sampled_at >= :from
                  AND sampled_at < :to
                ORDER BY sampled_at ASC
                """, params, (rs, rowNum) -> CameraHealthHistoryResponse.Sample.builder()
                .sampledAt(PredictiveTimeUtils.toSeoulOffset(rs.getTimestamp("sampled_at").toLocalDateTime()))
                .fpsAvg(rs.getBigDecimal("fps_avg"))
                .frameDropRate(rs.getBigDecimal("frame_drop_rate"))
                .latencyP95Ms((Integer) rs.getObject("latency_p95_ms"))
                .blurScoreAvg(rs.getBigDecimal("blur_score_avg"))
                .ocrFailRate(rs.getBigDecimal("ocr_fail_rate"))
                .cpuUsagePct(rs.getBigDecimal("cpu_usage_pct"))
                .memoryUsagePct(rs.getBigDecimal("memory_usage_pct"))
                .networkRttMs((Integer) rs.getObject("network_rtt_ms"))
                .healthScore(calculateHealthScore(rs))
                .qualityStatus(QualityStatus.valueOf(rs.getString("quality_status")))
                .build());

        return CameraHealthHistoryResponse.builder()
                .cameraId(cameraId)
                .samples(samples)
                .build();
    }

    public TrafficContextHistoryResponse getTrafficContextHistory(
            Long cameraId,
            Long zoneId,
            OffsetDateTime from,
            OffsetDateTime to,
            DataSourceType dataSource
    ) {
        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("cameraId", cameraId)
                .addValue("zoneId", zoneId)
                .addValue("from", PredictiveTimeUtils.toLocalDateTime(from))
                .addValue("to", PredictiveTimeUtils.toLocalDateTime(to))
                .addValue("dataSource", dataSource.name());

        List<TrafficContextHistoryResponse.Sample> samples = jdbcTemplate.query("""
                SELECT
                    sampled_at,
                    window_minutes,
                    vehicle_count,
                    avg_speed_kmh,
                    speed_violation_count,
                    ocr_attempt_count,
                    ocr_success_count,
                    ocr_failure_count,
                    quality_status,
                    data_source
                FROM traffic_context_samples
                WHERE camera_id = :cameraId
                  AND zone_id = :zoneId
                  AND data_source = :dataSource
                  AND sampled_at >= :from
                  AND sampled_at < :to
                ORDER BY sampled_at ASC
                """, params, (rs, rowNum) -> TrafficContextHistoryResponse.Sample.builder()
                .sampledAt(PredictiveTimeUtils.toSeoulOffset(rs.getTimestamp("sampled_at").toLocalDateTime()))
                .windowMinutes((Integer) rs.getObject("window_minutes"))
                .vehicleCount((Integer) rs.getObject("vehicle_count"))
                .avgSpeedKmh(rs.getBigDecimal("avg_speed_kmh"))
                .speedViolationCount((Integer) rs.getObject("speed_violation_count"))
                .ocrAttemptCount((Integer) rs.getObject("ocr_attempt_count"))
                .ocrSuccessCount((Integer) rs.getObject("ocr_success_count"))
                .ocrFailureCount((Integer) rs.getObject("ocr_failure_count"))
                .qualityStatus(QualityStatus.valueOf(rs.getString("quality_status")))
                .dataSource(DataSourceType.valueOf(rs.getString("data_source")))
                .build());

        return TrafficContextHistoryResponse.builder()
                .cameraId(cameraId)
                .zoneId(zoneId)
                .samples(samples)
                .build();
    }

    public List<AnomalyPolicyResponse> getPolicies(Boolean enabled) {
        return (enabled == null
                ? anomalyPolicyRepository.findAllByOrderByPolicyCodeAsc()
                : anomalyPolicyRepository.findByEnabledOrderByPolicyCodeAsc(enabled))
                .stream()
                .map(policy -> AnomalyPolicyResponse.builder()
                        .policyCode(policy.getPolicyCode())
                        .anomalyType(policy.getAnomalyType())
                        .detectionMethod(policy.getDetectionMethod())
                        .warningThreshold(policy.getWarningThreshold())
                        .criticalThreshold(policy.getCriticalThreshold())
                        .warningConsecutiveWindows(policy.getWarningConsecutiveWindows())
                        .criticalConsecutiveWindows(policy.getCriticalConsecutiveWindows())
                        .minimumSampleCount(policy.getMinimumSampleCount())
                        .predictionHorizonMinutes(policy.getPredictionHorizonMinutes())
                        .config(policy.getConfigJson() != null ? policy.getConfigJson() : Map.of())
                        .enabled(policy.isEnabled())
                        .updatedAt(PredictiveTimeUtils.toSeoulOffset(policy.getUpdatedAt()))
                        .build())
                .toList();
    }

    private CameraOperatingStatusResponse toCameraOperatingStatus(
            ResultSet rs,
            DataSourceType dataSource
    ) throws SQLException {
        BigDecimal healthScore = calculateHealthScore(rs);
        HealthStatus healthStatus = resolveHealthStatus(healthScore, rs.getString("quality_status"));
        return CameraOperatingStatusResponse.builder()
                .cameraId(rs.getLong("camera_id"))
                .cameraName(rs.getString("camera_name"))
                .zoneId(rs.getLong("zone_id"))
                .healthScore(healthScore)
                .healthStatus(healthStatus)
                .baselineStatus(healthStatus == HealthStatus.INSUFFICIENT_DATA
                        ? BaselineStatus.LEARNING : BaselineStatus.READY)
                .activeAnomalyCount(rs.getLong("active_anomaly_count"))
                .predictedRiskCount(rs.getLong("predicted_risk_count"))
                .latestSampledAt(rs.getTimestamp("sampled_at") == null
                        ? null
                        : PredictiveTimeUtils.toSeoulOffset(rs.getTimestamp("sampled_at").toLocalDateTime()))
                .dataSource(dataSource)
                .build();
    }

    private BigDecimal calculateHealthScore(ResultSet rs) throws SQLException {
        BigDecimal fpsScore = lowerIsWorseScore(rs.getBigDecimal("fps_avg"), new BigDecimal("5"), new BigDecimal("10"));
        BigDecimal frameDropScore = higherIsWorseScore(rs.getBigDecimal("frame_drop_rate"), new BigDecimal("0.30"), new BigDecimal("0.60"));
        BigDecimal latencyScore = higherIsWorseScore(toBigDecimal(rs.getObject("latency_p95_ms")), new BigDecimal("2000"), new BigDecimal("5000"));
        BigDecimal blurScore = higherIsWorseScore(rs.getBigDecimal("blur_score_avg"), new BigDecimal("0.75"), new BigDecimal("0.90"));
        BigDecimal ocrScore = higherIsWorseScore(rs.getBigDecimal("ocr_fail_rate"), new BigDecimal("0.70"), new BigDecimal("0.90"));
        BigDecimal cpuScore = higherIsWorseScore(rs.getBigDecimal("cpu_usage_pct"), new BigDecimal("85"), new BigDecimal("95"));
        BigDecimal memoryScore = higherIsWorseScore(rs.getBigDecimal("memory_usage_pct"), new BigDecimal("85"), new BigDecimal("95"));
        BigDecimal networkScore = higherIsWorseScore(toBigDecimal(rs.getObject("network_rtt_ms")), new BigDecimal("500"), new BigDecimal("1000"));

        List<BigDecimal> scores = Stream.of(fpsScore, frameDropScore, latencyScore, blurScore, ocrScore, cpuScore, memoryScore, networkScore)
                .filter(score -> score != null)
                .toList();
        if (scores.size() < 4) {
            return null;
        }
        BigDecimal sum = scores.stream().reduce(BigDecimal.ZERO, BigDecimal::add);
        return sum.divide(new BigDecimal(scores.size()), 1, RoundingMode.HALF_UP);
    }

    private HealthStatus resolveHealthStatus(BigDecimal healthScore, String qualityStatus) {
        if (healthScore == null || qualityStatus == null || QualityStatus.INSUFFICIENT.name().equals(qualityStatus)) {
            return HealthStatus.INSUFFICIENT_DATA;
        }
        if (healthScore.compareTo(new BigDecimal("50")) < 0) {
            return HealthStatus.CRITICAL;
        }
        if (healthScore.compareTo(new BigDecimal("80")) < 0) {
            return HealthStatus.DEGRADED;
        }
        return HealthStatus.NORMAL;
    }

    private BigDecimal lowerIsWorseScore(BigDecimal value, BigDecimal critical, BigDecimal warning) {
        if (value == null) {
            return null;
        }
        if (value.compareTo(critical) <= 0) {
            return BigDecimal.ZERO;
        }
        if (value.compareTo(warning) >= 0) {
            return new BigDecimal("100");
        }
        return value.subtract(critical)
                .multiply(new BigDecimal("100"))
                .divide(warning.subtract(critical), 1, RoundingMode.HALF_UP);
    }

    private BigDecimal higherIsWorseScore(BigDecimal value, BigDecimal warning, BigDecimal critical) {
        if (value == null) {
            return null;
        }
        if (value.compareTo(warning) <= 0) {
            return new BigDecimal("100");
        }
        if (value.compareTo(critical) >= 0) {
            return BigDecimal.ZERO;
        }
        return critical.subtract(value)
                .multiply(new BigDecimal("100"))
                .divide(critical.subtract(warning), 1, RoundingMode.HALF_UP);
    }

    private BigDecimal toBigDecimal(Object value) {
        if (value == null) {
            return null;
        }
        return new BigDecimal(value.toString());
    }

    private long countByStatus(List<CameraOperatingStatusResponse> cameras, HealthStatus status) {
        return cameras.stream()
                .filter(camera -> camera.getHealthStatus() == status)
                .count();
    }

    private long countLearningOrInsufficient(List<CameraOperatingStatusResponse> cameras) {
        return cameras.stream()
                .filter(camera -> camera.getHealthStatus() == HealthStatus.BASELINE_LEARNING
                        || camera.getHealthStatus() == HealthStatus.INSUFFICIENT_DATA
                        || camera.getBaselineStatus() == BaselineStatus.LEARNING)
                .count();
    }

    private long countLong(String sql, DataSourceType dataSource) {
        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("dataSource", dataSource.name());
        Long value = jdbcTemplate.queryForObject(sql, params, Long.class);
        return value != null ? value : 0;
    }

    private void validatePage(int page, int size) {
        if (page < 0 || size < 1 || size > 100) {
            throw new BusinessException("Invalid page request.", HttpStatus.BAD_REQUEST);
        }
    }

    private SortSpec parseSort(String sort, List<String> allowedFields) {
        String raw = sort == null || sort.isBlank() ? "cameraName,asc" : sort;
        String[] parts = raw.split(",");
        String field = parts[0].trim();
        String direction = parts.length > 1 ? parts[1].trim().toLowerCase() : "asc";
        if (!allowedFields.contains(field) || (!"asc".equals(direction) && !"desc".equals(direction))) {
            throw new BusinessException("Unsupported sort: " + raw, HttpStatus.BAD_REQUEST);
        }
        return new SortSpec(field, direction);
    }

    private Comparator<CameraOperatingStatusResponse> cameraComparator(SortSpec sortSpec) {
        Comparator<CameraOperatingStatusResponse> comparator = switch (sortSpec.field()) {
            case "healthScore" -> Comparator.comparing(
                    CameraOperatingStatusResponse::getHealthScore,
                    Comparator.nullsLast(BigDecimal::compareTo)
            );
            case "latestSampledAt" -> Comparator.comparing(
                    CameraOperatingStatusResponse::getLatestSampledAt,
                    Comparator.nullsLast(OffsetDateTime::compareTo)
            );
            default -> Comparator.comparing(CameraOperatingStatusResponse::getCameraName, String.CASE_INSENSITIVE_ORDER);
        };
        return "desc".equals(sortSpec.direction()) ? comparator.reversed() : comparator;
    }

    private record SortSpec(String field, String direction) {
    }
}
