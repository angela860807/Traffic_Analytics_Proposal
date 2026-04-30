package com.example.traffic.domain;

import com.example.traffic.common.enums.DetectionType;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "detection_logs", indexes = {
        @Index(name = "idx_plate_number", columnList = "plate_number"),
        @Index(name = "idx_detected_at", columnList = "detected_at")
})
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class DetectionLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "detection_log_id")
    private Long logId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "camera_id", nullable = false)
    private Camera camera;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "vehicle_id")
    private Vehicle vehicle;

    @Column(nullable = false, length = 20)
    private String plateNumber;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private DetectionType detectionType;

    @Column(precision = 5, scale = 4)
    private BigDecimal confidenceScore;

    @Column(length = 255)
    private String imagePath;

    @Column(nullable = false)
    private LocalDateTime detectedAt;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public DetectionLog(Camera camera, Vehicle vehicle, String plateNumber, DetectionType detectionType,
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
