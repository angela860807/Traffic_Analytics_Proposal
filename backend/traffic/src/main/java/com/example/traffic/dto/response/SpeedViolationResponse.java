package com.example.traffic.dto.response;

import com.example.traffic.common.enums.ViolationStatus;
import com.example.traffic.domain.SpeedViolation;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
public class SpeedViolationResponse {

    private final Long violationId;
    private final Long flowEventId;
    private final Long vehicleId;
    private final Long cameraId;
    private final String cameraName;
    private final String plateNumber;
    private final Double measuredSpeed;
    private final Double speedLimit;
    private final String violationImagePath;
    private final ViolationStatus violationStatus;
    private final LocalDateTime violatedAt;
    private final LocalDateTime createdAt;

    public static SpeedViolationResponse from(SpeedViolation violation) {
        return SpeedViolationResponse.builder()
                .violationId(violation.getViolationId())
                .flowEventId(violation.getFlowEvent().getFlowEventId())
                .vehicleId(violation.getVehicle().getVehicleId())
                .cameraId(violation.getCamera().getCameraId())
                .cameraName(violation.getCamera().getCameraName())
                .plateNumber(violation.getPlateNumber())
                .measuredSpeed(violation.getMeasuredSpeed().doubleValue())
                .speedLimit(violation.getSpeedLimit().doubleValue())
                .violationImagePath(violation.getViolationImagePath())
                .violationStatus(violation.getViolationStatus())
                .violatedAt(violation.getViolatedAt())
                .createdAt(violation.getCreatedAt())
                .build();
    }
}
