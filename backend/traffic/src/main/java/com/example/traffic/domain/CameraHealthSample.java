package com.example.traffic.domain;

import com.example.traffic.common.enums.DataSourceType;
import com.example.traffic.common.enums.QualityStatus;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(
        name = "camera_health_samples",
        uniqueConstraints = {
                @UniqueConstraint(name = "uq_camera_health_samples_camera_sampled",
                        columnNames = {"camera_id", "sampled_at"}),
                @UniqueConstraint(name = "uq_camera_health_samples_idempotency",
                        columnNames = "idempotency_key")
        },
        indexes = {
                @Index(name = "idx_camera_health_samples_camera_sampled",
                        columnList = "camera_id, sampled_at"),
                @Index(name = "idx_camera_health_samples_quality_sampled",
                        columnList = "quality_status, sampled_at"),
                @Index(name = "idx_camera_health_samples_datasource_sampled",
                        columnList = "data_source, sampled_at")
        }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class CameraHealthSample {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "camera_id", nullable = false)
    private Camera camera;

    @Column(name = "processor_code", length = 50)
    private String processorCode;

    @Column(name = "sampled_at", nullable = false)
    private LocalDateTime sampledAt;

    @Column(name = "sample_window_seconds", nullable = false)
    private Integer sampleWindowSeconds;

    @Column(name = "fps_avg", precision = 7, scale = 2)
    private BigDecimal fpsAvg;

    @Column(name = "frame_drop_rate", precision = 7, scale = 6)
    private BigDecimal frameDropRate;

    @Column(name = "latency_p95_ms")
    private Integer latencyP95Ms;

    @Column(name = "blur_score_avg", precision = 7, scale = 6)
    private BigDecimal blurScoreAvg;

    @Column(name = "brightness_score_avg", precision = 7, scale = 6)
    private BigDecimal brightnessScoreAvg;

    @Column(name = "detection_count")
    private Integer detectionCount;

    @Column(name = "ocr_attempt_count")
    private Integer ocrAttemptCount;

    @Column(name = "ocr_failure_count")
    private Integer ocrFailureCount;

    @Column(name = "ocr_fail_rate", precision = 7, scale = 6)
    private BigDecimal ocrFailRate;

    @Column(name = "cpu_usage_pct", precision = 5, scale = 2)
    private BigDecimal cpuUsagePct;

    @Column(name = "memory_usage_pct", precision = 5, scale = 2)
    private BigDecimal memoryUsagePct;

    @Column(name = "disk_usage_pct", precision = 5, scale = 2)
    private BigDecimal diskUsagePct;

    @Column(name = "network_rtt_ms")
    private Integer networkRttMs;

    @Column(name = "last_frame_at")
    private LocalDateTime lastFrameAt;

    @Enumerated(EnumType.STRING)
    @Column(name = "data_source", nullable = false, length = 50)
    private DataSourceType dataSource;

    @Enumerated(EnumType.STRING)
    @Column(name = "quality_status", nullable = false, length = 50)
    private QualityStatus qualityStatus;

    @Column(name = "is_imputed", nullable = false)
    private boolean isImputed;

    @Column(name = "idempotency_key", nullable = false, unique = true, length = 100)
    private String idempotencyKey;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public CameraHealthSample(Camera camera, String processorCode, LocalDateTime sampledAt,
                              Integer sampleWindowSeconds, BigDecimal fpsAvg, BigDecimal frameDropRate,
                              Integer latencyP95Ms, BigDecimal blurScoreAvg, BigDecimal brightnessScoreAvg,
                              Integer detectionCount, Integer ocrAttemptCount, Integer ocrFailureCount,
                              BigDecimal ocrFailRate, BigDecimal cpuUsagePct, BigDecimal memoryUsagePct,
                              BigDecimal diskUsagePct, Integer networkRttMs, LocalDateTime lastFrameAt,
                              DataSourceType dataSource, QualityStatus qualityStatus, boolean isImputed,
                              String idempotencyKey) {
        this.camera = camera;
        this.processorCode = processorCode;
        this.sampledAt = sampledAt;
        this.sampleWindowSeconds = sampleWindowSeconds != null ? sampleWindowSeconds : 60;
        this.fpsAvg = fpsAvg;
        this.frameDropRate = frameDropRate;
        this.latencyP95Ms = latencyP95Ms;
        this.blurScoreAvg = blurScoreAvg;
        this.brightnessScoreAvg = brightnessScoreAvg;
        this.detectionCount = detectionCount;
        this.ocrAttemptCount = ocrAttemptCount;
        this.ocrFailureCount = ocrFailureCount;
        this.ocrFailRate = ocrFailRate;
        this.cpuUsagePct = cpuUsagePct;
        this.memoryUsagePct = memoryUsagePct;
        this.diskUsagePct = diskUsagePct;
        this.networkRttMs = networkRttMs;
        this.lastFrameAt = lastFrameAt;
        this.dataSource = dataSource != null ? dataSource : DataSourceType.REAL;
        this.qualityStatus = qualityStatus != null ? qualityStatus : QualityStatus.COMPLETE;
        this.isImputed = isImputed;
        this.idempotencyKey = idempotencyKey;
        this.createdAt = LocalDateTime.now();
    }
}
