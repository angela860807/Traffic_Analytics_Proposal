package com.example.traffic.dto.response.predictive;

import com.example.traffic.common.enums.MaintenanceStatus;
import lombok.Builder;
import lombok.Getter;

import java.time.OffsetDateTime;

@Getter
@Builder
public class MaintenanceTicketHistoryResponse {
    private final Long id;
    private final MaintenanceStatus fromStatus;
    private final MaintenanceStatus toStatus;
    private final ChangedBy changedBy;
    private final String note;
    private final OffsetDateTime changedAt;

    @Getter
    @Builder
    public static class ChangedBy {
        private final Long memberId;
        private final String name;
    }
}
