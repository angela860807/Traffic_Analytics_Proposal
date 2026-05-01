package com.example.traffic.repository;

import com.example.traffic.domain.Camera;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;

public interface CameraRepository extends JpaRepository<Camera, Long> {
    // 카메라 코드로 카메라 찾기[cite: 2]
    Optional<Camera> findByCameraCode(String cameraCode);

    // 특정 구역에 설치된 모든 카메라 조회[cite: 2]
    List<Camera> findByZoneZoneId(Long zoneId);
}