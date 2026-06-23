package com.example.traffic.domain;

import com.example.traffic.common.enums.AnomalySeverity;
import com.example.traffic.common.enums.DataSourceType;
import com.example.traffic.common.enums.QualityStatus;
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
        name = "model_prediction_logs",
        uniqueConstraints = @UniqueConstraint(
                name = "uq_model_prediction_logs_camera_detector_evaluated",
                columnNames = {"camera_id", "detector_version_id", "evaluated_at"}
        ),
        indexes = {
                @Index(name = "idx_model_prediction_logs_camera_evaluated",
                        columnList = "camera_id, evaluated_at"),
                @Index(name = "idx_model_prediction_logs_detector_evaluated",
                        columnList = "detector_version_id, evaluated_at"),
                @Index(name = "idx_model_prediction_logs_predicted_anomaly",
                        columnList = "predicted_anomaly, evaluated_at")
        }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ModelPredictionLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "camera_id", nullable = false)
    private Camera camera;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "detector_version_id", nullable = false)
    private DetectorVersion detectorVersion;

    @Column(name = "evaluated_at", nullable = false)
    private LocalDateTime evaluatedAt;

    @Column(name = "input_window_from", nullable = false)
    private LocalDateTime inputWindowFrom;

    @Column(name = "input_window_to", nullable = false)
    private LocalDateTime inputWindowTo;

    @Column(name = "anomaly_score", precision = 7, scale = 6)
    private BigDecimal anomalyScore;

    @Column(name = "warning_threshold", precision = 7, scale = 6)
    private BigDecimal warningThreshold;

    @Column(name = "critical_threshold", precision = 7, scale = 6)
    private BigDecimal criticalThreshold;

    @Column(name = "predicted_anomaly", nullable = false)
    private boolean predictedAnomaly;

    @Enumerated(EnumType.STRING)
    @Column(name = "predicted_severity", length = 20)
    private AnomalySeverity predictedSeverity;

    @Enumerated(EnumType.STRING)
    @Column(name = "quality_status", nullable = false, length = 50)
    private QualityStatus qualityStatus;

    @Column(name = "feature_schema_version", length = 100)
    private String featureSchemaVersion;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "top_features_json", nullable = false, columnDefinition = "jsonb")
    private List<Object> topFeaturesJson = new ArrayList<>();

    @Enumerated(EnumType.STRING)
    @Column(name = "data_source", nullable = false, length = 50)
    private DataSourceType dataSource;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public ModelPredictionLog(Camera camera, DetectorVersion detectorVersion,
                              LocalDateTime evaluatedAt, LocalDateTime inputWindowFrom,
                              LocalDateTime inputWindowTo,
                              BigDecimal anomalyScore, BigDecimal warningThreshold,
                              BigDecimal criticalThreshold, boolean predictedAnomaly,
                              AnomalySeverity predictedSeverity, QualityStatus qualityStatus,
                              String featureSchemaVersion, List<Object> topFeaturesJson,
                              DataSourceType dataSource) {
        this.camera = camera;
        this.detectorVersion = detectorVersion;
        this.evaluatedAt = evaluatedAt;
        this.inputWindowFrom = inputWindowFrom;
        this.inputWindowTo = inputWindowTo;
        this.anomalyScore = anomalyScore;
        this.warningThreshold = warningThreshold;
        this.criticalThreshold = criticalThreshold;
        this.predictedAnomaly = predictedAnomaly;
        this.predictedSeverity = predictedAnomaly ? predictedSeverity : null;
        this.qualityStatus = qualityStatus != null ? qualityStatus : QualityStatus.COMPLETE;
        this.featureSchemaVersion = featureSchemaVersion;
        this.topFeaturesJson = topFeaturesJson != null ? new ArrayList<>(topFeaturesJson) : new ArrayList<>();
        this.dataSource = dataSource != null ? dataSource : DataSourceType.REAL;
        this.createdAt = LocalDateTime.now();
    }
}
