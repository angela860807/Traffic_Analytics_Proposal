package com.example.traffic.domain;

import com.example.traffic.common.enums.Direction;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "vehicle_flow_events")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class VehicleFlowEvent {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "flow_event_id")
    private Long flowEventId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "vehicle_id", nullable = false)
    private Vehicle vehicle;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "camera_id", nullable = false)
    private Camera camera;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "zone_id", nullable = false)
    private Zone zone;

    @Enumerated(EnumType.STRING)
    @Column(name = "flow_direction", nullable = false, length = 20)
    private Direction flowDirection;

    @Column(name = "event_at", nullable = false)
    private LocalDateTime eventAt;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "source_detection_log_id", nullable = false)
    private DetectionLog sourceDetectionLog;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(precision = 5, scale = 2)
    private Double speed;

    @Column
    private Long stayTime;

    @Builder
    public VehicleFlowEvent(Vehicle vehicle, Camera camera, Zone zone, Direction flowDirection,
                            LocalDateTime eventAt, DetectionLog sourceDetectionLog,
                            Double speed, Long stayTime) { // 파라미터 추가
        this.vehicle = vehicle;
        this.camera = camera;
        this.zone = zone;
        this.flowDirection = flowDirection;
        this.eventAt = (eventAt != null) ? eventAt : LocalDateTime.now();
        this.sourceDetectionLog = sourceDetectionLog;
        this.speed = (speed != null) ? speed : 0.0; // 추가
        this.stayTime = (stayTime != null) ? stayTime : 0L; // 추가
        this.createdAt = LocalDateTime.now();
    }
}
