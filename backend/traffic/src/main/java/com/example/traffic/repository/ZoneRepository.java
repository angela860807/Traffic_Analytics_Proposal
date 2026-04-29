package com.example.traffic.repository;

import com.example.traffic.domain.Zone;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface ZoneRepository extends JpaRepository<Zone, Long> {
    Optional<Zone> findByZoneCode(String zoneCode);
}
