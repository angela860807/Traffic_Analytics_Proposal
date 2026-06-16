package com.example.traffic.repository;

import com.example.traffic.domain.CameraHealthSample;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CameraHealthSampleRepository extends JpaRepository<CameraHealthSample, Long> {
}
