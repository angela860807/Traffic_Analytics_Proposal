package com.example.traffic.repository;

import com.example.traffic.domain.DetectorVersion;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DetectorVersionRepository extends JpaRepository<DetectorVersion, Long> {
}
