package com.example.traffic.domain;

import com.example.traffic.common.enums.ViolationStatus;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "speed_violations")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class SpeedViolation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "violation_id")
    private Long violationId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "flow_event_id", nullable = false)
    private VehicleFlowEvent flowEvent;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "vehicle_id", nullable = false)
    private Vehicle vehicle;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "camera_id", nullable = false)
    private Camera camera;

    @Column(nullable = false, length = 20)
    private String plateNumber;

    @Column(nullable = false, precision = 5, scale = 2)
    private BigDecimal measuredSpeed;

    @Column(nullable = false, precision = 5, scale = 2)
    private BigDecimal speedLimit;

    @Column(columnDefinition = "TEXT")
    private String violationImagePath;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private ViolationStatus violationStatus;

    @Column(nullable = false)
    private LocalDateTime violatedAt;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public SpeedViolation(VehicleFlowEvent flowEvent, Vehicle vehicle, Camera camera,
                          String plateNumber, BigDecimal measuredSpeed, BigDecimal speedLimit,
                          String violationImagePath, ViolationStatus violationStatus,
                          LocalDateTime violatedAt) {
        this.flowEvent = flowEvent;
        this.vehicle = vehicle;
        this.camera = camera;
        this.plateNumber = plateNumber;
        this.measuredSpeed = measuredSpeed;
        this.speedLimit = speedLimit;
        this.violationImagePath = violationImagePath;
        this.violationStatus = violationStatus != null ? violationStatus : ViolationStatus.UNPROCESSED;
        this.violatedAt = violatedAt != null ? violatedAt : LocalDateTime.now();
        this.createdAt = LocalDateTime.now();
    }

    public void updateStatus(ViolationStatus violationStatus) {
        this.violationStatus = violationStatus;
    }
}
