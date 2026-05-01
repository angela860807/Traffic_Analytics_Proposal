package com.example.traffic.repository;

import com.example.traffic.domain.Vehicle;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface VehicleRepository extends JpaRepository<Vehicle, Long> {
    // 번호판 번호로 차량 존재 여부 확인
    Optional<Vehicle> findByPlateNumber(String plateNumber);
}