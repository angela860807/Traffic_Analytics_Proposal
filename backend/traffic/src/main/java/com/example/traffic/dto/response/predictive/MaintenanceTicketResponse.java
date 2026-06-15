package com.example.traffic.dto.response.predictive;

import com.example.traffic.common.enums.MaintenancePriority;
import com.example.traffic.common.enums.MaintenanceStatus;
import lombok.Builder;
import lombok.Getter;

import java.time.OffsetDateTime;

@Getter
@Builder
public class MaintenanceTicketResponse {
    private final Long id;
    private final String ticketNumber;
    private final Long anomalyEventId;
    private final Long cameraId;
    private final MaintenancePriority priority;
    private final MaintenanceStatus status;
    private final Assignee assignee;
    private final OffsetDateTime dueAckAt;
    private final OffsetDateTime dueStartAt;
    private final boolean ackOverdue;
    private final boolean startOverdue;
    private final OffsetDateTime createdAt;

    @Getter
    @Builder
    public static class Assignee {
        private final Long memberId;
        private final String name;
    }
}
