package com.example.traffic.dto.response;

import com.example.traffic.common.enums.Direction;
import com.example.traffic.common.enums.DetectionLogStatus;
import com.example.traffic.domain.DetectionLog;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
public class DetectionResponse {
    private final Long logId;
    private final String plateNumber;
    private final String cameraName;
    private final String zoneName;
    private final Direction directionType;
    private final String imagePath;
    private final String imageUrl;
    private final String plateCropImageUrl;
    private final String ocrImageUrl;
    private final Double confidenceScore;
    private final LocalDateTime detectedAt;
    private final DetectionLogStatus status;

    public static DetectionResponse from(DetectionLog log) {
        return DetectionResponse.builder()
                .logId(log.getLogId())
                .plateNumber(log.getPlateNumber())
                .cameraName(log.getCamera().getCameraName())
                .zoneName(log.getCamera().getZone().getZoneName())
                .directionType(log.getCamera().getDirectionType())
                .imagePath(log.getImagePath())
                .imageUrl(log.getImageUrl())
                .plateCropImageUrl(log.getPlateCropImageUrl())
                .ocrImageUrl(log.getOcrImageUrl())
                .confidenceScore(log.getConfidenceScore() != null ? log.getConfidenceScore().doubleValue() : null)
                .detectedAt(log.getDetectedAt())
                .status(log.getStatus())
                .build();
    }
}
