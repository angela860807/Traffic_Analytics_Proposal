package com.example.traffic.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "detection_logs")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class DetectionLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long logId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "camera_id", nullable = false)
    private Camera camera;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "vehicle_id")
    private Vehicle vehicle;

    @Column(nullable = false, length = 20)
    private String plateNumber;

    @Column(nullable = false, length = 20)
    private String detectionType;

    @Column(precision = 5, scale = 4)
    private BigDecimal confidenceScore;

    @Column(length = 255)
    private String imagePath;

    @Column(nullable = false)
    private LocalDateTime detectedAt;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public DetectionLog(Camera camera, Vehicle vehicle, String plateNumber, String detectionType,
                        BigDecimal confidenceScore, String imagePath, LocalDateTime detectedAt) {
        this.camera = camera;
        this.vehicle = vehicle;
        this.plateNumber = plateNumber;
        this.detectionType = detectionType;
        this.confidenceScore = confidenceScore;
        this.imagePath = imagePath;
        this.detectedAt = (detectedAt != null) ? detectedAt : LocalDateTime.now();
        this.createdAt = LocalDateTime.now();
    }
}
