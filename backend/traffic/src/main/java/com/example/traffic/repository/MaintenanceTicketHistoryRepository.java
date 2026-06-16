package com.example.traffic.repository;

import com.example.traffic.domain.MaintenanceTicketHistory;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MaintenanceTicketHistoryRepository extends JpaRepository<MaintenanceTicketHistory, Long> {
}
