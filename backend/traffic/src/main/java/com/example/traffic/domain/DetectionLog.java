package com.example.traffic.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "detection_logs", indexes = {
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

    @Column(length = 255)
    private String imagePath;

    @Column(length = 500)
    private String imageUrl;

    @Column(nullable = false)
    private LocalDateTime detectedAt;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public DetectionLog(Camera camera, String imagePath, String imageUrl, LocalDateTime detectedAt) {
        this.camera = camera;
        this.imagePath = imagePath;
        this.imageUrl = imageUrl;
        this.detectedAt = (detectedAt != null) ? detectedAt : LocalDateTime.now();
        this.createdAt = LocalDateTime.now();
    }
}
