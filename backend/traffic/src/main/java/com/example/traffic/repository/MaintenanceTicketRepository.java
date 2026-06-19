package com.example.traffic.repository;

import com.example.traffic.domain.MaintenanceTicket;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

import java.util.Optional;

public interface MaintenanceTicketRepository extends JpaRepository<MaintenanceTicket, Long>, JpaSpecificationExecutor<MaintenanceTicket> {
    Optional<MaintenanceTicket> findByAnomalyEvent_Id(Long anomalyEventId);
}
