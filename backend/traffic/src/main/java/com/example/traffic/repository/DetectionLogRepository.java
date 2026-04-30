package com.example.traffic.repository;

import com.example.traffic.domain.DetectionLog;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface DetectionLogRepository extends JpaRepository<DetectionLog, Long> {
    // 1. 특정 카메라에서 데이터가 잘 들어오는지 확인용
    List<DetectionLog> findByCameraCameraId(Long cameraId);

    // 2. 특정 번호판이 찍혔는지 확인용 (가장 기초적인 식별 확인)
    List<DetectionLog> findByPlateNumber(String plateNumber);
}
