package com.example.traffic.repository;

import com.example.traffic.common.enums.ViolationStatus;
import com.example.traffic.domain.Camera;
import com.example.traffic.domain.SpeedViolation;
import com.example.traffic.domain.Vehicle;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public interface SpeedViolationRepository extends JpaRepository<SpeedViolation, Long> {

    Optional<SpeedViolation> findByFlowEvent_FlowEventId(Long flowEventId);

    List<SpeedViolation> findByVehicleOrderByViolatedAtDesc(Vehicle vehicle);

    List<SpeedViolation> findByCameraOrderByViolatedAtDesc(Camera camera);

    List<SpeedViolation> findByViolationStatusOrderByViolatedAtDesc(ViolationStatus violationStatus);

    List<SpeedViolation> findByViolatedAtBetweenOrderByViolatedAtDesc(
            LocalDateTime start,
            LocalDateTime end
    );

    long countByViolatedAtBetween(LocalDateTime start, LocalDateTime end);
}
