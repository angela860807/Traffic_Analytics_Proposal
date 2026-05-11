package com.example.traffic.dto.response;

import com.example.traffic.common.enums.Direction;
import com.example.traffic.domain.VehicleFlowEvent;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
public class FlowEventResponse {
    private final String plateNumber; //[cite: 6]
    private final String zoneName; //[cite: 6]
    private final String cameraName; //[cite: 6]
    private final Direction flowDirection; //[cite: 6]
    private final LocalDateTime eventAt; //[cite: 6]
    private final Double speed;
    private final Long stayTime;

    public static FlowEventResponse from(VehicleFlowEvent event) {
        return FlowEventResponse.builder()
                .plateNumber(event.getVehicle().getPlateNumber()) //[cite: 6]
                .zoneName(event.getZone().getZoneName()) //[cite: 6]
                .cameraName(event.getCamera().getCameraName()) //[cite: 6]
                .flowDirection(event.getFlowDirection()) //[cite: 6]
                .eventAt(event.getEventAt()) //[cite: 6]
                .speed(event.getSpeed() != null ? event.getSpeed().doubleValue() : null)
                .stayTime(event.getStayTime())
                .build();
    }
}
