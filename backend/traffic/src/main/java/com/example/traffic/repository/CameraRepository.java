package com.example.traffic.repository;

import com.example.traffic.domain.Camera;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CameraRepository extends JpaRepository<Camera, Long> {

    List<Camera> findByZoneZoneId(Long zoneId);
}
