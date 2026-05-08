package com.example.traffic.repository;

import com.example.traffic.domain.Vehicle;
import com.example.traffic.domain.VehicleFlowEvent;
import com.example.traffic.domain.Zone;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;

public interface VehicleFlowEventRepository extends JpaRepository<VehicleFlowEvent, Long> {
    // 특정 차량의 통과 이력 조회
    @Query("select vfe from VehicleFlowEvent vfe " +
            "join fetch vfe.vehicle " +
            "join fetch vfe.zone " +
            "join fetch vfe.camera " +
            "where vfe.vehicle.vehicleId = :vehicleId " +
            "order by vfe.eventAt desc")
    List<VehicleFlowEvent> findByVehicleIdWithDetails(@Param("vehicleId") Long vehicleId);

    // VehicleFlowEventRepository.java 에 추가
    boolean existsByVehicleAndZoneAndEventAtAfter(Vehicle vehicle, Zone zone, LocalDateTime dateTime);

    // 특정 구역, 특정 방향(IN/OUT), 특정 시간대의 데이터 개수를 집계
    long countByZoneAndFlowDirectionAndEventAtBetween(
            com.example.traffic.domain.Zone zone,
            com.example.traffic.common.enums.Direction flowDirection,
            LocalDateTime start,
            LocalDateTime end);
}