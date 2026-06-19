package com.example.traffic.repository;

import com.example.traffic.domain.DetectorVersion;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface DetectorVersionRepository extends JpaRepository<DetectorVersion, Long> {

    Optional<DetectorVersion> findByDetectorNameAndVersion(String detectorName, String version);
}
