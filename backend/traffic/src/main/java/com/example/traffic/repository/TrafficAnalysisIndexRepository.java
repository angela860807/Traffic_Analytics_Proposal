package com.example.traffic.repository;

import com.example.traffic.domain.TrafficAnalysisIndex;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface TrafficAnalysisIndexRepository extends JpaRepository<TrafficAnalysisIndex, Long> {
    Optional<TrafficAnalysisIndex> findByZoneZoneId(Long zoneId);
}
