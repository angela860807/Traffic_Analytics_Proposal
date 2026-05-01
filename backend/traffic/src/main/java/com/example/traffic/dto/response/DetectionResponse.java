package com.example.traffic.dto.response;

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
    private final String imagePath;
    private final Double confidenceScore;
    private final LocalDateTime detectedAt;

    public static DetectionResponse from(DetectionLog log) {
        return DetectionResponse.builder()
                .logId(log.getLogId())
                .plateNumber(log.getPlateNumber())
                // 1. 로그가 참조하는 카메라의 이름을 가져옴
                .cameraName(log.getCamera().getCameraName())
                // 2. 로그 -> 카메라 -> 구역 순으로 한 단계 더 타고 들어가야 합니다!
                .zoneName(log.getCamera().getZone().getZoneName())
                .imagePath(log.getImagePath())
                // BigDecimal 타입을 Double로 변환하거나 타입을 맞춰주세요.
                .confidenceScore(log.getConfidenceScore() != null ? log.getConfidenceScore().doubleValue() : null)
                .detectedAt(log.getDetectedAt())
                .build();
    }
}