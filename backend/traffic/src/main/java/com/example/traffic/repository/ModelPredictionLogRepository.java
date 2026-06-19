package com.example.traffic.repository;

import com.example.traffic.domain.ModelPredictionLog;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDateTime;

public interface ModelPredictionLogRepository extends JpaRepository<ModelPredictionLog, Long> {

    boolean existsByCamera_CameraIdAndDetectorVersion_IdAndEvaluatedAt(
            Long cameraId,
            Long detectorVersionId,
            LocalDateTime evaluatedAt
    );
}
