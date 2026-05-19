package com.example.traffic.dto.response;

import com.example.traffic.common.enums.Direction;
import com.example.traffic.common.enums.DetectionLogStatus;
import com.example.traffic.domain.DetectionAnalysisResult;
import com.example.traffic.domain.DetectionLog;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
public class DetectionResponse {
    private final Long logId;
    private final Long flowEventId;
    private final String cameraName;
    private final String zoneName;
    private final Direction directionType;
    private final String imagePath;
    private final String imageUrl;
    private final LocalDateTime detectedAt;

    // 분석 결과 테이블(DetectionAnalysisResult)에서 가져올 필드들
    private final String plateNumber;
    private final String plateCropImageUrl;
    private final String ocrImageUrl;
    private final Double confidenceScore;
    private final DetectionLogStatus status;

    public static DetectionResponse of(DetectionLog log, DetectionAnalysisResult result) {
        return of(log, result, null);
    }

    public static DetectionResponse of(DetectionLog log, DetectionAnalysisResult result, Long flowEventId) {
        return DetectionResponse.builder()
                .logId(log.getLogId())
                .flowEventId(flowEventId)
                .cameraName(log.getCamera().getCameraName())
                .zoneName(log.getCamera().getZone().getZoneName())
                .directionType(log.getCamera().getDirectionType())
                .imagePath(log.getImagePath())
                .imageUrl(log.getImageUrl())
                .detectedAt(log.getDetectedAt())
                // 분석 결과가 있을 경우에만 세팅
                .plateNumber(result != null ? result.getPlateNumber() : null)
                .plateCropImageUrl(result != null ? result.getPlateCropImageUrl() : null)
                .ocrImageUrl(result != null ? result.getOcrImageUrl() : null)
                .confidenceScore(result != null && result.getConfidenceScore() != null ? result.getConfidenceScore().doubleValue() : null)
                .status(result != null ? result.getStatus() : DetectionLogStatus.RECEIVED)
                .build();
    }
}
