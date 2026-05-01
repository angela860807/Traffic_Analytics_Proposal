package com.example.traffic.repository;

import com.example.traffic.domain.DetectionLog;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface DetectionLogRepository extends JpaRepository<DetectionLog, Long> {
    // 최근 탐지 로그 100개 조회 (대시보드용)
    List<DetectionLog> findTop100ByOrderByDetectedAtDesc();

    // 차량 번호판으로 검색 (추가 필요)
    List<DetectionLog> findByPlateNumberOrderByDetectedAtDesc(String plateNumber);

    // 구역 ID로 검색
    List<DetectionLog> findByCamera_Zone_ZoneIdOrderByDetectedAtDesc(Long zoneId);
}