package com.example.traffic.domain;

import com.example.traffic.common.enums.MaintenancePriority;
import com.example.traffic.common.enums.MaintenanceStatus;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(
        name = "maintenance_tickets",
        uniqueConstraints = {
                @UniqueConstraint(name = "uq_maintenance_tickets_anomaly_event",
                        columnNames = "anomaly_event_id"),
                @UniqueConstraint(name = "uq_maintenance_tickets_ticket_number",
                        columnNames = "ticket_number")
        },
        indexes = {
                @Index(name = "idx_maintenance_tickets_status_priority",
                        columnList = "status, priority")
        }
)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class MaintenanceTicket {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "anomaly_event_id", nullable = false, unique = true)
    private AnomalyEvent anomalyEvent;

    @Column(name = "ticket_number", nullable = false, unique = true, length = 30)
    private String ticketNumber;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 10)
    private MaintenancePriority priority;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 50)
    private MaintenanceStatus status;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "assignee_id")
    private Member assignee;

    @Column(name = "due_ack_at")
    private LocalDateTime dueAckAt;

    @Column(name = "due_start_at")
    private LocalDateTime dueStartAt;

    @Column(name = "acknowledged_at")
    private LocalDateTime acknowledgedAt;

    @Column(name = "started_at")
    private LocalDateTime startedAt;

    @Column(name = "resolved_at")
    private LocalDateTime resolvedAt;

    @Column(name = "closed_at")
    private LocalDateTime closedAt;

    @Column(name = "action_note", columnDefinition = "TEXT")
    private String actionNote;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "created_by")
    private Member createdBy;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @Builder
    public MaintenanceTicket(AnomalyEvent anomalyEvent, String ticketNumber,
                             MaintenancePriority priority, MaintenanceStatus status,
                             Member assignee, LocalDateTime dueAckAt, LocalDateTime dueStartAt,
                             String actionNote, Member createdBy) {
        this.anomalyEvent = anomalyEvent;
        this.ticketNumber = ticketNumber;
        this.priority = priority;
        this.status = status != null ? status : MaintenanceStatus.OPEN;
        this.assignee = assignee;
        this.dueAckAt = dueAckAt;
        this.dueStartAt = dueStartAt;
        this.actionNote = actionNote;
        this.createdBy = createdBy;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = this.createdAt;
    }
}
