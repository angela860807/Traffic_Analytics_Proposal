package com.example.traffic.repository;

import com.example.traffic.domain.DetectionLog;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface DetectionLogRepository extends JpaRepository<DetectionLog, Long> {

    List<DetectionLog> findTop100ByOrderByDetectedAtDesc();

    List<DetectionLog> findByCamera_Zone_ZoneIdOrderByDetectedAtDesc(Long zoneId);
}
