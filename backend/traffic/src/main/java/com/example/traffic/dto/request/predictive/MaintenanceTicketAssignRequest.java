package com.example.traffic.dto.request.predictive;

import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class MaintenanceTicketAssignRequest {

    @NotNull
    private Long assigneeId;

    private String note;
}
