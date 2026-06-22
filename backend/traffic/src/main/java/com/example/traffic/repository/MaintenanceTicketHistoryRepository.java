package com.example.traffic.repository;

import com.example.traffic.domain.MaintenanceTicketHistory;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface MaintenanceTicketHistoryRepository extends JpaRepository<MaintenanceTicketHistory, Long> {
    List<MaintenanceTicketHistory> findByMaintenanceTicket_IdOrderByChangedAtAscIdAsc(Long ticketId);
}
