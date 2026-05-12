package com.example.traffic.dto.response;

import com.example.traffic.common.enums.Direction;
import com.example.traffic.domain.VehicleFlowEvent;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
public class FlowEventResponse {
    private final String plateNumber;
    private final String zoneName;
    private final String cameraName;
    private final Direction flowDirection;
    private final LocalDateTime eventAt;
    private final Double speed;
    private final Long stayTime;

    public static FlowEventResponse from(VehicleFlowEvent event) {
        return FlowEventResponse.builder()
                .plateNumber(event.getVehicle().getPlateNumber())
                .zoneName(event.getZone().getZoneName())
                .cameraName(event.getCamera().getCameraName())
                .flowDirection(event.getFlowDirection())
                .eventAt(event.getEventAt())
                .speed(event.getSpeed() != null ? event.getSpeed().doubleValue() : null)
                .stayTime(event.getStayTime())
                .build();
    }
}
