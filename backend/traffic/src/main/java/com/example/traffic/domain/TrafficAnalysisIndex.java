package com.example.traffic.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "traffic_analysis_index",
        indexes = {
                @Index(name = "idx_traffic_analysis_index_zone", columnList = "zone_id")
        },
        uniqueConstraints = {
                @UniqueConstraint(name = "uk_traffic_analysis_index_zone", columnNames = "zone_id")
        }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class TrafficAnalysisIndex {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "zone_id")
    private Zone zone;

    // Last processed vehicle_flow_events.flow_event_id.
    private Long lastSeq;

    // Last source detection_logs.detection_log_id included in analysis.
    private Long lastLogId;

    // Last analyzed event time.
    private LocalDateTime lastLogTime;

    // Time when this index row was updated.
    private LocalDateTime fetchedTime;

    @Builder
    public TrafficAnalysisIndex(Zone zone, Long lastSeq, Long lastLogId,
                                LocalDateTime lastLogTime,
                                LocalDateTime fetchedTime) {
        this.zone = zone;
        this.lastSeq = lastSeq;
        this.lastLogId = lastLogId;
        this.lastLogTime = lastLogTime;
        this.fetchedTime = fetchedTime != null ? fetchedTime : LocalDateTime.now();
    }

    public void update(Long lastSeq, Long lastLogId, LocalDateTime lastLogTime) {
        this.lastSeq = lastSeq;
        this.lastLogId = lastLogId;
        this.lastLogTime = lastLogTime;
        this.fetchedTime = LocalDateTime.now();
    }
}
