package com.example.traffic.dto.request.predictive;

import com.example.traffic.common.enums.MaintenanceStatus;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class MaintenanceTicketStatusRequest {

    @NotNull
    private MaintenanceStatus toStatus;

    private String note;
}
