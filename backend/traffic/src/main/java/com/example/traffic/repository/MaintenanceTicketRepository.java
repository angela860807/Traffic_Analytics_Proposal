package com.example.traffic.repository;

import com.example.traffic.domain.MaintenanceTicket;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MaintenanceTicketRepository extends JpaRepository<MaintenanceTicket, Long> {
}
