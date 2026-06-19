package com.example.traffic.domain;

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
        name = "anomaly_event_evidence",
        indexes = @Index(
                name = "idx_anomaly_event_evidence_event_id",
                columnList = "anomaly_event_id, sampled_at"
        )
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class AnomalyEventEvidence {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "anomaly_event_id", nullable = false)
    private AnomalyEvent anomalyEvent;

    @Column(name = "metric_name", nullable = false, length = 50)
    private String metricName;

    @Column(name = "observed_value", precision = 12, scale = 6)
    private BigDecimal observedValue;

    @Column(name = "baseline_value", precision = 12, scale = 6)
    private BigDecimal baselineValue;

    @Column(name = "threshold_value", precision = 12, scale = 6)
    private BigDecimal thresholdValue;

    @Column(name = "metric_score", precision = 12, scale = 6)
    private BigDecimal metricScore;

    @Column(length = 20)
    private String unit;

    @Column(name = "sampled_at")
    private LocalDateTime sampledAt;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "context_json", nullable = false, columnDefinition = "jsonb")
    private Map<String, Object> contextJson = new HashMap<>();

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public AnomalyEventEvidence(AnomalyEvent anomalyEvent, String metricName,
                                BigDecimal observedValue, BigDecimal baselineValue,
                                BigDecimal thresholdValue, BigDecimal metricScore,
                                String unit, LocalDateTime sampledAt,
                                Map<String, Object> contextJson) {
        this.anomalyEvent = anomalyEvent;
        this.metricName = metricName;
        this.observedValue = observedValue;
        this.baselineValue = baselineValue;
        this.thresholdValue = thresholdValue;
        this.metricScore = metricScore;
        this.unit = unit;
        this.sampledAt = sampledAt;
        this.contextJson = contextJson != null ? new HashMap<>(contextJson) : new HashMap<>();
        this.createdAt = LocalDateTime.now();
    }
}
