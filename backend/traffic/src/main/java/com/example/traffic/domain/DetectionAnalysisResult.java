package com.example.traffic.domain;

import com.example.traffic.common.enums.DetectionLogStatus;
import com.example.traffic.common.enums.DetectionType;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "detection_analysis_results", indexes = {
        @Index(name = "idx_analysis_results_log_id", columnList = "detection_log_id"),
        @Index(name = "idx_analysis_results_status_created", columnList = "status, created_at"),
        @Index(name = "idx_analysis_results_plate_created", columnList = "plate_number, created_at")
})

@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class DetectionAnalysisResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "analysis_result_id")
    private Long resultId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "detection_log_id", nullable = false)
    private DetectionLog detectionLog; // 원본 로그 참조

    @Column(nullable = false)
    private Integer attemptNo; // 처리 회차 (1차, 2차 등)

    @Column(length = 30, nullable = false)
    private String processorType; // 처리 주체 (FASTAPI_OCR 등)

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30)
    private DetectionLogStatus status; // 처리 상태

    @Column(length = 20)
    private String plateNumber; // 차량 번호

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private DetectionType detectionType; // 탐지 타입 (PLATE, VEHICLE 등)

    @Column(precision = 5, scale = 4)
    private BigDecimal confidenceScore; // 신뢰도 점수

    @Column(columnDefinition = "TEXT")
    private String plateCropImagePath;

    @Column(columnDefinition = "TEXT")
    private String plateCropImageUrl;

    @Column(columnDefinition = "TEXT")
    private String ocrImagePath;

    @Column(columnDefinition = "TEXT")
    private String ocrImageUrl;

    @Column(nullable = false)
    private LocalDateTime processedAt; // 처리 완료 시각

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public DetectionAnalysisResult(DetectionLog detectionLog, Integer attemptNo, String processorType,
                                   DetectionLogStatus status, String plateNumber, DetectionType detectionType,
                                   BigDecimal confidenceScore, String plateCropImagePath, String plateCropImageUrl,
                                   String ocrImagePath, String ocrImageUrl, LocalDateTime processedAt) {
        this.detectionLog = detectionLog;
        this.attemptNo = (attemptNo != null) ? attemptNo : 1;
        this.processorType = (processorType != null) ? processorType : "FASTAPI_OCR";
        this.status = status;
        this.plateNumber = plateNumber;
        this.detectionType = detectionType;
        this.confidenceScore = confidenceScore;
        this.plateCropImagePath = plateCropImagePath;
        this.plateCropImageUrl = plateCropImageUrl;
        this.ocrImagePath = ocrImagePath;
        this.ocrImageUrl = ocrImageUrl;
        this.processedAt = (processedAt != null) ? processedAt : LocalDateTime.now();
        this.createdAt = LocalDateTime.now();
    }
}
