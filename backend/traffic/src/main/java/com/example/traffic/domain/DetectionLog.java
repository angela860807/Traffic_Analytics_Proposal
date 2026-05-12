package com.example.traffic.domain;

import com.example.traffic.common.enums.DetectionType;
import com.example.traffic.common.enums.DetectionLogStatus;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "detection_logs", indexes = {
        // 복합 인덱스로 조회 성능 최적화 (차량번호 + 인식시간)
        @Index(name = "idx_plate_detected", columnList = "plate_number, detected_at"),
        @Index(name = "idx_detected_at", columnList = "detected_at"),
        @Index(name = "idx_status", columnList = "status")
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

    @Column(length = 20)
    private String plateNumber;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private DetectionType detectionType;

    @Column(precision = 5, scale = 4)
    private BigDecimal confidenceScore;

    @Column(length = 255)
    private String imagePath;

    @Column(length = 500)
    private String imageUrl;

    @Column(columnDefinition = "TEXT")
    private String plateCropImagePath;

    @Column(columnDefinition = "TEXT")
    private String plateCropImageUrl;

    @Column(columnDefinition = "TEXT")
    private String ocrImagePath;

    @Column(columnDefinition = "TEXT")
    private String ocrImageUrl;

    @Column(nullable = false)
    private LocalDateTime detectedAt;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30, columnDefinition = "varchar(30) default 'RECEIVED'")
    private DetectionLogStatus status;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public DetectionLog(Camera camera, Vehicle vehicle, String plateNumber, DetectionType detectionType,
                        BigDecimal confidenceScore, String imagePath, String imageUrl,
                        String plateCropImagePath, String plateCropImageUrl,
                        String ocrImagePath, String ocrImageUrl,
                        LocalDateTime detectedAt, DetectionLogStatus status) {
        this.camera = camera;
        this.vehicle = vehicle;
        this.plateNumber = plateNumber;
        this.detectionType = detectionType;
        this.confidenceScore = confidenceScore;
        this.imagePath = imagePath;
        this.imageUrl = imageUrl;
        this.plateCropImagePath = plateCropImagePath;
        this.plateCropImageUrl = plateCropImageUrl;
        this.ocrImagePath = ocrImagePath;
        this.ocrImageUrl = ocrImageUrl;
        this.detectedAt = (detectedAt != null) ? detectedAt : LocalDateTime.now();
        this.status = (status != null) ? status : DetectionLogStatus.RECEIVED;
        this.createdAt = LocalDateTime.now();
    }

    public void markFlowEventCreated() {
        this.status = DetectionLogStatus.FLOW_EVENT_CREATED;
    }

    public void markDuplicateSkipped() {
        this.status = DetectionLogStatus.DUPLICATE_SKIPPED;
    }

    public void markOcrFailed() {
        this.status = DetectionLogStatus.OCR_FAILED;
    }
}
