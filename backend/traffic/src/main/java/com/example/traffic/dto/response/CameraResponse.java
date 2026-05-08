package com.example.traffic.dto.response;

import com.example.traffic.common.enums.Direction;
import com.example.traffic.domain.Camera;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
public class CameraResponse {
    private Long cameraId;
    private Long zoneId;
    private String zoneName; // 화면 편의를 위해 추가[cite: 6]
    private String cameraCode;
    private String cameraName;
    private String streamUrl;
    private Direction directionType;
    private boolean isActive;
    private LocalDateTime createdAt;

    public static CameraResponse from(Camera camera) {
        return CameraResponse.builder()
                .cameraId(camera.getCameraId())
                .zoneId(camera.getZone().getZoneId())
                .zoneName(camera.getZone().getZoneName())
                .cameraCode(camera.getCameraCode())
                .cameraName(camera.getCameraName())
                .streamUrl(camera.getStreamUrl())
                .directionType(camera.getDirectionType())
                .isActive(camera.isActive())
                .createdAt(camera.getCreatedAt())
                .build();
    }
}