package com.example.traffic.dto.request;

import com.example.traffic.common.enums.VehicleStatus;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class VehicleStatusRequest {
    @NotNull(message = "차량 상태값은 필수입니다.")
    private VehicleStatus vehicleStatus; // Enum 사용
}
