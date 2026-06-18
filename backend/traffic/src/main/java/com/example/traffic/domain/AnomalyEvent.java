package com.example.traffic.domain;

import com.example.traffic.common.enums.*;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(
        name = "anomaly_events",
        indexes = {
                @Index(name = "idx_anomaly_events_camera_status",
                        columnList = "target_camera_id, status"),
                @Index(name = "idx_anomaly_events_status_severity_time",
                        columnList = "status, severity, first_detected_at"),
                @Index(name = "idx_anomaly_events_first_detected",
                        columnList = "first_detected_at")
        }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class AnomalyEvent {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Enumerated(EnumType.STRING)
    @Column(name = "target_type", nullable = false, length = 50)
    private AnomalyTargetType targetType;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "target_camera_id", nullable = false)
    private Camera targetCamera;

    @Enumerated(EnumType.STRING)
    @Column(name = "anomaly_type", nullable = false, length = 100)
    private AnomalyType anomalyType;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 50)
    private AnomalySeverity severity;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 50)
    private AnomalyEventStatus status;

    @Enumerated(EnumType.STRING)
    @Column(name = "detection_method", nullable = false, length = 50)
    private DetectionMethod detectionMethod;

    @Enumerated(EnumType.STRING)
    @Column(name = "data_source", nullable = false, length = 50)
    private DataSourceType dataSource;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "policy_id")
    private AnomalyPolicy policy;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "detector_version_id")
    private DetectorVersion detectorVersion;

    @Column(name = "anomaly_score", precision = 12, scale = 6)
    private BigDecimal anomalyScore;

    @Column(name = "baseline_source", length = 100)
    private String baselineSource;

    @Column(name = "baseline_from")
    private LocalDateTime baselineFrom;

    @Column(name = "baseline_to")
    private LocalDateTime baselineTo;

    @Column(name = "baseline_sample_count")
    private Integer baselineSampleCount;

    @Column(name = "trend_slope", precision = 12, scale = 6)
    private BigDecimal trendSlope;

    @Column(name = "trend_confidence", precision = 7, scale = 6)
    private BigDecimal trendConfidence;

    @Column(name = "prediction_horizon_minutes")
    private Integer predictionHorizonMinutes;

    @Column(name = "projected_threshold_crossing_at")
    private LocalDateTime projectedThresholdCrossingAt;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "suspected_causes_json", nullable = false, columnDefinition = "jsonb")
    private List<Object> suspectedCausesJson = new ArrayList<>();

    @Enumerated(EnumType.STRING)
    @Column(name = "confirmed_cause", length = 100)
    private SuspectedCause confirmedCause;

    @Column(name = "resolution_note", columnDefinition = "TEXT")
    private String resolutionNote;

    @Column(name = "recurrence_count", nullable = false)
    private Integer recurrenceCount;

    @Column(name = "first_detected_at", nullable = false)
    private LocalDateTime firstDetectedAt;

    @Column(name = "last_detected_at", nullable = false)
    private LocalDateTime lastDetectedAt;

    @Column(name = "recovered_at")
    private LocalDateTime recoveredAt;

    @Column(name = "resolved_at")
    private LocalDateTime resolvedAt;

    @Column(name = "acknowledged_at")
    private LocalDateTime acknowledgedAt;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "acknowledged_by")
    private Member acknowledgedBy;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "resolved_by")
    private Member resolvedBy;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @Builder
    public AnomalyEvent(AnomalyTargetType targetType, Camera targetCamera, AnomalyType anomalyType,
                        AnomalySeverity severity, AnomalyEventStatus status, DetectionMethod detectionMethod,
                        DataSourceType dataSource, AnomalyPolicy policy, DetectorVersion detectorVersion,
                        BigDecimal anomalyScore, String baselineSource, LocalDateTime baselineFrom,
                        LocalDateTime baselineTo, Integer baselineSampleCount, BigDecimal trendSlope,
                        BigDecimal trendConfidence, Integer predictionHorizonMinutes,
                        LocalDateTime projectedThresholdCrossingAt, List<Object> suspectedCausesJson,
                        SuspectedCause confirmedCause, String resolutionNote, Integer recurrenceCount,
                        LocalDateTime firstDetectedAt, LocalDateTime lastDetectedAt) {
        this.targetType = targetType != null ? targetType : AnomalyTargetType.CAMERA;
        this.targetCamera = targetCamera;
        this.anomalyType = anomalyType;
        this.severity = severity;
        this.status = status != null ? status : AnomalyEventStatus.OPEN;
        this.detectionMethod = detectionMethod;
        this.dataSource = dataSource != null ? dataSource : DataSourceType.REAL;
        this.policy = policy;
        this.detectorVersion = detectorVersion;
        this.anomalyScore = anomalyScore;
        this.baselineSource = baselineSource;
        this.baselineFrom = baselineFrom;
        this.baselineTo = baselineTo;
        this.baselineSampleCount = baselineSampleCount;
        this.trendSlope = trendSlope;
        this.trendConfidence = trendConfidence;
        this.predictionHorizonMinutes = predictionHorizonMinutes;
        this.projectedThresholdCrossingAt = projectedThresholdCrossingAt;
        this.suspectedCausesJson = suspectedCausesJson != null
                ? new ArrayList<>(suspectedCausesJson) : new ArrayList<>();
        this.confirmedCause = confirmedCause;
        this.resolutionNote = resolutionNote;
        this.recurrenceCount = recurrenceCount != null ? recurrenceCount : 0;
        this.firstDetectedAt = firstDetectedAt;
        this.lastDetectedAt = lastDetectedAt;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = this.createdAt;
    }

    public void refreshDetection(AnomalySeverity newSeverity,
                                 BigDecimal newAnomalyScore,
                                 LocalDateTime detectedAt,
                                 BigDecimal newTrendSlope,
                                 BigDecimal newTrendConfidence,
                                 Integer newPredictionHorizonMinutes,
                                 LocalDateTime newProjectedThresholdCrossingAt,
                                 List<Object> newSuspectedCausesJson) {
        if (AnomalySeverity.CRITICAL.equals(newSeverity)) {
            this.severity = AnomalySeverity.CRITICAL;
        }
        this.anomalyScore = newAnomalyScore;
        this.lastDetectedAt = detectedAt;
        this.trendSlope = newTrendSlope;
        this.trendConfidence = newTrendConfidence;
        this.predictionHorizonMinutes = newPredictionHorizonMinutes;
        this.projectedThresholdCrossingAt = newProjectedThresholdCrossingAt;
        this.suspectedCausesJson = newSuspectedCausesJson != null
                ? new ArrayList<>(newSuspectedCausesJson) : new ArrayList<>();
        if (AnomalyEventStatus.RECOVERED.equals(this.status)) {
            this.status = AnomalyEventStatus.OPEN;
            this.recurrenceCount = this.recurrenceCount == null ? 1 : this.recurrenceCount + 1;
        }
        this.updatedAt = LocalDateTime.now();
    }
}
