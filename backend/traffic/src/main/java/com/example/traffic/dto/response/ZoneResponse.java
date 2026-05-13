package com.example.traffic.dto.response;

import com.example.traffic.common.enums.ZoneType;
import com.example.traffic.domain.Zone;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class ZoneResponse {

    private final Long zoneId;
    private final String zoneCode;
    private final String zoneName;
    private final ZoneType zoneType;
    private final boolean isActive;
    private final LocalDateTime createdAt;

    @Builder
    public ZoneResponse(Long zoneId, String zoneCode, String zoneName,
                        ZoneType zoneType, boolean isActive, LocalDateTime createdAt) {
        this.zoneId = zoneId;
        this.zoneCode = zoneCode;
        this.zoneName = zoneName;
        this.zoneType = zoneType;
        this.isActive = isActive;
        this.createdAt = createdAt;
    }

    // 엔티티를 DTO로 변환하는 정적 팩토리 메서드
    public static ZoneResponse from(Zone zone) {
        return ZoneResponse.builder()
                .zoneId(zone.getZoneId())
                .zoneCode(zone.getZoneCode())
                .zoneName(zone.getZoneName())
                .zoneType(zone.getZoneType())
                .isActive(zone.isActive())
                .createdAt(zone.getCreatedAt())
                .build();
    }
}