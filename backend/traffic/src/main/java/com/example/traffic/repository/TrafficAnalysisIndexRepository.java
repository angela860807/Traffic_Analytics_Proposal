package com.example.traffic.repository;

import com.example.traffic.domain.TrafficAnalysisIndex;
import com.example.traffic.domain.Zone;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface TrafficAnalysisIndexRepository extends JpaRepository<TrafficAnalysisIndex, Long> {
    Optional<TrafficAnalysisIndex> findTopByOrderByIdDesc();
    Optional<TrafficAnalysisIndex> findByZone(Zone zone);
}
