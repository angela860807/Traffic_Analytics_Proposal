package com.example.traffic.repository;

import com.example.traffic.domain.MaintenanceTicket;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface MaintenanceTicketRepository extends JpaRepository<MaintenanceTicket, Long> {
    Optional<MaintenanceTicket> findByAnomalyEvent_Id(Long anomalyEventId);
}
