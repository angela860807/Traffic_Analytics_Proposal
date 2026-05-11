package com.example.traffic.repository;

import com.example.traffic.domain.Camera;
import com.example.traffic.domain.DetectionLog;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDateTime;
import java.util.List;

public interface DetectionLogRepository extends JpaRepository<DetectionLog, Long> {

    // 1. [서비스 연동 필수] 중복 인식 방지를 위한 존재 여부 확인
    // 서비스의 request.getDetectedAt().minusSeconds(5) 로직과 연동됩니다.
    boolean existsByCameraAndPlateNumberAndDetectedAtAfter(Camera camera, String plateNumber, LocalDateTime detectedAt);

    // 2. [대시보드용] 최근 탐지 로그 100개 조회
    List<DetectionLog> findTop100ByOrderByDetectedAtDesc();

    // 3. [검색용] 차량 번호판으로 검색
    List<DetectionLog> findByPlateNumberOrderByDetectedAtDesc(String plateNumber);

    // 4. [검색용] 구역 ID로 검색 (객체 그래프 탐색)
    List<DetectionLog> findByCamera_Zone_ZoneIdOrderByDetectedAtDesc(Long zoneId);

    // 5. [재처리/비동기용] 특정 상태(PENDING, FAILED)의 로그만 조회
    List<DetectionLog> findByStatus(String status);
}