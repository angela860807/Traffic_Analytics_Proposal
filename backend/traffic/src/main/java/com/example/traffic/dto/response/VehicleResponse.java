package com.example.traffic.dto.response;

import com.example.traffic.common.enums.VehicleStatus;
import com.example.traffic.domain.Vehicle;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
public class VehicleResponse {
    private final Long vehicleId;
    private final String plateNumber;
    private final VehicleStatus vehicleStatus;
    private final LocalDateTime firstDetectedAt;
    private final LocalDateTime lastDetectedAt;
    private final LocalDateTime createdAt;

    public static VehicleResponse from(Vehicle vehicle) {
        return VehicleResponse.builder()
                .vehicleId(vehicle.getVehicleId())
                .plateNumber(vehicle.getPlateNumber())
                .vehicleStatus(vehicle.getVehicleStatus())
                .firstDetectedAt(vehicle.getFirstDetectedAt())
                .lastDetectedAt(vehicle.getLastDetectedAt())
                .createdAt(vehicle.getCreatedAt())
                .build();
    }
}
