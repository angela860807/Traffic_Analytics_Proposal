package com.example.traffic.dto.request.predictive;

import com.example.traffic.common.enums.MaintenancePriority;
import com.example.traffic.common.enums.MaintenanceStatus;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class MaintenanceTicketSearchRequest {
    private MaintenancePriority priority;
    private MaintenanceStatus status;
    private Long assigneeId;
    @Min(0)
    private int page = 0;
    @Min(1)
    @Max(100)
    private int size = 20;
    private String sort = "createdAt,desc";
}
