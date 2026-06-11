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
        name = "traffic_context_samples",
        uniqueConstraints = {
                @UniqueConstraint(name = "uq_traffic_context_camera_zone_sampled",
                        columnNames = {"camera_id", "zone_id", "sampled_at"}),
                @UniqueConstraint(name = "uq_traffic_context_idempotency",
                        columnNames = "idempotency_key")
        },
        indexes = {
                @Index(name = "idx_traffic_context_samples_camera_sampled",
                        columnList = "camera_id, sampled_at"),
                @Index(name = "idx_traffic_context_samples_zone_sampled",
                        columnList = "zone_id, sampled_at"),
                @Index(name = "idx_traffic_context_samples_datasource_sampled",
                        columnList = "data_source, sampled_at")
        }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class TrafficContextSample {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "camera_id", nullable = false)
    private Camera camera;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "zone_id", nullable = false)
    private Zone zone;

    @Column(name = "sampled_at", nullable = false)
    private LocalDateTime sampledAt;

    @Column(name = "window_minutes", nullable = false)
    private Integer windowMinutes;

    @Column(name = "vehicle_count")
    private Integer vehicleCount;

    @Column(name = "avg_speed_kmh", precision = 7, scale = 2)
    private BigDecimal avgSpeedKmh;

    @Column(name = "speed_measurement_count")
    private Integer speedMeasurementCount;

    @Column(name = "speed_violation_count")
    private Integer speedViolationCount;

    @Column(name = "ocr_attempt_count")
    private Integer ocrAttemptCount;

    @Column(name = "ocr_success_count")
    private Integer ocrSuccessCount;

    @Column(name = "ocr_failure_count")
    private Integer ocrFailureCount;

    @Column(name = "in_count")
    private Integer inCount;

    @Column(name = "out_count")
    private Integer outCount;

    @Enumerated(EnumType.STRING)
    @Column(name = "data_source", nullable = false, length = 50)
    private DataSourceType dataSource;

    @Enumerated(EnumType.STRING)
    @Column(name = "quality_status", nullable = false, length = 50)
    private QualityStatus qualityStatus;

    @Column(name = "is_imputed", nullable = false)
    private boolean isImputed;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "source_from_flow_event_id")
    private VehicleFlowEvent sourceFromFlowEvent;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "source_to_flow_event_id")
    private VehicleFlowEvent sourceToFlowEvent;

    @Column(name = "idempotency_key", nullable = false, unique = true, length = 100)
    private String idempotencyKey;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @Builder
    public TrafficContextSample(Camera camera, Zone zone, LocalDateTime sampledAt, Integer windowMinutes,
                                Integer vehicleCount, BigDecimal avgSpeedKmh, Integer speedMeasurementCount,
                                Integer speedViolationCount, Integer ocrAttemptCount, Integer ocrSuccessCount,
                                Integer ocrFailureCount, Integer inCount, Integer outCount,
                                DataSourceType dataSource, QualityStatus qualityStatus, boolean isImputed,
                                VehicleFlowEvent sourceFromFlowEvent, VehicleFlowEvent sourceToFlowEvent,
                                String idempotencyKey) {
        this.camera = camera;
        this.zone = zone;
        this.sampledAt = sampledAt;
        this.windowMinutes = windowMinutes != null ? windowMinutes : 5;
        this.vehicleCount = vehicleCount;
        this.avgSpeedKmh = avgSpeedKmh;
        this.speedMeasurementCount = speedMeasurementCount;
        this.speedViolationCount = speedViolationCount;
        this.ocrAttemptCount = ocrAttemptCount;
        this.ocrSuccessCount = ocrSuccessCount;
        this.ocrFailureCount = ocrFailureCount;
        this.inCount = inCount;
        this.outCount = outCount;
        this.dataSource = dataSource != null ? dataSource : DataSourceType.REAL;
        this.qualityStatus = qualityStatus != null ? qualityStatus : QualityStatus.COMPLETE;
        this.isImputed = isImputed;
        this.sourceFromFlowEvent = sourceFromFlowEvent;
        this.sourceToFlowEvent = sourceToFlowEvent;
        this.idempotencyKey = idempotencyKey;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = this.createdAt;
    }
}
