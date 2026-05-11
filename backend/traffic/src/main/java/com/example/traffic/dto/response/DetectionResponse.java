package com.example.traffic.dto.response;

import com.example.traffic.common.enums.Direction;
import com.example.traffic.domain.DetectionLog;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
public class DetectionResponse {
    private final Long logId;
    private final String plateNumber;
    private final String cameraName; // 화면 표시용
    private final String zoneName;   // 화면 표시용
    private final Direction directionType;
    private final String imagePath;
    private final String preprocessedPath;
    private final String imageUrl;
    private final String status;
    private final Double confidenceScore;
    private final LocalDateTime detectedAt;

    public static DetectionResponse from(DetectionLog log) {
        return DetectionResponse.builder()
                .logId(log.getLogId())
                .plateNumber(log.getPlateNumber())
                .cameraName(log.getCamera().getCameraName())
                .zoneName(log.getCamera().getZone().getZoneName())
                .directionType(log.getCamera().getDirectionType())
                .imagePath(log.getImagePath())
                .preprocessedPath(log.getPreprocessedPath())
                .imageUrl(log.getImageUrl()) // ★ 엔티티 값을 응답 DTO에 매핑
                .status(log.getStatus())
                .confidenceScore(log.getConfidenceScore() != null ? log.getConfidenceScore().doubleValue() : null)
                .detectedAt(log.getDetectedAt())
                .build();
    }
}
