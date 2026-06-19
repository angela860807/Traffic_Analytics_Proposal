package com.example.traffic.dto.request.predictive;

import com.example.traffic.common.enums.MaintenancePriority;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class MaintenanceTicketCreateRequest {

    @NotNull
    private Long anomalyEventId;

    @NotNull
    private MaintenancePriority priority;

    private String actionNote;
}
