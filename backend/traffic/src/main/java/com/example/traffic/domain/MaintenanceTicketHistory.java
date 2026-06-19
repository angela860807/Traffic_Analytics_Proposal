package com.example.traffic.domain;

import com.example.traffic.common.enums.MaintenanceStatus;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "maintenance_ticket_histories",
        indexes = @Index(
                name = "idx_maintenance_ticket_histories_ticket_id",
                columnList = "maintenance_ticket_id, changed_at"
        )
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class MaintenanceTicketHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "maintenance_ticket_id", nullable = false)
    private MaintenanceTicket maintenanceTicket;

    @Enumerated(EnumType.STRING)
    @Column(name = "from_status", length = 50)
    private MaintenanceStatus fromStatus;

    @Enumerated(EnumType.STRING)
    @Column(name = "to_status", nullable = false, length = 50)
    private MaintenanceStatus toStatus;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "changed_by")
    private Member changedBy;

    @Column(columnDefinition = "TEXT")
    private String note;

    @Column(name = "changed_at", nullable = false)
    private LocalDateTime changedAt;

    @Builder
    public MaintenanceTicketHistory(MaintenanceTicket maintenanceTicket,
                                    MaintenanceStatus fromStatus,
                                    MaintenanceStatus toStatus,
                                    Member changedBy, String note,
                                    LocalDateTime changedAt) {
        this.maintenanceTicket = maintenanceTicket;
        this.fromStatus = fromStatus;
        this.toStatus = toStatus;
        this.changedBy = changedBy;
        this.note = note;
        this.changedAt = changedAt != null ? changedAt : LocalDateTime.now();
    }
}
