package com.example.traffic.domain;

import com.example.traffic.common.enums.AnomalyType;
import com.example.traffic.common.enums.DetectionMethod;
import com.example.traffic.common.enums.ThresholdDirection;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Entity
@Table(
        name = "anomaly_policies",
        uniqueConstraints = @UniqueConstraint(
                name = "uq_anomaly_policies_policy_code",
                columnNames = "policy_code"
        )
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class AnomalyPolicy {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "policy_code", nullable = false, unique = true, length = 100)
    private String policyCode;

    @Enumerated(EnumType.STRING)
    @Column(name = "anomaly_type", nullable = false, length = 100)
    private AnomalyType anomalyType;

    @Enumerated(EnumType.STRING)
    @Column(name = "detection_method", nullable = false, length = 50)
    private DetectionMethod detectionMethod;

    @Column(name = "warning_threshold", precision = 12, scale = 6)
    private BigDecimal warningThreshold;

    @Column(name = "critical_threshold", precision = 12, scale = 6)
    private BigDecimal criticalThreshold;

    @Enumerated(EnumType.STRING)
    @Column(name = "threshold_direction", nullable = false, length = 20)
    private ThresholdDirection thresholdDirection;

    @Column(name = "warning_consecutive_windows")
    private Integer warningConsecutiveWindows;

    @Column(name = "critical_consecutive_windows")
    private Integer criticalConsecutiveWindows;

    @Column(name = "minimum_sample_count")
    private Integer minimumSampleCount;

    @Column(name = "prediction_horizon_minutes")
    private Integer predictionHorizonMinutes;

    @Column(name = "cooldown_minutes")
    private Integer cooldownMinutes;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "config_json", nullable = false, columnDefinition = "jsonb")
    private Map<String, Object> configJson = new HashMap<>();

    @Column(nullable = false)
    private boolean enabled;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "updated_by")
    private Member updatedBy;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @Builder
    public AnomalyPolicy(String policyCode, AnomalyType anomalyType, DetectionMethod detectionMethod,
                         BigDecimal warningThreshold, BigDecimal criticalThreshold,
                         ThresholdDirection thresholdDirection,
                         Integer warningConsecutiveWindows, Integer criticalConsecutiveWindows,
                         Integer minimumSampleCount,
                         Integer predictionHorizonMinutes, Integer cooldownMinutes,
                         Map<String, Object> configJson, Boolean enabled, Member updatedBy) {
        this.policyCode = policyCode;
        this.anomalyType = anomalyType;
        this.detectionMethod = detectionMethod;
        this.warningThreshold = warningThreshold;
        this.criticalThreshold = criticalThreshold;
        this.thresholdDirection = thresholdDirection != null
                ? thresholdDirection : ThresholdDirection.HIGHER_IS_WORSE;
        this.warningConsecutiveWindows = warningConsecutiveWindows;
        this.criticalConsecutiveWindows = criticalConsecutiveWindows;
        this.minimumSampleCount = minimumSampleCount;
        this.predictionHorizonMinutes = predictionHorizonMinutes;
        this.cooldownMinutes = cooldownMinutes;
        this.configJson = configJson != null ? new HashMap<>(configJson) : new HashMap<>();
        this.enabled = enabled == null || enabled;
        this.updatedBy = updatedBy;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = this.createdAt;
    }
}
