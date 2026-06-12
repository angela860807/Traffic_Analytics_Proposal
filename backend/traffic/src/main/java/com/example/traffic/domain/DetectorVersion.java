package com.example.traffic.domain;

import com.example.traffic.common.enums.DetectionMethod;
import com.example.traffic.common.enums.DetectorOperatingMode;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Entity
@Table(
        name = "detector_versions",
        uniqueConstraints = @UniqueConstraint(
                name = "uq_detector_versions_name_version",
                columnNames = {"detector_name", "version"}
        )
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class DetectorVersion {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "detector_name", nullable = false, length = 100)
    private String detectorName;

    @Column(nullable = false, length = 20)
    private String version;

    @Enumerated(EnumType.STRING)
    @Column(name = "detection_method", nullable = false, length = 50)
    private DetectionMethod detectionMethod;

    @Column(name = "model_format", length = 20)
    private String modelFormat;

    @Column(name = "artifact_path", length = 500)
    private String artifactPath;

    @Column(name = "artifact_sha256", length = 64)
    private String artifactSha256;

    @Column(name = "feature_schema_version", length = 20)
    private String featureSchemaVersion;

    @Column(name = "dataset_version", length = 50)
    private String datasetVersion;

    @Column(name = "config_hash", length = 64)
    private String configHash;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "metrics_json", nullable = false, columnDefinition = "jsonb")
    private Map<String, Object> metricsJson = new HashMap<>();

    @Enumerated(EnumType.STRING)
    @Column(name = "operating_mode", nullable = false, length = 20)
    private DetectorOperatingMode operatingMode;

    @Column(nullable = false)
    private boolean active;

    @Column(name = "trained_at")
    private LocalDateTime trainedAt;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public DetectorVersion(String detectorName, String version, DetectionMethod detectionMethod,
                           String modelFormat, String artifactPath, String artifactSha256,
                           String featureSchemaVersion, String datasetVersion,
                           String configHash, Map<String, Object> metricsJson,
                           DetectorOperatingMode operatingMode, boolean active,
                           LocalDateTime trainedAt) {
        this.detectorName = detectorName;
        this.version = version;
        this.detectionMethod = detectionMethod;
        this.modelFormat = modelFormat;
        this.artifactPath = artifactPath;
        this.artifactSha256 = artifactSha256;
        this.featureSchemaVersion = featureSchemaVersion;
        this.datasetVersion = datasetVersion;
        this.configHash = configHash;
        this.metricsJson = metricsJson != null ? new HashMap<>(metricsJson) : new HashMap<>();
        this.operatingMode = operatingMode != null
                ? operatingMode : DetectorOperatingMode.SHADOW;
        this.active = active;
        this.trainedAt = trainedAt;
        this.createdAt = LocalDateTime.now();
    }
}
