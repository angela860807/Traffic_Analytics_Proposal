package com.example.traffic.repository;

import com.example.traffic.domain.Zone;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface ZoneRepository extends JpaRepository<Zone, Long> {
    // 구역 코드로 구역 찾기 (중복 체크나 분석 시 사용)[cite: 7]
    Optional<Zone> findByZoneCode(String zoneCode);
}